from iexfinance.stocks import get_historical_data
import pandas as pd
from managers import loadJSON
from buildData import printMessage

def getData(ticker, start, end, what='close'):
    data = get_historical_data(ticker, start, end, output_format='pandas')
    data = data[what]
    data.name = ticker
    return data

def writeStocks(tickers, start, end, fileType, what='close'):
    printMessage('Writing Stocks')
    for i, tick in enumerate(tickers):
        df = pd.DataFrame(getData(tick, start, end, what))
        if fileType == 'pickle':
            df.to_pickle('data/pickle/{}.pickle'.format(tick))
        elif fileType == 'json':
            df.to_json('data/json/{}.json'.format(tick), orient='index')
        print(i+1, '/', len(tickers))

def loadStocks(tickers, fileType, start, end):
    #===========================================================================
    # ADD SOMETHING TO CHECK THAT STOCKS CONTAIN DATES
    #===========================================================================
    if isinstance(tickers, str):
        if fileType == 'json':
            return pd.read_json('data/{}/{}.{}'.format(fileType, tickers, fileType), orient='index')
        elif fileType == 'pickle':
            data = pd.read_pickle('data/{}/{}.{}'.format(fileType, tickers, fileType))
            data = data.loc[start:end]
            return data
    else:
        printMessage('Loading Stocks')
        stockData = pd.DataFrame()
        for tick in tickers:
            data = loadStocks(tick, fileType, start=start, end=end)
            stockData[tick] = data[tick]
        stockData = stockData.loc[start:end]
        return stockData