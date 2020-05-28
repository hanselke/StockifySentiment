def InitCharts(algorithm):
    performance_plot = Chart('Performance Breakdown')
    performance_plot.AddSeries(Series('Total Fees', SeriesType.Line, 0))
    performance_plot.AddSeries(Series('Total Gross Profit', SeriesType.Line, 0))
    algorithm.AddChart(performance_plot)

    exposure_plot = Chart('Exposure/Leverage')
    exposure_plot.AddSeries(Series('Gross', SeriesType.Line, 0))
    exposure_plot.AddSeries(Series('Net', SeriesType.Line, 0))
    algorithm.AddChart(exposure_plot)

    country_exposure_plot = Chart('Country Exposure')
    for etf, country in algorithm.etf_country.items():
        country_exposure_plot.AddSeries(Series(country, SeriesType.Line, 0))


def PlotPerformanceChart(algorithm):
    algorithm.Plot('Performance Breakdown', 'Total Fees', algorithm.Portfolio.TotalFees)
    algorithm.Plot('Performance Breakdown', 'Total Gross Profit', algorithm.Portfolio.TotalProfit)


def PlotExposureChart(algorithm):
    long_val = 0
    short_val = 0
    for security, v in algorithm.Portfolio.items():
        if v.Invested:
            val = v.AbsoluteHoldingsValue
            if v.IsLong:
                long_val += val
            elif v.IsShort:
                short_val += val

    total_equity = algorithm.Portfolio.TotalPortfolioValue
    gross = (long_val + short_val) / total_equity
    net = (long_val - short_val) / total_equity
    algorithm.Plot('Exposure/Leverage', 'Gross', gross)
    algorithm.Plot('Exposure/Leverage', 'Net', net)


def PlotCountryExposureChart(algorithm):
    for etf, country in algorithm.etf_country.items():
        exposure = algorithm.Securities[etf].Holdings.HoldingsValue / algorithm.Portfolio.TotalHoldingsValue
        algorithm.Plot('Country Exposure', country, exposure)