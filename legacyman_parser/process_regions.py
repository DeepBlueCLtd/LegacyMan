from bs4 import BeautifulSoup

from crawler.simple_crawler import SimpleCrawler


def process_soup(returned_soup: BeautifulSoup, url: str, parent_url: str):
    """This assumes that there's going to be only
    one table of regions in this page"""
    for rows in returned_soup.find_all('td'):
        print(rows)


craw = SimpleCrawler("data/PlatformData/PD_1.html", True)
craw.crawl(resource_processor_callback=process_soup, crawl_recursively=False)
