# BusinessPaths.py

from pathlib import Path
import os


class BusinessPaths:
    def __init__(self):
        os.chdir(os.path.abspath(os.path.dirname(__file__)))
        self.homepath = Path('.')
        self.rootpath = self.homepath / '..'

        self.datapath = self.rootpath / 'data'
        self.datapath.mkdir(exist_ok=True)

        self.dbpath = self.datapath / 'database'
        self.dbpath.mkdir(exist_ok=True)

        self.htmlpath = self.datapath / 'html'
        self.htmlpath.mkdir(exist_ok=True)

        self.idpath = self.datapath / 'Idfiles'
        self.idpath.mkdir(exist_ok=True)
        
        self.jsonpath = self.datapath / 'json'
        self.jsonpath.mkdir(exist_ok=True)

        self.prettypath = self.datapath / 'pretty'
        self.prettypath.mkdir(exist_ok=True)

        self.textpath = self.datapath / 'text'
        self.textpath.mkdir(exist_ok=True)

        self.tmppath = self.datapath / 'tmp'
        self.tmppath.mkdir(exist_ok=True)

        self.base_url = 'http://searchctbusiness.ctdata.org/'

        self.cities_json = self.jsonpath / 'cities.json'
        self.city_list_url = 'https://ctstatelibrary.org/cttowns/counties'
        self.raw_city_file = self.tmppath / 'raw_city.html'
        # self.cities_text = self.textpath / 'cities.txt'

        self.company_master_json = self.jsonpath / 'CompanyMaster.json'

        self.CompanyMasterDb = self.dbpath / 'CompanyMaster.db'

        self.company_main = self.jsonpath / 'CompanyMain.json'
        self.company_detail = self.jsonpath / 'CompanyDetail.json'
        self.company_principals = self.jsonpath / 'CompanyPrincipals.json'
        self.company_agents = self.jsonpath / 'CompanyAgents.json'
        self.company_filings = self.jsonpath / 'CompanyFilings.json'


if __name__ == '__main__':
    BusinessPaths()
