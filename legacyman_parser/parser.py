import sys

from crawler.simple_crawler import SimpleCrawler
from legacyman_parser.parse_classes_of_country import extract_classes_of_country, CLASS_COLLECTION
from legacyman_parser.parse_countries import extract_countries_in_region, COUNTRY_COLLECTION
from legacyman_parser.parse_regions import extract_regions, REGION_COLLECTION
from legacyman_parser.parse_tonals_of_class import extract_tonals_of_class, TONAL_COLLECTION

INVALID_COUNTRY_HREFS = []


def parse_from_root():
    arg = sys.argv[0:]
    if len(arg) < 2:
        print("Url empty. Exiting")
        return

    """Parsing Region
    The regions are processed from map"""
    root_spidey_to_extract_regions = SimpleCrawler(url=arg[1], disable_crawler_log=True)
    root_spidey_to_extract_regions.crawl(resource_processor_callback=extract_regions, crawl_recursively=False)

    print("\n\nRegions:")
    for region in REGION_COLLECTION:
        """Parsing Countries from extracted regions"""
        if region.url.endswith('Britain1.html'):
            continue
        reg_dict = {"region": region.region}
        region_spidey_to_extract_countries = SimpleCrawler(url=region.url,
                                                           disable_crawler_log=True,
                                                           userland_dict=reg_dict)
        region_spidey_to_extract_countries.crawl(resource_processor_callback=extract_countries_in_region,
                                                 crawl_recursively=False)
        print(region)

    print("\n\nCountries:")
    for country in COUNTRY_COLLECTION:
        """Parsing classes in each country"""
        print(country)
        if country.url is None:
            INVALID_COUNTRY_HREFS.append({"country": country.country,
                                          "url": country.url})
            continue
        country_dict = {"country": country.country}
        country_spidey_to_extract_classes = SimpleCrawler(url=country.url,
                                                          disable_crawler_log=True,
                                                          userland_dict=country_dict)
        country_spidey_to_extract_classes.crawl(resource_processor_callback=extract_classes_of_country,
                                                crawl_recursively=False)
        if len(country_spidey_to_extract_classes.unreachable_child_resources) > 0:
            INVALID_COUNTRY_HREFS.append({"country": country.country,
                                          "url": country.url})

    print("\n\nClasses:")
    for class_u in CLASS_COLLECTION:
        print(class_u)

    print("\n\nTonals:")
    for class_with_tonals in filter(lambda class_in_coll: class_in_coll.has_tonal is True, CLASS_COLLECTION):
        class_dict = {"class": class_with_tonals}
        tonal_spidey = SimpleCrawler(url=class_with_tonals.tonal_href,
                                     disable_crawler_log=True,
                                     userland_dict=class_dict)
        tonal_spidey.crawl(resource_processor_callback=extract_tonals_of_class,
                           crawl_recursively=False)

    for class_u in filter(lambda class_coll: class_coll.has_tonal is True, CLASS_COLLECTION):
        print(class_u, ":")
        for tonal in filter(lambda tonal_collection: tonal_collection.class_u == class_u, TONAL_COLLECTION):
            print(tonal)

    print("\n\nDiscrepancies:")
    for invalid_country_href in INVALID_COUNTRY_HREFS:
        print("Not able to reach href `{}` of `{}` in country_spidey".format(
            invalid_country_href["url"],
            invalid_country_href["country"]))


if __name__ == "__main__":
    parse_from_root()
