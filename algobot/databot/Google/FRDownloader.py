"""
algobot::databot::Google
================================================

API to download data from Google finance:

http://www.google.com/finance

Author: Yue Zhao (yzhao0527'at'gmail'dot'com)
Last Modified: 2014-11-15
"""

from ..stock_downloader import StockDownloader
from . import fr_codes
from urllib import request
from bs4 import BeautifulSoup
import itertools
import numpy as np
import pandas as pd

class FRDownloader(StockDownloader):
    """
    Financial Report Data Dowload
    """
    __URL = r'https://www.google.com/finance?q={}&fstype=ii'
    __Exchanges = set(['NYSE', 'NASDAQ'])

    __formIds     = ['inc{}div', 'bal{}div', 'cas{}div']
    __frequencies = ['interim', 'annual']


    def __init__(self, ticker=None, exchange=None):
        StockDownloader.__init__(self, ticker, exchange)

    
    def download(self):
        """
        download the entire HTML file from Google finance

        Return
        ------
        
        """
        assert isinstance(self.ticker, str)
        assert len(self.ticker) > 0
        if self.exchange is None:
            url = self.__URL.format(self.ticker)
        else:
            assert self.exchange in self.__Exchanges
            url = self.__URL.format(r"{}:{}".format(self.exchange,
                                                     self.ticker))

        # load data from web
        try:
            response = request.urlopen(url)
            html = response.read()
        except:
            print("Warning: download failed for {}".format(self.ticker))
        else:
            self.done = True
            self.__parseResult(html)
            

    def __parseResult(self, html):
        """
        """
        soup = BeautifulSoup(html)

        data = {}
        for fid, freq in itertools.product(self.__formIds, self.__frequencies):
            # Iterate throught 3 forms and 2 frequencies
            formId  = fid.format(freq)
            frame   = soup.find(id=formId)
            fsTable = frame.find(id="fs-table")
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

    def __init__(self, tickers):
        self.tickers = tickers
        self.downloaders = []
       
        
