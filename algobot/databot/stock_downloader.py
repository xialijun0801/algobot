"""
algobot::databot::stock_downloader.py
================================================

The base class that downloads data for a single stock

Author: Yue Zhao (yzhao0527'at'gmail'dot'com)
Last Modified: 2014-11-15
"""

from abc import ABCMeta, abstractmethod

class StockDownloader(object, meta=ABCMeta):
    """
    Parameters
    ----------
    ticker : str, optional

    exchange : str, optional 
        exchange is optional but recommendated for some data engines,
        e.g Google. Specifying exchange explicitly usually help the
        engine locate the right stock
    """

    def __init__(self, ticker=None, exchange=None):
        self.__done = False
        self.__data = None

        if ticker is None or isinstance(exchange, str):
            self.__ticker = ticker
        else:
            raise TypeError("ticker must be of type str.")
        
        if exchange is None or isinstance(exchange, str):
            self.__exchange = exchange
        else:
            raise TypeError("exchange must be a str variable.")
    
    @abstractmethod
    def download(self):
        """Download Data from a particular data sources"""
        pass

    @property
    def done(self):
        return self.__done

    @property
    def data(self):
        if not self.__done:
            raise ValueError("Data hasn't been downloaded.")
        return self.__data

    @ticker.setter
    def ticker(self, v):
        if not isinstance(v, str):
            raise TypeError("ticker must be of type str.")
        self.__ticker = v

    @property
    def ticker(self):
        return self.__ticker

    @exchange.setter
    def exchange(self, v):
        if not isinstance(x, str):
            raise TypeError("exchange must be of type str.")
        self.__exchange = v

    @property
    def exchange(self):
        return self.__exchange

