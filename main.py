class StockifySentiment(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2017, 1, 1)  # Set Start Date
        self.SetCash(100000)  # Set Strategy Cash
        self.data = pd.DataFrame()
        self.etf_list = []

        # Add ETFs
        for etf in self.etf_list:
            self.AddEquity(etf, Resolution.Minute)

        # Alpha model
        self.CustomAlphaModel = ValueAlphaModel()

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
