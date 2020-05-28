import pandas as pd

from io import StringIO
from datetime import timedelta

from alpha_model import SpotifySentimentAlphaModel
from portfolio_construction import OptimisationPortfolioConstructionModel
from execution import Execution


class StockifySentiment(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2017, 1, 1)  # Set Start Date
        self.SetEndDate(2020, 5, 20)
        self.SetCash(100000)  # Set Strategy Cash
        self.data, self.etf_list = self.DataSetup()

        # Add ETFs
        for etf in self.etf_list:
            self.AddEquity(etf, Resolution.Minute)

        # Portfolio construction model
        self.CustomPortfolioConstructionModel = OptimisationPortfolioConstructionModel(turnover=0.01, max_wt=0.05,
                                                                                       longshort=True)

        # Execution model
        self.CustomExecution = Execution(liq_tol=0.005)

        # Schedule rebalancing
        self.Schedule.On(self.DateRules.Every(DayOfWeek.Wednesday), self.TimeRules.BeforeMarketClose('IVV', 210),
                         Action(self.RebalancePortfolio))

    def OnData(self, data):
        pass

    def RebalancePortfolio(self):
        date = self.data.loc[self.Time - timedelta(7):self.Time].index.levels[0][0]
        portfolio = self.CustomPortfolioConstructionModel.GenerateOptimalPortfolio(self, self.data.loc[date])
        self.CustomExecution.ExecutePortfolio(self, portfolio)

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
        return data, etf_df['symbol'].to_list()
