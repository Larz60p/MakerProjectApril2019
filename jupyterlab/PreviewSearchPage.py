# PreviesSearchPage.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import BusinessPaths
import time
import PrettifyPage
import CreateDict
import json
import sys


class PreviewSearchPage:
    def __init__(self):
        self.bpath = BusinessPaths.BusinessPaths()
        self.pp = PrettifyPage.PrettifyPage()
        self.cd = CreateDict.CreateDict()

        self.analyze_page()

    def start_browser(self):
        caps = webdriver.DesiredCapabilities().FIREFOX
        caps["marionette"] = True
        self.browser = webdriver.Firefox(capabilities=caps)

    def stop_browser(self):
        self.browser.close()

    def save_page(self, filename):
        soup = BeautifulSoup(self.browser.page_source, "lxml")
        with filename.open('w') as fp:
            fp.write(self.pp.prettify(soup, 2))
    
    def analyze_page(self):
        self.start_browser()
        self.get_search_page('Andover')
        self.stop_browser()
    
    def get_search_page(self, searchitem):
        # pick city with multiple pages
        url = self.bpath.base_url
        self.browser.get(url)
        time.sleep(2)
        print(f'Main Page URL: {self.browser.current_url}')
        self.browser.find_element(By.XPATH, '/html/body/div[2]/div[4]/div/form/div/div/span[1]/select/option[3]').click()
        searchbox = self.browser.find_element(By.XPATH, '//*[@id="query"]')
        searchbox.clear()
        searchbox.send_keys(searchitem)
        self.browser.find_element(By.XPATH, '/html/body/div[2]/div[4]/div/form/div/div/span[3]/button').click()
        time.sleep(2)
        print(f'Results Page 1 URL: {self.browser.current_url}')        
        # get page 2
        # find next page button and click
        self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div[3]/div[2]/div/span[1]/a/icon').click()
        time.sleep(2)
        print(f'Results Page 2 URL: {self.browser.current_url}')
        # Get url of a detail page
        self.browser.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/table/tbody/tr[1]/td[1]/a').click()
        time.sleep(2)
        print(f'Detail Page URL: {self.browser.current_url}')


if __name__ == '__main__':
    PreviewSearchPage()
