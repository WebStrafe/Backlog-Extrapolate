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

















