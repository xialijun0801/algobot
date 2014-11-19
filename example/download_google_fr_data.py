"""
Please run this code from the algobot root dir.
"""
import pandas as pd
from algobot.databot.Google.FRDownloader import FRBatchDownloader

univ = pd.read_csv('data/2014/11/IWV_20141114.csv')
univ.Exchange[univ.Exchange == 'New York Stock Exchange Inc.'] = 'NYSE'

tickerList = {r[1].Ticker : r[1].Exchange for r in univ.iterrows()}

# Set up the downloader, 
downloader = FRBatchDownloader()
downloader.addTickers(tickerList)

downloader.download(blink=0)

res = downloader.fetchResult()
res.to_csv("fr_data.csv", index=True)
