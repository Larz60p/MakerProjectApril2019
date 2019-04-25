# ScrapeConnecticut.py

import BusinessPaths
import concurrent.futures
from pathlib import Path
from bs4 import BeautifulSoup
import requests
import string
import time
import json
import os
import sys
class ScrapeConnecticut:
    def __init__(self):
        self.bpath = BusinessPaths.BusinessPaths()

        self.citydict = {}
        with self.bpath.cities_json.open() as fp:
            self.citydict = json.load(fp)

        self.citylist = []
        for city, info in self.citydict['Connecticut'].items():
            if city == 'Header':
                continue
            cityn = city.replace(' ', '')
            self.citylist.append([city, self.bpath.htmlpath / f'{cityn}_page1.html', self.get_url(city)])
        
        self.pages_to_download = len(self.citylist)

        self.numpages = []
        # self.test_parse()
        self.dispatch()
        
    def get_url(self, city, page='1'):
        return f'{self.bpath.base_url}search_results?page={page}' \
            f'&start_date=1900-01-01&end_date=2019-04-01&query={city.upper()}' \
            f'&index_field=place_of_business_city&sort_by=nm_name&sort_order=asc'

    def dispatch(self):
        self.get_numpages()
        for letter in string.ascii_uppercase:
            self.add_new_pages(letter)
            self.get_numpages()

    def add_new_pages(self, letter):
        self.citylist = []
        findstart = True
        for city, npages in self.numpages:
            if findstart and not city.startswith(letter):
                print(f'findstart city: {city}')
                continue
            findstart = False
            if not city.startswith(letter):
                print(f'for break, city: {city}')
                break
            # Remove spaces from city name.
            cityn = city.replace(' ', '')

            currentpage = 2
            finalpage = int(npages)

            while True:
                # Check if done
                if currentpage > finalpage:
                    break
                url = self.get_url(city, page=str(currentpage))

                entry = [ city, self.bpath.htmlpath / f'{cityn}_page{currentpage}.html', url ]
                self.citylist.append(entry)
                currentpage += 1

        self.pages_to_download = len(self.citylist)

        # for debugging:
        # filename = self.bpath.tmppath / 'citylist.text'
        # with filename.open('w') as fp:
        #     for entry in self.citylist:
        #         fp.write(f'{entry}\n')

        print(f'Length citylist for {city}: {self.pages_to_download}')

    def parse(self, city, filename, url):
        # Will skip files already downloaded
        # print(f'city: {city}, filename: {filename}, url: {url}')        
        print(f'fetching {filename.name}')

        if filename.exists():
            with filename.open('rb') as fp:
                page = fp.read()
        else:
            response = requests.get(url)
            if response.status_code == 200:
                time.sleep(.25)
                page = response.content
                with filename.open('wb') as fp:                
                    fp.write(page)
            else:
                print("can;t download: {url}")
                return False
        soup = BeautifulSoup(page, 'lxml')
        numpages = soup.find('span', {'class': "paginate-info"}).text.split()[2]
        return city, numpages

    def test_parse(self):
        for city, filename, url in self.citylist:
            city, numpages = self.parse(city, filename, url)
            print(f'{city}: {numpages}')

    def get_numpages(self):
        countdown = self.pages_to_download
        with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
            city_pages = [ executor.submit(self.parse, city, filename, url) for city, filename, url in self.citylist ]
            for future in concurrent.futures.as_completed(city_pages):
                countdown -= 1
                try:
                    city, numpages = future.result()
                    print(f'{city}: {numpages}')
                except TypeError as exc:
                    print(f'TypeError exception: {exc}')
                else:
                    self.numpages.append([city, numpages])
                    print(f'Remaining files: {countdown}')


if __name__ == '__main__':
    ScrapeConnecticut()
