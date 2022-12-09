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


def extract_regions(returned_soup: BeautifulSoup, url: str, parent_url: str) -> []:
    for area_element in returned_soup.find_all('area'):
        parsed_url = urljoin(url, area_element.get('href'))
        REGION_COLLECTION.append(RegionMap(area_element.get('alt'), parsed_url))
    return REGION_COLLECTION
