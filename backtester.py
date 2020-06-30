import os
from os import path
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import time
import pyfiglet
import openpyxl
import sqlite3
from datetime import datetime
from datetime import date
from math import ceil
import pandas as pd
import requests
from bs4 import BeautifulSoup
import math
import collections
import xlrd
import xlsxwriter
import glob





class Spreadsheet():
    def __init__(self, path):
        self.sheets = []
        pd.set_option('display.max_rows', None)

        xl = pd.ExcelFile(path)
        # print(f"{path} could not converted to Spreadsheet object.")
        

        dfs = {sheet: xl.parse(sheet) for sheet in xl.sheet_names}


























class Backtest():
    def __init__(self, path):
        self.spreadsheets = []

        isDirectory = os.path.isdir(path)

        if isDirectory == False:
            raise Exception("Directory not found. Please make sure path is leading to a folder, and not to the file itself.")


        allFiles = os.listdir(path)
        if '.DS_Store' in allFiles:
            allFiles.remove('.DS_Store')

        if len(allFiles) == 0:
            raise Exception("Directory Found, but no files are in directory.")


        spreadsheetFileNames = []
        for eachFile in glob.glob(f"{path}/*.xlsx"):
            spreadsheetFileNames.append(eachFile)

        if len(spreadsheetFileNames) == 0:
            raise Exception("Files in directory are not in an XLSX format.")

        print(spreadsheetFileNames)

        for eachSpreadsheet in spreadsheetFileNames:
            spreadsheetObject = Spreadsheet(eachSpreadsheet)

































def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = f"{dir_path}/Imports"

    backtest = Backtest(path)
    





if __name__ == "__main__":
    main()