# CreateTables.py

import BusinessPaths
import sqlite3
import sys


class CreateTables:
    def __init__(self):
        self.bpath = BusinessPaths.BusinessPaths()

        self.insert_statements = {}
        self.dbcon = None
        self.dbcur = None

    def db_connect(self):
        try:
            self.dbcon = sqlite3.connect(self.bpath.CompanyMasterDb)
            self.dbcur = self.dbcon.cursor()
        except sqlite3.Error as e:
            print(e)

    def create_tables(self):
        self.db_connect()
        company = [ 
            'BusinessId', 'BusinessName', 'DetailURL', 'Filename', 'DateFormed',
            'Status', 'Address', 'CityState', 'PrincipalNames', 'AgentNames'
        ] 
        self.insert_statements['Company'] = self.create_table(company, 'Company')

        details = [
            'BusinessId', 'BusinessName', 'CitizenshipStateInc', 'LatestReport',
            'BusinessAddress', 'BusinessType', 'MailingAddress', 'BusinessStatus',
            'DateIncRegistration', 'Unused'
        ]
        self.insert_statements['Details'] = self.create_table(
            details, 'Details')

        # need to assign principalId
        principals = [
            'BusinessId', 'NameTitle', 'BusinessAddress', 'ResidenceAddress'
        ]
        self.insert_statements['Principals'] = self.create_table(
            principals, 'Principals')

        agents = [
            'BusinessId', 'AgentName', 'AgentBusinessAddress',
            'AgentResidenceAddress'
        ]
        self.insert_statements['Agents'] = self.create_table(
            agents, 'Agents')

        filings = [
            'BusinessId', 'SeqNo', 'FilingId', 'FilingType', 'DateofFiling',
            'VolumeType', 'Volume', 'StartPage', 'Pages'
        ]
        self.insert_statements['Filings'] = self.create_table(
            filings, 'Filings')

    def create_table(self, header, tablename='tname'):
        """
        Create CorpTable from header record of self.bpath.corporation_master
        """
        qmarks = (f"?, " * len(header))[:-2]
        base_insert = f"INSERT INTO {tablename} VALUES "
        columns = ', '.join(header)
        sqlstr = f'DROP TABLE IF EXISTS {tablename};'
        self.dbcur.execute(sqlstr)
        sqlstr = f'CREATE TABLE IF NOT EXISTS {tablename} ({columns});'
        # print(sqlstr)
        self.dbcur.execute(sqlstr)
        self.db_commit()
        return base_insert

    def insert_data(self, tablename, columns):
        # print(f'\n{tablename}: {columns}')
        dbcolumns = None
        try:
            dbcolumns = '('
            for item in columns:
                dbcolumns = f"{dbcolumns}'{item}', "
            dbcolumns = f"{dbcolumns[:-2]});"
            sqlstr = f'{self.insert_statements[tablename]}{dbcolumns}'
            # print(f'\n{tablename}: {sqlstr}')
            self.dbcur.execute(sqlstr)
        except sqlite3.OperationalError:
            print(f'OperationalError:\n{sqlstr}')
            sys.exit(0)
        except sqlite3.IntegrityError:
            print(f'IntegrityError:\n{sqlstr}')
            sys.exit(0)


    def db_close(self, rollback=False):
        if rollback:
            self.dbcon.rollback()
        else:
            self.dbcon.commit()
        self.dbcon.close()

    def db_commit(self):
        self.dbcon.commit()

if __name__ == '__main__':
    ct = CreateTables()
    ct.create_tables()
