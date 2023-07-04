from urllib.parse import urljoin

from bs4 import BeautifulSoup

from legacyman_parser.parse_countries import CountryMap
from legacyman_parser.parse_regions import RegionMap

"""Independent unit testable parse_non_standard_countries module 
to process non-standard country data
"""
NON_STANDARD_COUNTRY_COLLECTION = []


def extract_non_standard_countries_in_region(
    soup: BeautifulSoup = None,
    parsed_url: str = None,
    parent_url: str = None,
    userland_dict: dict = None,
) -> []:
    seq = userland_dict["seq"]
    for area_element in soup.find_all("area"):
        href = area_element.get("href")
        country = area_element.get("alt")
        coords = area_element.get("coords")
        shape = area_element.get("shape")
        if href.startswith(".."):
            parsed_region_url = urljoin(parsed_url, href)
            NON_STANDARD_COUNTRY_COLLECTION.append(
                CountryMap(
                    seq.next_value(),
                    country,
                    RegionMap("SPL", country, parsed_region_url, coords, shape),
                    parsed_region_url,
                )
            )
