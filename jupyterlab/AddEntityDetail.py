# AddEntityDetail.py

import BusinessPaths
from pathlib import Path
from bs4 import BeautifulSoup
import PrettifyPage
import CreateDict
import json
import concurrent.futures
import os
import requests
import time
import sys

# use Id0667703.html for testing, has all fields

class AddEntityDetail:
    def __init__(self):
        self.bpath = BusinessPaths.BusinessPaths()
        self.pp = PrettifyPage.PrettifyPage()
        self.cd = CreateDict.CreateDict()

        self.header_replacepairs = [ ('(', ''), (')', ''), ('/', ''), (' ', ''),
            ('MMDDYYYY', '') ]

        self.missing = []
        self.BusinessInfo = {}
        self.new_business_info = {}
        self.current_node = {}
        self.download_list = []
        self.filelist = []
        self.filecount = 0

        self.add_entity_detail()
    
    def load_business_info(self):
        with self.bpath.company_master_json.open() as fp:
            self.BusinessInfo = json.load(fp)
        
        for BusinessId in self.BusinessInfo.keys():
            url = self.BusinessInfo[BusinessId]['DetailUrl']
            filename = Path(self.BusinessInfo[BusinessId]['Filename'])
            self.download_list.append([filename, url])
            self.filecount += 1
        self.download_list.sort()
        # self.cd.display_dict(self.BusinessInfo)

    def add_entity_detail(self):        
        self.load_business_info()
        # self.download_detail()
        self.parse_detail()
        self.save_as_json()

    def download_detail(self):
        print('starting download')
        countdown = self.filecount

        with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
            detail_info = [ executor.submit(self.fetch_url, filename, url) for filename, url in self.download_list if not filename.exists() ]

            for future in concurrent.futures.as_completed(detail_info):
                countdown -= 1
                print(f'countdown: {countdown}')
                filename = future.result()

    def fetch_url(self, filename, url):
        print(f'fetching {filename.name}')
        response = requests.get(url)
        if response.status_code == 200:
            # time.sleep(.25)
            with filename.open('wb') as fp:                
                fp.write(response.content)
        else:
            print(f"can't download: {url}")
            return False
        return filename

    def create_file_list(self):
        self.filelist = [filename for filename in self.bpath.idpath.iterdir()
            if filename.is_file and filename.stem.startswith('Id') ]
        self.filelist.sort()

    def parse_detail(self):
        self.create_file_list()

        for filename in self.filelist:
            print(f'processing {filename.name}')

            # Get existing dictionary node
            business_id = filename.stem[2:]
            try:
                self.current_node = self.BusinessInfo[business_id]
            except KeyError:
                self.missing.append(os.fspath(filename))
                continue

            # read file
            with filename.open() as fp:
                page = fp.read()
            soup = BeautifulSoup(page, 'lxml')

            # Add Business Detail
            try:
                discard = self.current_node['BusinessDetail']
            except KeyError:
                bnode = self.cd.add_node(self.current_node, 'BusinessDetail')
                self.parse_business_details(soup, bnode)

            # Add Principals Detail
            try:
                discard = self.current_node['PrincipalsDetail']
            except KeyError:
                pnode = self.cd.add_node(self.current_node, 'PrincipalsDetail')
                self.parse_principals(soup, pnode)

            # Add Agent Detail
            try:
                discard = self.current_node['AgentDetail']
            except KeyError:
                anode = self.cd.add_node(self.current_node, 'AgentDetail')
                self.parse_agents(soup, anode)

            # Add Filings Detail
            try:
                discard = self.current_node['FilingsDetail']
            except KeyError:
                fnode = self.cd.add_node(self.current_node, 'FilingsDetail')
                self.parse_filings(soup, fnode)
     
        missingfiles = self.bpath.jsonpath / 'missing.json'
        with missingfiles.open('w') as fp:
            json.dump(self.missing, fp)
            # verify
            # self.cd.display_dict(self.current_node)
            # print(self.current_node)

    def parse_business_details(self, soup, bnode):
        table = soup.find('table', {'class': 'detail-table'})
        trs = table.tbody.find_all('tr')
        for n, tr in enumerate(trs):            
            tds = tr.find_all('td')            
            odd = True
            skipeven = False
            for n1, td in enumerate(tds):
                # print(f'\n======================== tr_{n}, tr_ {n1} ========================')
                # print(f'{self.pp.prettify(td, 2)}')
                if skipeven:
                    skipeven = False
                    continue
                if odd:
                    if not len(td):
                        if n == 2 and n1 == 2:
                            title = 'BusinessType'
                            value = 'Unspecified'
                            self.cd.add_cell(bnode, title, value)
                        elif n == 4 and n1 == 2:
                            title = 'Unused'
                            value = 'Unspecified'
                            self.cd.add_cell(bnode, title, value)
                        skipeven = True
                        continue
                    title = td.text.strip()
                    if title[-1] == ':':
                        title = title[:-1]
                    title = title.replace('/', '')
                    title = title.replace(' ', '')
                    odd = False
                else:
                    if len(td):
                        value = td.text.strip()
                    else:
                        value = 'Unspecified'
                    # Already have business id, don't need twice
                    if title == 'BusinessID':
                        odd = True
                        continue
                    self.cd.add_cell(bnode, title, value)
                    odd = True

    def parse_principals(self, soup, pnode):
        # Get header
        principals = soup.find('table', {'id': 'principals'})
        if principals:
            phead = principals.thead.find('tr')
            pheader = []
            ths = phead.find_all('th')
            for th in ths:
                item = th.text.strip()
                for a, b in self.header_replacepairs:
                    item = item.replace(a, b)
                pheader.append(item)

            trs = principals.tbody.find_all('tr')
            for tr in trs:
                tds = tr.find_all('td')
                for n1, td in enumerate(tds):
                    if len(td):
                        self.cd.add_cell(pnode, pheader[n1], td.text.strip())
                    else:
                        self.cd.add_cell(pnode, pheader[n1], 'Unspecified')

    def parse_agents(self, soup, anode):
        agents = soup.find('table', {'id': 'agents'})
        if agents:
            aheader = []
            ahead = agents.thead.find('tr')
            ths = ahead.find_all('th')
            for th in ths:
                item = th.text.strip()
                for a, b in self.header_replacepairs:
                    item = item.replace(a, b)
                aheader.append(item)

            trs = agents.tbody.find_all('tr')
            for tr in trs:
                tds = tr.find_all('td')
                for n1, td in enumerate(tds):
                    if len(td):
                        self.cd.add_cell(anode, aheader[n1], td.text.strip())
                    else:
                        self.cd.add_cell(anode, aheader[n1], 'Unspecified')

    def parse_filings(self, soup, fnode):
            filings = soup.find('table', {'id': 'filings'})
            if filings:
                fheader = []
                fhead = filings.thead.find('tr')
                ths = fhead.find_all('th')
                for th in ths:
                    title = th.text.strip()
                    if '#' in title:
                        title = title[:-2]
                    for a, b in self.header_replacepairs:
                        title = title.replace(a, b)
                    fheader.append(title)
                
                trs = filings.find_all('tr')
                seq = 1
                for tr in trs:
                    tds = tr.find_all('td')
                    fitem = self.cd.add_node(fnode, str(seq))
                    for n1, td in enumerate(tds):
                        if len(td):
                            self.cd.add_cell(fitem, fheader[n1], td.text.strip())
                        else:
                            self.cd.add_cell(fitem, fheader[n1], 'Unspecified')
                    seq += 1
    
    def save_as_json(self):
        with self.bpath.company_master_json.open('w') as fp:
            json.dump(self.BusinessInfo, fp)

if __name__ == '__main__':
    AddEntityDetail()
