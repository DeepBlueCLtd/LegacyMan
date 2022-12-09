from urllib.parse import urljoin

from bs4 import BeautifulSoup

"""Independent unit testable parse_countries module
to process country data
"""
UNIT_COLLECTION = []
TONAL_COLLECTION = []


class UnitMap:
    def __init__(self, unit, country, url):
        self.unit = unit
        self.country = country
        self.url = url

    def __str__(self):
        return "{} of {} ==> {}".format(self.unit, self.country, self.url)


def extract_units_tonals_of_country(soup: BeautifulSoup = None,
                                parsed_url: str = None,
                                parent_url: str = None,
                                userland_dict: dict = None) -> []:
    for units in soup.find_all('div', {"id": "PageLayer"}):
        UNIT_COLLECTION.append(UnitMap(str(units.find('table')), userland_dict.get("country"), parsed_url))
    return UNIT_COLLECTION
