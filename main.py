import pandas as pd

from io import StringIO
from datetime import timedelta

from portfolio_construction import OptimisationPortfolioConstructionModel
from execution import Execution
from charting import InitCharts, PlotPerformanceChart, PlotExposureChart, PlotCountryExposureChart


def normalise(series, equal_ls=True):
    if equal_ls:
        series -= series.mean()
    sum = series.abs().sum()
    return series.apply(lambda x: x / sum)


class StockifySentiment(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2017, 1, 1)  # Set Start Date
        self.SetEndDate(2020, 5, 20)
        self.SetCash(100000)  # Set Strategy Cash
        self.data, self.etf_list, self.etf_country = self.DataSetup()

        # Add ETFs
        for etf in self.etf_list:
            self.AddEquity(etf, Resolution.Minute)

        # Weighting style - normalise or alpha maximisation w/ optimisation
        self.weighting_style = 'normalise'

        # Market neutral
        self.mkt_neutral = True

        # Portfolio construction model
        self.CustomPortfolioConstructionModel = OptimisationPortfolioConstructionModel(turnover=1, max_wt=0.2,
                                                                                       longshort=True,
                                                                                       mkt_neutral=self.mkt_neutral)

        # Execution model
        self.CustomExecution = Execution(liq_tol=0.005)

        # Schedule rebalancing
        self.Schedule.On(self.DateRules.Every(DayOfWeek.Wednesday), self.TimeRules.BeforeMarketClose('IVV', 210),
                         Action(self.RebalancePortfolio))

        # Init charting
        InitCharts(self)

        # Schedule charting
        self.Schedule.On(self.DateRules.Every(DayOfWeek.Wednesday), self.TimeRules.BeforeMarketClose('IVV', 5),
                         Action(self.PlotCharts))

    def OnData(self, data):
        pass

    def RebalancePortfolio(self):
        if self.weighting_style == 'normalise':
            portfolio = normalise(
                self.data.loc[self.Time - timedelta(7):self.Time].reset_index().set_index('symbol')['alpha_score'],
                equal_ls=self.mkt_neutral)
        elif self.weighting_style == 'alpha_max':
            df = self.data.loc[self.Time - timedelta(7):self.Time].reset_index().set_index('symbol')[['alpha_score']]
            portfolio = self.CustomPortfolioConstructionModel.GenerateOptimalPortfolio(self, df)
        else:
            raise Exception('Invalid weighting style')
        self.CustomExecution.ExecutePortfolio(self, portfolio)

    def PlotCharts(self):
        PlotPerformanceChart(self)
        PlotExposureChart(self)
        PlotCountryExposureChart(self)

    def DataSetup(self):
        df = pd.read_csv(StringIO(
            self.Download('https://raw.githubusercontent.com/Ollie-Hooper/StockifySentiment/master/data/scores.csv')))
        data = df[['date', 'country', 's_valence']].copy()
        data['date'] = pd.to_datetime(data['date'])
        data.rename(columns={'s_valence': 'alpha_score'}, inplace=True)
        etf_df = pd.read_csv(StringIO(
            self.Download('https://raw.githubusercontent.com/Ollie-Hooper/StockifySentiment/master/data/etf.csv')))
        data = pd.merge(data, etf_df)
        data = data.sort_values('date')
        data.set_index(['date', 'symbol'], inplace=True)
        data = data[['alpha_score']]
        return data, etf_df['symbol'].to_list(), etf_df.set_index('symbol')['country_name'].to_dict()