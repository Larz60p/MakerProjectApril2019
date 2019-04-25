# CreateCityFile.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import BusinessPaths
import time
import PrettifyPage
import CreateDict
import json
import sys


class CreateCityFile:
    def __init__(self):
        self.bpath = BusinessPaths.BusinessPaths()
        self.pp = PrettifyPage.PrettifyPage()
        self.cd = CreateDict.CreateDict()

        self.header = []
        self.city_info = {}

        self.get_city_info()

    def start_browser(self):
        caps = webdriver.DesiredCapabilities().FIREFOX
        caps["marionette"] = True
        self.browser = webdriver.Firefox(capabilities=caps)

    def stop_browser(self):
        self.browser.close()

    def get_city_info(self):
        if not self.bpath.cities_json.exists():
            if self.bpath.raw_city_file.exists():
                with self.bpath.raw_city_file.open() as fp:
                    page = fp.read()
                soup = BeautifulSoup(page, "lxml")
            else:
                self.start_browser()
                self.browser.get(self.bpath.city_list_url)
                time.sleep(2)
                page = self.browser.page_source
                # save working copy and pretty copy for analysis in temp
                with self.bpath.raw_city_file.open('w') as fp:
                    fp.write(page)
                soup = BeautifulSoup(page, "lxml")
                prettyfile = self.bpath.prettypath / 'raw_city_file_pretty.html'
                with prettyfile.open('w') as fp:
                    fp.write(f'{self.pp.prettify(soup, 2)}')
                self.stop_browser()
            table = soup.find('table', {'summary': 'This table displays Connecticut towns and the year of their establishment.'})
            trs = table.tbody.find_all('tr')

            # Create Node to separate Connecticut - May contain multiple states later
            masternode = self.cd.add_node(self.city_info, 'Connecticut')
            
            citynode = None
            contigname = 'Unspecified'
            for n, tr in enumerate(trs):
                if n == 0:
                    self.header = []
                    for td in self.get_td(tr):                            
                        self.header.append(td.p.b.i.text.strip())
                    self.cd.add_cell(masternode, 'Header', self.header)
                else:
                    for n1, td in enumerate(self.get_td(tr)):
                        # print(f'==================================== tr {n}, td: {n1} ====================================')
                        # print(f'{self.pp.prettify(td, 2)}')
                        if n1 == 0:
                            citynode = self.cd.add_node(masternode, f'{td.p.text.strip()}')
                        value = td.p
                        if td.p is None:
                            value = 'Unspecified'
                        else:
                            value = td.p.text.strip()
                            if value == '—-':
                                value ='No parent town'
                        self.cd.add_cell(citynode, self.header[n1], value.strip())
                        if self.header[n1] == 'Town name':
                            contigname = value.strip().replace(' ', '')
                    self.cd.add_cell(citynode, 'ContiguousCityName', contigname)
            self.cd.display_dict(self.city_info)

            # Create json file
            with self.bpath.cities_json.open('w') as fp:
                json.dump(self.city_info, fp)


    def get_td(self, tr):
        tds = tr.find_all('td')
        for td in tds:
            yield td

if __name__ == '__main__':
    CreateCityFile()
