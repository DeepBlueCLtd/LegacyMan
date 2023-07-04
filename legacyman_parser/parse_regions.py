from urllib.parse import urljoin

from bs4 import BeautifulSoup


class RegionData:
    def __init__(self, url, regions):
        self.id = id
        self.url = url
        self.regions = regions

    def __str__(self):
        return "{}. {} ==> {}".format(self.id, self.regions, self.url)

REGION_DATA = RegionData(None, [])

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
        return "{}. {} ==> {}".format(self.id, self.region, self.url, self.coords, self.shape)


def extract_regions(soup: BeautifulSoup = None,
                    parsed_url: str = None,
                    parent_url: str = None,
                    userland_dict: dict = None):
    seq = 0

    # start off with the image
    world_image = soup.find('img', {"usemap": "#image-map"})
    assert world_image != None, "Failed to find world image"
    REGION_DATA.url = world_image['src']
        
    # now the specific regions
    for area_element in soup.find_all('area'):
        seq = seq + 1
        href = area_element.get('href')
        if not href.startswith('..'):
            parsed_region_url = urljoin(parsed_url, href)
            REGION_DATA.regions.append(RegionMap(seq, area_element.get('alt'), parsed_region_url, area_element.get('coords'), area_element.get('shape')))
