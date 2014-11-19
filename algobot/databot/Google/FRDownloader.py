"""
algobot::databot::Google
================================================

API to download data from Google finance:

http://www.google.com/finance

Author: Yue Zhao (yzhao0527'at'gmail'dot'com)
Last Modified: 2014-11-15
"""
from urllib import request
from bs4 import BeautifulSoup
import itertools
import numpy as np
import pandas as pd

from ..downloader import StockDownloader, BatchDownloader
from . import fr_codes


class FRDownloader(StockDownloader):
    """
    Financial Report Data Dowload
    """

    URL = r'https://www.google.com/finance?q={}&fstype=ii'
    Exchanges = set(['NYSE', 'NASDAQ'])
    
    formIds     = ['inc{}div', 'bal{}div', 'cas{}div']
    frequencies = ['interim', 'annual']


    def __init__(self, ticker=None, exchange=None):
        StockDownloader.__init__(self, ticker, self.convertExchange(exchange))

    
    def convertExchange(self, exchange):
        if exchange in self.Exchanges:
            return exchange
        return None
    
    
    def download(self):
        """
        download the entire HTML file from Google finance
        """
        assert isinstance(self.ticker, str)
        assert len(self.ticker) > 0
        exchange = self.convertExchange(self.exchange)
        if exchange is None:
            url = self.URL.format(self.ticker)
        else:
            url = self.URL.format(r"{}:{}".format(exchange, self.ticker))
        
        # load data from web
        try:
            response = request.urlopen(url)
            html = response.read()
        except:
            print("Warning: download failed for {}".format(self.ticker))
        else:
            self.__parseResult(html)
            

    def __parseResult(self, html):
        """
        """
        soup = BeautifulSoup(html)

        data = {}
        for fid, freq in itertools.product(self.formIds, self.frequencies):
            # Iterate throught 3 forms and 2 frequencies
            formId  = fid.format(freq)
            frame   = soup.find(id=formId)
            if frame is None: return
            fsTable = frame.find(id="fs-table")
            if fsTable is None: return
            rows    = fsTable.findAll("tr")
    
            header  = [x.text.strip() for x in rows[0].findAll("th")][1:]
            index   = []
            content = []
            for rr in rows[1:]:
                cols  = rr.findAll("td")
                index.append(cols[0].text.strip())
                items = [x.text.strip().replace(",","") for x in cols[1:]]
                content.append(items)
            
            # convert rowname to code
            z = [fr_codes.name_dict[inx] 
            if inx in fr_codes.name_dict 
            else np.NaN for inx in index]
            codes = [b for a, b in z]
            
            m = np.array(content)
            m[m == '-'] = "NaN"
            m.astype(np.float64)
            data[formId] = pd.DataFrame(m, columns=header, index=codes, dtype=np.float64)

        self.data = data
        self.done = True



class FRBatchDownloader(BatchDownloader):
    """
    """

    def __init__(self):
        print("@TODO: rewrite this part, add exchange data")
        BatchDownloader.__init__(self, FRDownloader)
    
    
    def fetchResult(self):
        """
        Make the FR Table
        -----------------
        N-by-M
        
        N: number of stocks
        M: number of fields
        """
        allData = []
        tickers = []
        for ticker, v in self.downloaders.items():
            
            if not v.done: continue
            
            formIds     = FRDownloader.formIds
            frequencies = FRDownloader.frequencies

            dta = []
            for fid, freq in itertools.product(formIds, frequencies):
                formId = fid.format(freq)
                for i in range(v.data[formId].shape[1]):
                    z = v.data[formId].iloc[:,i]
                    if freq == 'annual':                        
                        inx = z.index.map(lambda n : "{}A{}_{}".format(fid[0].upper(), i, n))
                    else:
                        inx = z.index.map(lambda n : "{}Q{}_{}".format(fid[0].upper(), i, n))
                    dta.append(pd.Series(np.array(z), index=inx))

            series = pd.concat(dta)
            allData.append(pd.Series(np.array(series), index=[np.repeat(ticker, len(series)),
                                                              series.index.tolist()]))

        # make the table
        tbl = pd.concat(allData).unstack()
        return tbl
