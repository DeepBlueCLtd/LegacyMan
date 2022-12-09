from bs4 import BeautifulSoup

from crawler.simple_crawler import SimpleCrawler


def process_soup(returned_soup: BeautifulSoup, url: str, parent_url: str):
    """The regions are processed from map"""
    for area_element in returned_soup.find_all('area'):
        if not area_element.get('href').startswith('..'):
            print("{}  ==> {}".format(area_element.get('alt'), area_element.get('href')))


craw = SimpleCrawler("data/PlatformData/PD_1.html", True)
craw.crawl(resource_processor_callback=process_soup, crawl_recursively=False)
