import os
from os import path
import time
import openpyxl
import datetime
from dateutil import relativedelta
from datetime import date
import pandas as pd
import requests
import math
import collections
import xlrd
import xlsxwriter
import glob
import calendar






class Drawdown():
    def __init__(self, peakTrade, lowTrade, recoveryTrade):
        self.peakTrade = peakTrade
        self.lowTrade = lowTrade
        self.recoveryTrade = recoveryTrade
        self.percentageChange = round(((self.lowTrade.balance - self.peakTrade.balance) / self.peakTrade.balance) * 100, 2)
        self.daysInDrawdown = (self.recoveryTrade.date - self.peakTrade.date).days
        # self.percentage = percentage
        # self.daysInDrawdown = daysInDrawdown




def Calculate_Drawdowns(trades):
    drawdowns = []


    for x in range(0, len(trades)): # This gets the lowest low for each peak (can be duplicate lows.) and also finds the recovery. Once the recovery is found, it checks to see if lowestLow is same as Peak, and if it is, break and do not add to drawdowns list. There will be NO 'Non-Recoveries'.
        lowestLow = trades[x]
        recovery = None
        for y in range(x+1, len(trades)):
            if trades[y].balance < lowestLow.balance:
                lowestLow = trades[y]
            
            if trades[y].balance >= trades[x].balance: # ONLY IF RECOVERY IS FOUND, it will add.
                recovery = trades[y]
                
                if trades[x].balance == lowestLow.balance:
                    break
                else:
                    drawdown = Drawdown(trades[x], lowestLow, recovery)
                    drawdowns.append(drawdown)
                    break
        
    

    duplicateLowsAndRecoveryTrades = {} # If the Recovery Date AND Low Date is the SAME, then it will add to this dict.

    for eachDrawdown in drawdowns:
        lowDate = eachDrawdown.lowTrade.date
        recoveryDate = eachDrawdown.recoveryTrade.date
        lowRecoveryDate = f"{lowDate} | {recoveryDate}"
        if lowRecoveryDate in duplicateLowsAndRecoveryTrades:
            duplicateLowsAndRecoveryTrades[lowRecoveryDate].append(eachDrawdown)
        else:
            duplicateLowsAndRecoveryTrades[lowRecoveryDate] = []
            duplicateLowsAndRecoveryTrades[lowRecoveryDate].append(eachDrawdown)


    lowestDrawdowns = []
    for eachKey in duplicateLowsAndRecoveryTrades: # This will then find the lowestDrawdowns for each KEY (recoveryDate and lowDate), so only the lowest possible percentage is found.
        lowestPercentageChange = 0.01
        lowestDrawdown = None
        for eachDrawdown in duplicateLowsAndRecoveryTrades[eachKey]:
            
            if eachDrawdown.percentageChange <= lowestPercentageChange:
                lowestDrawdown = eachDrawdown
                lowestPercentageChange = eachDrawdown.percentageChange
    
        lowestDrawdowns.append(lowestDrawdown)
    
    
    duplicateRecoveryTrades = {} # This searches JUST for duplicate recovery trades and fills this dict

    for eachDrawdown in lowestDrawdowns:
        if eachDrawdown.recoveryTrade.date in duplicateRecoveryTrades:
            duplicateRecoveryTrades[eachDrawdown.recoveryTrade.date].append(eachDrawdown)
        else:
            duplicateRecoveryTrades[eachDrawdown.recoveryTrade.date] = []
            duplicateRecoveryTrades[eachDrawdown.recoveryTrade.date].append(eachDrawdown)
    

    lowestDrawdownsNoDuplicateRecoveries = [] # This then finds the lowest of ALL THESE ONES now, filtering it even further to where there shouldn't be ANY overlap whatsoever.
    for eachRecoveryDate in duplicateRecoveryTrades:
        lowestPercentageChange = 0.01
        lowestDrawdown = None
        for eachDrawdown in duplicateRecoveryTrades[eachRecoveryDate]:
            if eachDrawdown.percentageChange <= lowestPercentageChange:
                lowestPercentageChange = eachDrawdown.percentageChange
                lowestDrawdown = eachDrawdown

        lowestDrawdownsNoDuplicateRecoveries.append(lowestDrawdown)
    


    previousDates = []
    finalDrawdowns = []


    for x in range(0, len(lowestDrawdownsNoDuplicateRecoveries)): # Removes ALL Drawdowns containing any recovery dates that fall below *any* PREVIOUS recovery date.
        if x == 0:
            previousDates.append(lowestDrawdownsNoDuplicateRecoveries[x].recoveryTrade.date)
            finalDrawdowns.append(lowestDrawdownsNoDuplicateRecoveries[x])
            continue

        for y in range(0, len(previousDates)):
            if lowestDrawdownsNoDuplicateRecoveries[x].recoveryTrade.date > previousDates[y]:
                if y == len(previousDates) - 1:
                    finalDrawdowns.append(lowestDrawdownsNoDuplicateRecoveries[x])
                    previousDates.append(lowestDrawdownsNoDuplicateRecoveries[x].recoveryTrade.date)
            else:
                break



    print("\n\n")

    for eachDrawdown in finalDrawdowns:
        if eachDrawdown.percentageChange <= -15.00:
            print(f"{eachDrawdown.peakTrade.date} - {eachDrawdown.lowTrade.date} - {eachDrawdown.recoveryTrade.date}  ==  {eachDrawdown.percentageChange}%   |   Days in Drawdown: {eachDrawdown.daysInDrawdown}")
            print(f"{eachDrawdown.peakTrade.balance} - {eachDrawdown.lowTrade.balance} - {eachDrawdown.recoveryTrade.balance}")
            print("\n\n")
        



    
    

    return finalDrawdowns






