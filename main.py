from alpha_model import SpotifySentimentAlphaModel
from portfolio_construction import OptimisationPortfolioConstructionModel
from execution import Execution


class StockifySentiment(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2017, 1, 1)  # Set Start Date
        self.SetCash(100000)  # Set Strategy Cash
        self.data, self.etf_list = self.DataSetup()

        # Add ETFs
        for etf in self.etf_list:
            self.AddEquity(etf, Resolution.Minute)

        # Alpha model
        self.CustomAlphaModel = SpotifySentimentAlphaModel()

        # Portfolio construction model
        self.CustomPortfolioConstructionModel = OptimisationPortfolioConstructionModel(turnover=0.05, max_wt=0.05,
                                                                                       longshort=True)

        # Execution model
        self.CustomExecution = Execution(liq_tol=0.005)

        # Schedule rebalancing
        self.Schedule.On(self.DateRules.Every(DayOfWeek.Wednesday), self.TimeRules.BeforeMarketClose('IVV', 0),
                         Action(self.RebalancePortfolio))

    def OnData(self, data):
        pass

    def RebalancePortfolio(self):
        alpha_df = self.CustomAlphaModel.GenerateAlphaScores(self, self.data)
        portfolio = self.CustomPortolioConstructionModel.GenerateOptimalPortfolio(self, alpha_df)
        self.CustomExecution.ExecutePortfolio(self, portfolio)

    def DataSetup(self):
        df = pd.read_csv(StringIO(self.Download('')))
        etf_df = pd.read_csv(StringIO(self.Download('')))
        etf_list = etf_df['etf'].to_list()
        data = df
        return data, etf_list