from urllib.parse import urljoin

from bs4 import BeautifulSoup

"""Independent unit testable parse_region module 
to process region data
"""
REGION_COLLECTION = []


class RegionMap:
    def __init__(self, id, region, url):
        self.id = id
        self.region = region
        self.url = url
    
    def __init__(self, id, region, url, coords, shape):
        self.id = id
        self.region = region
        self.url = url
        self.coords = coords
        self.shape = shape

    def __str__(self):
        return "{}. {} ==> {}".format(self.id, self.region, self.url)

    def __str__(self):
        return "{}. {} ==> {}".format(self.id, self.region, self.url, self.coords, self.shape)


def extract_regions(soup: BeautifulSoup = None,
                    parsed_url: str = None,
                    parent_url: str = None,
                    userland_dict: dict = None) -> []:
    seq = 0
    for area_element in soup.find_all('area'):
        seq = seq + 1
        href = area_element.get('href')
        if not href.startswith('..'):
            parsed_region_url = urljoin(parsed_url, href)
            REGION_COLLECTION.append(RegionMap(seq, area_element.get('alt'), parsed_region_url, area_element.get('coords'), area_element.get('shape')))
