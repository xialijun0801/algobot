"""
algobot::databot::stock_downloader.py
================================================

The base class that downloads data for a single stock

Author: Yue Zhao (yzhao0527'at'gmail'dot'com)
Last Modified: 2014-11-15
"""

from abc import ABCMeta, abstractmethod
import time

class StockDownloader(metaclass=ABCMeta):
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

        if ticker is None or isinstance(ticker, str):
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

    @done.setter
    def done(self, v):
        self.__done = v
    
    @property
    def data(self):
        if not self.__done:
            raise ValueError("Data hasn't been downloaded.")
        return self.__data

    @data.setter
    def data(self, v):
        self.__data = v
    
    @property
    def ticker(self):
        return self.__ticker

    @ticker.setter
    def ticker(self, v):
        if not isinstance(v, str):
            raise TypeError("ticker must be of type str.")
        self.__ticker = v
    
    @property
    def exchange(self):
        return self.__exchange
    
    @exchange.setter
    def exchange(self, v):
        if not isinstance(x, str):
            raise TypeError("exchange must be of type str.")
        self.__exchange = v



class BatchDownloader(object, metaclass=ABCMeta):
    """
    Batch Downloader Base Class
    """
    
    def __init__(self, downloader):
        """
        Initialize BatchDownloader
        --------------------------

        parameters
        ==========
        downloader StockDownloader object
        """
        assert issubclass(downloader, StockDownloader)
        self.D = downloader
        self.downloaders = {}

    
    def addTickers(self, arg):
        """
        Add list of (ticker, exchange) to the BatchDownloader
        --------------------------

        Parameters
        ==========
        arg str, dict of (ticker, exchange) pairs, or any iterable object
            of strings
        """
        if isinstance(arg, dict):
            for ticker, exchange in arg.items():
                self.downloaders[ticker] = self.D(ticker, exchange)
        elif isinstance(arg, str):
            self.downloaders[arg] = self.D(ticker)
        else:
            # skip chekcing if arg is iterable
            for ticker in arg:
                self.downloaders[ticker] = self.D(ticker)
            

    def download(self, blink=1, interval=30, n_iter=10, verbose=True):
        """
        Download All Data
        -----------------

        parameters
        ==========
        blink int, seconds to wait between downloading two stocks
        
        interval int, seconds to wait between two iterations
        
        n_iter int, number of iterations 
        """
        n_iter = max(1, n_iter)
        for loop in range(n_iter):
            
            allDone = True
            
            for k, v in self.downloaders.items():
                
                if not v.done:
                    
                    try:
                        v.download()
                    except:
                        if verbose:
                            print("loop {} - process {}: exception raised.".format(loop, k))
                    else:
                        if not v.done:
                            allDone = False
                            if verbose:
                                print("loop {} - process {}: failed.".format(loop, k))
                        else:
                            print("loop {} - process {}: succeeded.".format(loop, k))
                    time.sleep(blink)
                
            if allDone: break
            
            time.sleep(interval)


    @abstractmethod
    def fetchResult(self):
        pass
