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
            
            if trades[y].balance >= trades[x].balance:
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


    print("\n\nHere are drawdowns under -15%:\n")
    for eachDrawdown in lowestDrawdownsNoDuplicateRecoveries:
        if eachDrawdown.percentageChange <= -15.00:
            print(f"{eachDrawdown.peakTrade.date} - {eachDrawdown.lowTrade.date} - {eachDrawdown.recoveryTrade.date}  ==  {eachDrawdown.percentageChange}%   |   Days in Drawdown: {eachDrawdown.daysInDrawdown}")
            print(f"{eachDrawdown.peakTrade.balance} - {eachDrawdown.lowTrade.balance} - {eachDrawdown.recoveryTrade.balance}")
            print("\n\n")
    

    return lowestDrawdownsNoDuplicateRecoveries






def Highest_Drawdown(drawdowns, percentage=-15.00, no_filter=False):
    highestDrawdownPercent = 0
    highestDrawdown = None

    if no_filter == False:
        for eachDrawdown in drawdowns:
            if eachDrawdown.percentageChange > percentage and eachDrawdown.percentageChange <= highestDrawdownPercent:
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






































def Monthly_Profit(trades, fakeTrade):
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










        
            

        



        
        


        