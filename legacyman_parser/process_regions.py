from bs4 import BeautifulSoup

from crawler.simple_crawler import SimpleCrawler

craw = SimpleCrawler("data/PlatformData/PD_1.html")


def process_soup(soup: BeautifulSoup, url: str, parent_url: str):
    print("Tango " + url + " " + str(parent_url))


craw.crawl(resource_processor_callback=process_soup)
