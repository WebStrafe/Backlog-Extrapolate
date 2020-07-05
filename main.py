from backtester import Backtest
from extrapolate import Monthly_Profit
from extrapolate import Calculate_Drawdowns
from extrapolate import Highest_Drawdown
from extrapolate import Count_Periods_Drawdown
from extrapolate import Filter_Drawdowns
from extrapolate import Longest_Drawdown_Period
from extrapolate import Average_Drawdown_Period
from extrapolate import Max_Consecutive_Losses
import os
from os import path








def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = f"{dir_path}/Imports"

    backtest = Backtest(path)

    for eachSpreadsheet in backtest.spreadsheets:
        for eachSheet in eachSpreadsheet.sheets:
            monthlyProfits = Monthly_Profit(eachSheet.trades, eachSheet.fakeTrade)
            for eachMonth in monthlyProfits:
                print(eachMonth[-1])


            drawdowns = Calculate_Drawdowns(eachSheet.trades)

            highestDrawdown = Highest_Drawdown(drawdowns, no_filter=True)
            print(highestDrawdown.percentageChange)

            drawdownsOverFifteenPercent = Filter_Drawdowns(drawdowns)

            periodsOverFifteenPercent = Count_Periods_Drawdown(drawdownsOverFifteenPercent, no_filter=True)
            print(periodsOverFifteenPercent)

            longestPeriodForFifteenPercent = Longest_Drawdown_Period(drawdowns, moreThan=-1000, lessThan=-15.00)
            print(longestPeriodForFifteenPercent.daysInDrawdown)
            longestPeriodForAll = Longest_Drawdown_Period(drawdowns)
            print(longestPeriodForAll.daysInDrawdown)

            averageDrawdownPeriodForFifteen = Average_Drawdown_Period(drawdowns)
            print(averageDrawdownPeriodForFifteen)

            Max_Consecutive_Losses(eachSheet.trades)











if __name__ == "__main__":
    main()