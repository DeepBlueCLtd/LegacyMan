from urllib.parse import urljoin

from bs4 import BeautifulSoup

"""Independent unit testable parse_countries module 
to process country data
"""
COUNTRY_COLLECTION = []


class CountryMap:
    def __init__(self, id, country, region, url):
        self.id = id
        self.country = country
        self.region = region
        self.url = url

    def __str__(self):
        return "{}. {} in {} ==> {}".format(self.id, self.country, self.region.region, self.url)


def extract_countries_in_region(soup: BeautifulSoup = None,
                                parsed_url: str = None,
                                parent_url: str = None,
                                userland_dict: dict = None) -> []:
    seq = len(COUNTRY_COLLECTION)
    for country in soup.find_all('td'):
        seq = seq + 1
        COUNTRY_COLLECTION.append(create_country(seq, country, userland_dict['region'], parsed_url))


def create_country(seq, country, region, url):
    url_tag = country.find('a')
    url_str = None
    parsed_url = None
    if url_tag is not None:
        url_str = url_tag.get('href')
        parsed_url = urljoin(url, url_str)
    return CountryMap(seq, country.getText(), region, parsed_url)