def Highest_Drawdown(drawdowns, moreThan=-14.99, lessThan=0, no_filter=False):
    highestDrawdownPercent = 0
    highestDrawdown = None

    if no_filter == False:
        for eachDrawdown in drawdowns:
            if eachDrawdown.percentageChange <= lessThan and eachDrawdown.percentageChange >= moreThan and eachDrawdown.percentageChange <= highestDrawdownPercent:
                highestDrawdownPercent = eachDrawdown.percentageChange
                highestDrawdown = eachDrawdown
    else:
        for eachDrawdown in drawdowns:
            if eachDrawdown.percentageChange <= highestDrawdownPercent:
                highestDrawdownPercent = eachDrawdown.percentageChange
                highestDrawdown = eachDrawdown
        

    return highestDrawdown








def Count_Periods_Drawdown(drawdowns, percentage=-15.00, no_filter=False):
    totalPeriods = 0

    if no_filter == False:
        for eachDrawdown in drawdowns:
            if eachDrawdown.percentageChange <= percentage:
                totalPeriods += 1
    else:
        totalPeriods = len(drawdowns)


    return totalPeriods





def Filter_Drawdowns(drawdowns, percentage=-15.00):
    filteredDrawdowns = []

    for eachDrawdown in drawdowns:
        if eachDrawdown.percentageChange <= percentage:
            filteredDrawdowns.append(eachDrawdown)
    
    return filteredDrawdowns




def Longest_Drawdown_Period(drawdowns, moreThan=-15.00, lessThan=0.00, no_filter=False):

    longestPeriod = 0
    longestDrawdown = None

    if no_filter == False:
        for eachDrawdown in drawdowns:
            if eachDrawdown.percentageChange <= lessThan and eachDrawdown.percentageChange >= moreThan:
                if eachDrawdown.daysInDrawdown > longestPeriod:
                    longestPeriod = eachDrawdown.daysInDrawdown
                    longestDrawdown = eachDrawdown
    else:
        for eachDrawdown in drawdowns:
            if eachDrawdown.daysInDrawdown > longestPeriod:
                longestPeriod = eachDrawdown.daysInDrawdown
                longestDrawdown = eachDrawdown
    
    return longestDrawdown





def Average_Drawdown_Period(drawdowns, moreThan=-10000, lessThan=-15.00, no_filter=False):

    drawdownPeriodsToSum = []

    if no_filter == False:
        for eachDrawdown in drawdowns:
            if eachDrawdown.percentageChange <= lessThan and eachDrawdown.percentageChange >= moreThan:
                drawdownPeriodsToSum.append(eachDrawdown.daysInDrawdown)
    else:
        for eachDrawdown in drawdowns:
            drawdownPeriodsToSum.append(eachDrawdown.daysInDrawdown)
    

    try:
        avgDrawdownPeriod = round((sum(drawdownPeriodsToSum) / len(drawdownPeriodsToSum)))
    except ZeroDivisionError:
        avgDrawdownPeriod = "N/A"
    
    return avgDrawdownPeriod



































