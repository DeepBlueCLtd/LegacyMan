import sys

from crawler.simple_crawler import SimpleCrawler
from legacyman_parser.parse_countries import extract_countries_in_region, COUNTRY_COLLECTION
from legacyman_parser.parse_regions import extract_regions, REGION_COLLECTION
from legacyman_parser.parse_units_and_tonals_of_country import extract_units_tonals_of_country, UNIT_COLLECTION


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
        reg_dict = {"region": region.region}
        region_spidey = SimpleCrawler(url=region.url, disable_crawler_log=True, userland_dict=reg_dict)
        region_spidey.crawl(resource_processor_callback=extract_countries_in_region, crawl_recursively=False)
        print("parser/Region: ", region)

    for country in COUNTRY_COLLECTION:
        """Parsing class in each country and their units"""
        print("parser/Country: ", country)
        if country.url is None:
            continue
        country_dict = {"country": country.country}
        country_spidey = SimpleCrawler(url=country.url, disable_crawler_log=True, userland_dict=country_dict)
        country_spidey.crawl(resource_processor_callback=extract_units_tonals_of_country, crawl_recursively=False)

    for unit in UNIT_COLLECTION:
        print(unit)


if __name__ == "__main__":
    parse_from_root()
