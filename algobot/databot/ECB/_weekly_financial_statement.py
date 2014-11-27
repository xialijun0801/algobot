"""
Author: Yue Zhao (yzhao0527 'at' gmail 'dot' com)
Last Modified Date: 2014-11-27
"""

import sys
import time
from datetime import date
from dateutil.relativedelta import relativedelta
import urllib
from bs4 import BeautifulSoup


class ECBFinancialStatementDownloader(object):
    """\
    Download Financial Statement from ECB Website at:

    www.ecb.europa.eu/press/pr/wfs/${yyyy}/html/index.en.html
    """

    def __init__(self):
        pass


    def getAllLinks(self, start_year=2005, end_year=None):

        monthDict = {'january' : '01', 'february' : '02', 'march' : '03',
                     'april' : '04', 'may' : '05', 'june' : '06',
                     'july' : '07', 'august' : '08', 'september' : '09',
                     'october' : '10', 'november' : '11', 'december' : '12'}

        # End Date
        if end_year is None:
            end_year = date.today().year
            
        if start_year < 2005:
            start_year = 2005

        allLinks = []
        for year in range(start_year, end_year + 1):

            # fetch list page
            url = "http://www.ecb.europa.eu/press/pr/wfs/{:4d}/html/index.en.html".format(year)
            try:
                response = urllib.request.urlopen(url)
                html     = response.read()
            except urllib.error.URLError:
                sys.stderr.write("Failed to fetch list page:")
                sys.stderr.write("    " + url)
                raise 

            # parse links to ECB
            soup       = BeautifulSoup(html)
            press_list = soup.find("div", {"class" : "pressList"})
            if press_list is None: continue
            
            item_list  = press_list.findAll("dd")
            links = []
            for item in item_list:
                title = item.find("span", {"class" : "doc-title"}).text.strip()
                link  = item.find("a", text="en")['href']

                d0, d1 = title.split('-')
                d0 = d0.strip().lower().replace("as", "").replace("at","").strip() # cannot simplify
                d1 = d1.strip().lower().replace("published", "").replace("on","").strip()  # cannot simplify

                dd, mm, yy = d0.split(' ')
                d0 = "{}{}{:02d}".format(yy, monthDict[mm], int(dd))

                dd, mm, yy = d1.split(' ')
                d1 = "{}{}{:02d}".format(yy, monthDict[mm], int(dd))

                allLinks.append({'date' : d0,
                                 'publish_date' : d1,
                                 'link' : link})

        return allLinks
    

    def getTable(self, table_name):
        """\
        Get the content of a table
        """
        url = "http://www.ecb.europa.eu/press/pr/wfs/20{}/html/{}".format(table_name[2:4], table_name)

        # fetch table page
        try:
            response = urllib.request.urlopen(url)
            html     = response.read()
        except urllib.error.URLError:
            sys.stderr.write("Failed to fetch table page:")
            sys.stderr.write("    " + url)
            raise 

        # parse table content:
        soup = BeautifulSoup(html)

        data = {}
        for asset_type in ['Assets', 'Liabilities']:
            data[asset_type] = []
            
            tbl_assets = soup.find('table', {'summary' : 'Assets'}).find('tbody')
            items      = tbl_assets.findAll("tr")
            
            for item in items:
                z = item.findAll("th")
                if len(z) > 3:
                    s = {"Level"   : 1,
                        "Label"   : z[0].text,
                        "Name"    : z[1].text,
                        "Balance" : z[2].text.replace(',',''),
                        "Diff_W"  : z[3].text.replace(',','')}
                    data[asset_type].append(s)
                    continue
    
                z = item.findAll("td")
                if len(z) > 4:
                    s = {"Level"   : 2,
                        "Label"   : z[1].text,
                        "Name"    : z[2].text,
                        "Balance" : z[3].text.replace(',',''),
                        "Diff_W"  : z[4].text.replace(',','')}
                    data[asset_type].append(s)

        return data
    

    def downloadAll(self, start_year, end_year = None, verbose=True, blink=1):

        if verbose:
            print("Downloading all links ...")
            
        allLinks = self.getAllLinks(start_year, end_year)
        
        allData = []
        for link in allLinks:
            if verbose:
                print("downloading ECB Data on {} ...".format(link['date']))

            x = {'date'         : link['date'],
                 'publish_date' : link['publish_date']}
            x['data'] = self.getTable(link['link'])
            allData.append(x)

            time.sleep(blink) # In case ECB blocks our IP

        return allData
            
if __name__ == '__main__':
    import pickle
    x = ECBFinancialStatementDownloader()
    y = x.downloadAll(2005, 2006, True)

    with open("ecb_financial_report.pkl", "wb") as f:
        pickle.dump(y, f)
