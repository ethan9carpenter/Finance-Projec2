from datetime import datetime as dt
from os.path import exists
from buildData.manageStockData import loadTickers, writeStocks, loadStocks
from buildData.manageResults import loadResults, saveProgress
from buildData.monitors import printMessage
from buildData.manageFiles import deleteFile, loadJSON
from time import time as currentTime
import pandas as pd
#from analysis.analysis import sortedDF

#Add overwrite prompt to make sure you don't overwrite
#make a function to backup the data

def getCorrelations(data, otherData, maxShift, minShift=0, shiftFactor=1, neg=True):
    correlations = []
    data = data.shift(minShift-1)
    
    for _ in range(1+maxShift-minShift):
        #===========================================================================
        # Costly: shift and corr
        #===========================================================================
        data = data.shift(shiftFactor)
        corr = data.corr(otherData)
        if not neg and corr < 0:
            corr = -corr
        correlations.append(corr)
    return correlations


def _removeCompleted(fp, tickers):        
    results = loadResults(fp)
    numComplete = 0
    for tick in results:
        if tick in tickers:
            numComplete += 1
            tickers.remove(tick)
    return numComplete


def _calculateAllCorr(numComplete, against, totalToAnalyze, stocks, fp, maxShift, minShift, shiftFactor):
    printMessage('Calculating Correlations')
    for i, tick in enumerate(stocks.columns):
        start = currentTime()
        tickResults = pd.DataFrame()
        tickData = stocks[tick].shift(minShift)
        
        for day in range(minShift, maxShift+1):
            tickData = tickData.shift(shiftFactor)
            tickResults[day] = against.corrwith(tickData)
        print(i+1+numComplete, 'out of', totalToAnalyze, currentTime()-start)
        
        saveProgress(fp, tickResults, tick)

def performAnalysis(stocks, fp, start, end, maxShift, loadDataType, minShift=1, shiftFactor=1, overwrite=False, against=None):
    if overwrite:
        deleteFile(fp)
    if against is None:
        against = stocks
        
    totalToAnalyze = len(stocks)
    allStocks = list(set(stocks) | set(against))
    _validateSymbols(allStocks, start, end, 'close', fileType=loadDataType)
    numComplete = _removeCompleted(fp, stocks)
    allStocks = loadStocks(allStocks, loadDataType, False)
    stocks = allStocks[list(stocks)]
    against = allStocks[list(against)]
    del allStocks
    
    _calculateAllCorr(numComplete, against, totalToAnalyze, stocks, fp, maxShift, minShift, shiftFactor)
    
def _validateSymbols(symbols, start, end, what, fileType):
    invalid = []
    
    for tick in symbols:
        if not exists('data/{}/{}.{}'.format(fileType, tick, fileType)):
            invalid.append(tick) 
    writeStocks(invalid, start, end, what, fileType)
    
def formatFP(start, end, tickList, againstTL, minShift, maxShift, saveType):
    baseFormat = 'results/{}_{}__{}_{}__{}_{}__{}_{}.{}' 
    fp = baseFormat.format(start.date(), end.date(), len(tickList), tickList, len(againstTL), againstTL, 
                           minShift, maxShift, saveType)
    return fp
    
def _initAnalysis(which, against, start, end, minShift, maxShift, saveType):
    if against is None:
        against = which
    tickList = loadTickers(which)
    againstTL = loadTickers(against)
    fp = formatFP(start, end, tickList, againstTL, minShift, maxShift, saveType)
    printMessage('Init Info')
    print('Start Time:', dt.now(), '\nTotal Tickers:', len(tickList), '\nFile:', fp)
    
    return tickList, againstTL, fp

if __name__ == '__main__':
    start = dt(2014, 1, 1)
    end  = dt(2018, 12, 20)
    which = 'fangs'
    against = ['vz']
    minShift = 1
    maxShift = 1
    saveType = 'json'
    loadDataType = 'pickle'
    overwrite = True
    
    tickers, againstTL, fp = _initAnalysis(which, against, start, end, minShift, maxShift, saveType)
    

    performAnalysis(stocks=tickers, against=againstTL, start=start, end=end, minShift=minShift, 
                    maxShift=maxShift, fp=fp, loadDataType=loadDataType, overwrite=overwrite)
    from pprint import pprint
    pprint(loadJSON(fp))
    