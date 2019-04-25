# makePretty.py

import BusinessPaths
import PrettifyPage
from pathlib import Path
from bs4 import BeautifulSoup


class MakePretty:
    def __init__(self):
        self.bpath = BusinessPaths.BusinessPaths()
        self.pp = PrettifyPage.PrettifyPage()


    def get_a_page(self, file=None):
        with file.open() as fp:
            return fp.read()
    
    def makepretty(self, file=None):
        pretty = None
        page = self.get_a_page(file=file)
        if page:
            soup = BeautifulSoup(page, 'lxml')
            pretty = self.pp.prettify(soup, 2)
        return pretty


if __name__ == '__main__':
    mp = MakePretty()
    # plist = [filename for filename in mp.bpath.htmlpath.iterdir() if filename.is_file()]
    plist = [
        mp.bpath.idpath / 'Id0667703.html'
    ]
    for file in plist:
        ofile = mp.bpath.prettypath / f'pretty{file.name}'
        with ofile.open('w') as fp:
            fp.write(mp.makepretty(file))          
