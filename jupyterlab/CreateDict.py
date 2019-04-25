# CreateDict.py

import os


class CreateDict:
    def __init__(self):
        os.chdir(os.path.abspath(os.path.dirname(__file__)))

    def new_dict(self, dictname):
        setattr(self, dictname, {})

    def add_node(self, parent, nodename):
        node = parent[nodename] = {}
        return node

    def add_cell(self, nodename, cellname, value):
        cell =  nodename[cellname] = value
        return cell

    def display_dict(self, dictname, level=0):
        indent = " " * (4 * level)
        for key, value in dictname.items():
            if isinstance(value, dict):
                print(f'\n{indent}{key}')
                level += 1
                self.display_dict(value, level)
            else:
                print(f'{indent}{key}: {value}')
            if level > 0:
                level -= 1


def testit():
    # instantiate class
    cd = CreateDict()

    # create new dictionary named CityList
    cd.new_dict('CityList')

    # add node Boston
    boston = cd.add_node(cd.CityList, 'Boston')
    # add sub node Resturants
    bos_resturants = cd.add_node(boston, 'Resturants')

    # Add subnode 'Spoke Wine Bar' to parent bos_resturants
    spoke = cd.add_node(bos_resturants, 'Spoke Wine Bar')
    cd.add_cell(spoke, 'Addr1', '89 Holland St')
    cd.add_cell(spoke, 'City', 'Sommerville')
    cd.add_cell(spoke, 'Addr1', '02144')
    cd.add_cell(spoke, 'Phone', '617-718-9463')

    # Add subnode 'Highland Kitchen' to parent bos_resturants
    highland = cd.add_node(bos_resturants, 'Highland Kitchen')
    cd.add_cell(highland, 'Addr1', '150 Highland Ave')
    cd.add_cell(highland, 'City', 'Sommerville')
    cd.add_cell(highland, 'ZipCode', '02144')
    cd.add_cell(highland, 'Phone', '617-625-1131')

    # display dictionary
    print(f'\nCityList Dictionary')
    cd.display_dict(cd.CityList)
    print(f'\nraw data: {cd.CityList}')

if __name__ == '__main__':
    testit()
