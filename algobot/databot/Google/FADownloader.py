"""
algobot::databot::Google
================================================

API to download data from Google finance:

http://www.google.com/finance

Author: Yue Zhao (yzhao0527'at'gmail'dot'com)
Last Modified: 2014-11-15
"""

from ..stock_downloader import StockDownloader

class FADownloader(StockDownloader):

    URL = r"https://www.google.com/finance?q={}"

    def __init__(self, ticker=None, exchange=None):
        super().__init__(ticker, exchange)

    def download(self):
        assert isinstance(self.__ticker, str)
        assert len(self.__ticker) > 0
        if self.__exchange is None:
            url = URL.format(self.__ticker)
        else:
            url = URL.format(r"{}%3{}".format(self.__ticker, 
                                              self.__exchange))
        print(url)
