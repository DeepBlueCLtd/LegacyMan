from urllib.parse import urljoin

from bs4 import BeautifulSoup

"""Independent unit testable parse_region module 
to process region data
"""
REGION_COLLECTION = []


class RegionMap:
    def __init__(self, region, url):
        self.region = region
        self.url = url

    def __str__(self):
        return "{} ==> {}".format(self.region, self.url)


def extract_regions(soup: BeautifulSoup = None,
                    parsed_url: str = None,
                    parent_url: str = None,
                    userland_dict: dict = None) -> []:
    for area_element in soup.find_all('area'):
        parsed_region_url = urljoin(parsed_url, area_element.get('href'))
        REGION_COLLECTION.append(RegionMap(area_element.get('alt'), parsed_region_url))
