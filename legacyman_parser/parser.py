import sys

from crawler.simple_crawler import SimpleCrawler
from legacyman_parser.parse_countries import extract_countries_in_region, COUNTRY_COLLECTION
from legacyman_parser.parse_regions import extract_regions, REGION_COLLECTION


def parse_from_root():
    arg = sys.argv[0:]
    if len(arg) < 2:
        print("Url empty. Exiting")
        return

    """Parsing Region
    The regions are processed from map"""
    spidey = SimpleCrawler(url=arg[1], disable_crawler_log=True)
    spidey.crawl(resource_processor_callback=extract_regions, crawl_recursively=False)

    for region in REGION_COLLECTION:
        """Parsing Countries from extracted regions
        The regions are processed from map"""
        if region.url.endswith('Britain1.html'):
            continue
        region_spidey = SimpleCrawler(url=region.url, disable_crawler_log=True)
        region_spidey.crawl(resource_processor_callback=extract_countries_in_region, crawl_recursively=False)
        print("parser/Region: ", region)

    for country in COUNTRY_COLLECTION:
        print("parser/Country: ", country)


if __name__ == "__main__":
    parse_from_root()
