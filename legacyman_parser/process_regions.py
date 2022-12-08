from bs4 import BeautifulSoup

from crawler.simple_crawler import SimpleCrawler

craw = SimpleCrawler("data/PlatformData/PD_1.html")


def process_soup(soup: BeautifulSoup):
    print("Tango"+str(soup))


craw.crawl(resource_processor_callback=process_soup)
