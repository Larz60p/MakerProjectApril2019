# ExtractBusinessEntities.py

import BusinessPaths
from pathlib import Path
from bs4 import BeautifulSoup
import PrettifyPage
import CreateDict
import concurrent.futures
import requests
import string
import time
import json
import os
import sys


class ExtractBusinessEntities:
    def __init__(self):
        self.bpath = BusinessPaths.BusinessPaths()
        self.pp = PrettifyPage.PrettifyPage()
        self.cd = CreateDict.CreateDict()

        self.summary_file_list = []
        self.BusinessInfo = {}
        self.city_node = {}
        self.current_node = {}

        self.header_replacepairs = [ ('(', ''), (')', ''), ('/', ''), (' ', ''),
            ('MMDDYYYY', '') ]

        self.header = []
        self.create_business_info()

    def create_business_info(self):
        self.get_summary_file_list()
        self.extract_company_info()
        self.save_as_json()

    # |++++++|+++++++++|+++++++++| Section 1 - Setup |+++++++++|+++++++++|+++++++++|

    def get_summary_file_list(self):
        path = self.bpath.htmlpath
        self.summary_file_list = \
            [ filename for filename in path.iterdir() if filename.is_file() \
            and 'page' in filename.stem ]
        self.summary_file_list.sort()

    # |++++++|+++++++++|+++ Section 2 - Parse Summary Pages +++|+++++++++|+++++++++|

    def extract_company_info(self):
        self.header = []

        for file in self.summary_file_list:            
            print(f'Processing {file.name}')

            city = str(file.stem).split('_')[0]
            with file.open('rb') as fp:
                page = fp.read()
            soup = BeautifulSoup(page, 'lxml')

            table = soup.find('table')
            head = table.thead.find_all('th')

            for element in head:
                if not len(element):
                    continue
                item = element.text.strip()

                for a, b in self.header_replacepairs:
                    item = item.replace(a, b)
                self.header.append(item)

            trs = table.tbody.find_all('tr')
            self.strip_business(trs)

    def strip_business(self, trs):
        base_url = 'http://searchctbusiness.ctdata.org'

        for tr in trs:
            tds = tr.find_all('td')

            for n1, td in enumerate(tds):
                if n1 == 0:
                    detail_url = f"{base_url}{td.a.get('href')}"
                    business_id = detail_url.split('/')[-1]                    
                    business_name = td.a.text.strip()
                    detail_filename = self.bpath.idpath / f'Id{business_id}.html'

                    self.current_node = self.cd.add_node(self.BusinessInfo, business_id)
                    self.cd.add_cell(self.current_node, 'BusinessId', business_id)
                    self.cd.add_cell(self.current_node, 'BusinessName', business_name)
                    self.cd.add_cell(self.current_node, 'DetailUrl', detail_url)
                    self.cd.add_cell(self.current_node, 'Filename', os.fspath(detail_filename))
                else:
                    self.cd.add_cell(self.current_node, self.header[n1], 
                        td.text.strip())            

    # |++++++|+++++++++| Section 3 - Get and Parse Detail Pages +++++++++|+++++++++|

    def save_as_json(self):
        with self.bpath.company_master_json.open('w') as fp:
            json.dump(self.BusinessInfo, fp)

if __name__ == '__main__':
    ExtractBusinessEntities()
