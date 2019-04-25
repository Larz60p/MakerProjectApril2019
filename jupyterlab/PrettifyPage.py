# PrettifyPage.py

from bs4 import BeautifulSoup
import requests
import BusinessPaths
import pathlib


class PrettifyPage:
    def __init__(self):
        self.bpath = BusinessPaths.BusinessPaths()

    def prettify(self, soup, indent):
        pretty_soup = str()
        previous_indent = 0
        for line in soup.prettify().split("\n"):
            current_indent = str(line).find("<")
            if current_indent == -1 or current_indent > previous_indent + 2:
                current_indent = previous_indent + 1
            previous_indent = current_indent
            pretty_soup += self.write_new_line(line, current_indent, indent)
        return pretty_soup

    def write_new_line(self, line, current_indent, desired_indent):
        new_line = ""
        spaces_to_add = (current_indent * desired_indent) - current_indent
        if spaces_to_add > 0:
            for i in range(spaces_to_add):
                new_line += " "		
        new_line += str(line) + "\n"
        return new_line

if __name__ == '__main__':
    pp = PrettifyPage()
    pfilename = pp.bpath.htmlpath / 'BusinessEntityRecordsAA.html'
    with pfilename.open('rb') as fp:
        page = fp.read()
    soup = BeautifulSoup(page, 'lxml')
    pretty = pp.prettify(soup, indent=2)
    print(pretty)
