from urllib.parse import urljoin

from bs4 import BeautifulSoup

from legacyman_parser.parse_countries import CountryMap
from legacyman_parser.parse_regions import RegionMap

"""Independent unit testable parse_non_standard_countries module 
to process non-standard country data
"""
NON_STANDARD_COUNTRY_COLLECTION = []


def extract_non_standard_countries_in_region(soup: BeautifulSoup = None,
                                             parsed_url: str = None,
                                             parent_url: str = None,
                                             userland_dict: dict = None) -> []:
    seq = len(NON_STANDARD_COUNTRY_COLLECTION)
    for area_element in soup.find_all('area'):
        seq = seq + 1
        href = area_element.get('href')
        country = area_element.get('alt')
        if href.startswith('..'):
            parsed_region_url = urljoin(parsed_url, href)
            NON_STANDARD_COUNTRY_COLLECTION.append(CountryMap(seq, country,
                                                              RegionMap("SPL", country, None),
                                                              parsed_region_url))
