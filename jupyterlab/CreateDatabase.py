# CreateDatabase.py

import BusinessPaths
import CreateTables
import sqlite3
import json
import sys


class CreateDatabase:
    def __init__(self):
        self.bpath = BusinessPaths.BusinessPaths()
        self.cretab = CreateTables.CreateTables()

        with self.bpath.company_master_json.open() as fp:
            self.master = json.load(fp)

        self.dbcon = None
        self.dbcur = None

        self.CompanyMain = {}
        self.Detail = {}
        self.Principals = {}
        self.Agents = {}
        self.Filings = {}

        self.insert_statements = {}

        self.db_connect()
        self.makedb()
        self.db_close()

    def db_connect(self):
        try:
            self.dbcon = sqlite3.connect(self.bpath.CompanyMasterDb)
            self.dbcur = self.dbcon.cursor()
        except sqlite3.Error as e:
            print(e)

    def db_close(self, rollback=False):
        if rollback:
            self.dbcon.rollback()
        else:
            self.dbcon.commit()
        self.dbcon.close()

    def db_commit(self):
        self.dbcon.commit()

    def insert_business_id(self, business_id, oldvalue):
        newvalue = {}
        newvalue['BusinessId'] = business_id
        for key, dvalue in oldvalue.items():
            newvalue[key] = dvalue
        return newvalue

    def split_dict(self):
        if not self.bpath.company_main.exists():
            for business_id, details in self.master.items():
                firstcompany = True
                print(f'Business_id: {business_id}')
                for key, value in details.items():
                    if key == 'BusinessDetail':
                        if len(value):
                            newvalue = self.insert_business_id(business_id, value)
                            self.Detail[business_id] = newvalue
                    elif key == 'PrincipalsDetail':
                        if len(value):
                            newvalue = self.insert_business_id(business_id, value)
                            self.Principals[business_id] = newvalue
                    elif key == 'AgentDetail':
                        if len(value):
                            newvalue = self.insert_business_id(business_id, value)
                            self.Agents[business_id] = newvalue
                    elif key == 'FilingsDetail':
                        if len(value):
                            newvalue = self.insert_business_id(business_id, value)
                            self.Filings[business_id] = newvalue
                    else:
                        if firstcompany:
                            cnode = self.CompanyMain[business_id] = {}
                            firstcompany = False
                        cnode[key] = value
            self.save_split_files()
        else:
            self.load_split_files()
    
    def save_split_files(self):
        with self.bpath.company_main.open('w') as fp:
            json.dump(self.CompanyMain, fp)

        with self.bpath.company_detail.open('w') as fp:
            json.dump(self.Detail, fp)

        with self.bpath.company_principals.open('w') as fp:
            json.dump(self.Principals, fp)

        with self.bpath.company_agents.open('w') as fp:
            json.dump(self.Agents, fp)

        with self.bpath.company_filings.open('w') as fp:
            json.dump(self.Filings, fp)

    def load_split_files(self):
        with self.bpath.company_main.open() as fp:
            self.CompanyMain = json.load(fp)

        with self.bpath.company_detail.open() as fp:
            self.Detail = json.load(fp)

        with self.bpath.company_principals.open() as fp:
            self.Principals = json.load(fp)

        with self.bpath.company_agents.open() as fp:
            self.Agents = json.load(fp)

        with self.bpath.company_filings.open() as fp:
            self.Filings = json.load(fp)

    def makedb(self):
        self.cretab.create_tables()
        self.split_dict()

        self.insert_data(self.CompanyMain, 'Company')
        self.insert_data(self.Detail, 'Details')
        self.insert_data(self.Principals, 'Principals')
        self.insert_data(self.Agents, 'Agents')
        self.insert_data(self.Filings, 'Filings')

    def insert_data(self, data_dict, tablename):
        print(f'Loading {tablename} table')
        self.base_insert = f"INSERT INTO {tablename} VALUES "        
        keys = list(data_dict.keys())
        for key in keys:
            try:
                data = data_dict[key]
                # print(f'data: {data}')
                columns = f"("
                for item in data:
                    value = data_dict[key][item]
                    if not len(value):
                        continue
                    if isinstance(value, dict):
                        columns = f"{columns}'{item}', "
                        for key1, subitem in value.items():
                            subitem = subitem.replace("'", "''")
                            columns = f"{columns}'{subitem}', "
                        break
                    value = value.replace("'", "''")
                    columns = f"{columns}'{value}', "
                columns = f"{columns[:-2]});"
                sqlstr = f'{self.base_insert}{columns}'
                # print(f'sqlstr: {sqlstr}')
                self.dbcon.execute(sqlstr)
            except sqlite3.OperationalError:
                print(f'sqlite3.OperationalError\ndata: {data}\nsqlstr: {sqlstr}')
                sys.exit(0)
            except AttributeError:
                print(f'AttributeError\nkey: {key}, item: {item}, value: {value}, data: {data}')
                sys.exit(0)
        self.db_commit()


if __name__ == '__main__':
    CreateDatabase()
