from urllib.parse import urljoin

from bs4 import BeautifulSoup

"""Independent unit testable parse_countries module 
to process country data
"""
COUNTRY_COLLECTION = []


class CountryMap:
    def __init__(self, country, url):
        self.country = country
        self.url = url

    def __str__(self):
        return "{} ==> {}".format(self.country, self.url)


def extract_countries_in_region(returned_soup: BeautifulSoup, url: str, parent_url: str) -> []:
    for country in returned_soup.find_all('td'):
        COUNTRY_COLLECTION.append(create_country(country, url))
    return COUNTRY_COLLECTION


def create_country(country, url):
    url_tag = country.find('a')
    url_str = None
    parsed_url = None
    if url_tag is not None:
        url_str = url_tag.get('href')
        parsed_url = urljoin(url, url_str)
    return CountryMap(country.getText(), parsed_url)