def Monthly_Profit(allTrades, fakeTrade):
    from backtester import Trade



    def month_filler(trade, toTrade): # This recursively keeps creating Trade objects with a month AHEAD of the previous until toTrade.date is the same as newDate. This returns the list of Trade Objects with same price and date for MISSING MONTHS! 
        newTrades = []
        newDate = trade.date + relativedelta.relativedelta(months=1)
        if (newDate.month == toTrade.date.month) and (newDate.year == toTrade.date.year):
            return newTrades
        else:
            newTrade = Trade("NONE", [trade.balance, newDate], fake=True)
            newTrades.append(newTrade)
            newTrades += month_filler(newTrade, toTrade)

        return newTrades



    trades = allTrades[:]
    
    trades.insert(0, fakeTrade) # Fake Trade is inserted so Percentage Change can be calculated from the Inital Balance ($1000 for example)
    monthToMonthTrades = []
    currentMonth = fakeTrade.monthDigit

    for eachTrade in range(0, len(trades)): # Retrieves all Months to Months including Fake Starting Month. Does NOT include adding MISSING MONTHS.
        if trades[eachTrade].monthDigit != currentMonth: # Every time the Month Digit changes, the LAST date(as a trade object) gets added to the monthToMonthTrades list, since it's the (last) end of the month.
            currentMonth = trades[eachTrade].monthDigit
            monthToMonthTrades.append(trades[eachTrade - 1])
        
        if eachTrade == len(trades) - 1:
            monthToMonthTrades.append(trades[eachTrade])
    

    addedTrades = {}
    for tradeIndex in range(0, len(monthToMonthTrades)): # Finds the MISSING Months, but does NOT add to list YET.
        if tradeIndex != len(monthToMonthTrades) - 1:
            fakeTrades = month_filler(monthToMonthTrades[tradeIndex], monthToMonthTrades[tradeIndex + 1])
            if len(fakeTrades) == 0:
                continue
            addedTrades[tradeIndex + 1] = fakeTrades
    
    for eachInsertionIndex in addedTrades: # This INSERTS the Missing Months (as trade objects) to the list. Percentage Change NOT YET Calculated.
        monthToMonthTrades[eachInsertionIndex:eachInsertionIndex] = addedTrades[eachInsertionIndex]


    monthlyProfits = []
    for tradeIndex in range(0, len(monthToMonthTrades)): # Percentage Change is calulated here.
        if tradeIndex != len(monthToMonthTrades) - 1:
            currentTrade = monthToMonthTrades[tradeIndex]
            nextTrade = monthToMonthTrades[tradeIndex + 1]

            monthlyProfitCompounded = round(((nextTrade.balance - currentTrade.balance) / currentTrade.balance) * 100, 2)

            monthlyProfitString = f"{nextTrade.month} {nextTrade.year}  ==  {monthlyProfitCompounded}%   (${currentTrade.balance} TO ${nextTrade.balance})"

            monthlyProfit = [nextTrade.month, nextTrade.year, currentTrade.balance, nextTrade.balance, monthlyProfitCompounded, monthlyProfitString]
            monthlyProfits.append(monthlyProfit)
    


    return monthlyProfits # This contains the following: [ theMonth, theYear, theOldBalance, theNewBalance, thePercentageChange, theStringUsedInTextFile ]






def Average_Monthly_Profit(monthlyProfits):

    percentages = []

    for eachMonth in monthlyProfits:
        percentages.append(eachMonth[4])
    

    return round(sum(percentages) / len(percentages), 2)
















        
            

        


def Max_Consecutive_Losses(trades):
    maxConsecutiveLosses = 0

    currentMax = 0
    for eachTrade in trades:
        if eachTrade.profitLossPercent < 0:
            currentMax += 1
        else:
            currentMax = 0


        if currentMax > maxConsecutiveLosses:
                maxConsecutiveLosses = currentMax
    

    return maxConsecutiveLosses








def Average_Win(trades):
    wins = []

    for eachTrade in trades:
        if eachTrade.profitLossPercent >= 0:
            wins.append(eachTrade.profitLossPercent)
    

    return round(sum(wins) / len(wins), 2)




def Highest_Win(trades):
    highestWin = 0

    for eachTrade in trades:
        if eachTrade.profitLossPercent >= 0 and eachTrade.profitLossPercent > highestWin:
            highestWin = eachTrade.profitLossPercent
    

    return round(highestWin, 2)




def Average_Loss(trades):
    losses = []

    for eachTrade in trades:
        if eachTrade.profitLossPercent < 0:
            losses.append(eachTrade.profitLossPercent)
    

    return round(sum(losses) / len(losses), 2)



def Total_Trades(trades):
    return len(trades)




def Total_Wins(trades):
    totalWins = 0
    for eachTrade in trades:
        if eachTrade.profitLossPercent >= 0:
            totalWins += 1
    

    return totalWins




def Total_Losses(trades):
    totalLosses = 0
    for eachTrade in trades:
        if eachTrade.profitLossPercent < 0:
            totalLosses += 1
    
    return totalLosses




def Win_Rate(trades):
    totalWins = 0
    for eachTrade in trades:
        if eachTrade.profitLossPercent >= 0:
            totalWins += 1
    

    return round((totalWins / len(trades)) * 100, 2)






def Total_Backtest_Days(trades):
    firstDate = trades[0].entry.date
    lastDate = trades[len(trades) - 1].exit.date

    days = (lastDate - firstDate).days

    return days



def Total_Backtest_Months(trades):
    firstDate = trades[0].entry.date
    lastDate = trades[len(trades) - 1].exit.date

    days = (lastDate - firstDate).days

    months = round((days / 30.417), 2)

    return months


def Total_Backtest_Years(trades):
    firstDate = trades[0].entry.date
    lastDate = trades[len(trades) - 1].exit.date

    days = (lastDate - firstDate).days

    years = round((days / 365), 2)

    return years




def Total_Backtest_Period(trades, days=False, months=False, years=False):


    firstDate = trades[0].entry.date
    lastDate = trades[len(trades) - 1].exit.date

    

    daysCount = (lastDate - firstDate).days

    if days == True:
        return daysCount
    
    if months == True:
        return round((daysCount / 30.417), 2)
    
    if years == True:
        return round((daysCount / 365), 2)
    
    else:
        return None


















            


        


        