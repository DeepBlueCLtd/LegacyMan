import os
import sys

from crawler.simple_crawler import SimpleCrawler
from legacy_publisher import json_publisher
from legacyman_parser.parse_classes_of_country import extract_classes_of_country, CLASS_COLLECTION, SUBTYPE_COLLECTION, \
    TOO_FEW_PROPERTIES
from legacyman_parser.parse_countries import extract_countries_in_region, COUNTRY_COLLECTION
from legacyman_parser.parse_regions import extract_regions, REGION_COLLECTION
from legacyman_parser.parse_tonals_of_class import extract_tonals_of_class, TONAL_COLLECTION, TONAL_TYPE_COLLECTION

INVALID_COUNTRY_HREFS = []


def path_has_drive_component(path):
    if os.path.splitdrive(path)[0]:
        return True
    return False


def path_has_back_slash(path: str):
    # Check if it has backslash
    if '\\' in path:
        return True
    return False


def change_to_drive_root_directory(path: str):
    os.chdir(os.path.splitdrive(path)[0] + "\\")


def get_cleansed_path(path: str):
    return os.path.splitdrive(path)[1].replace("\\", "/")


def parse_from_root():
    arg = sys.argv[0:]
    if len(arg) < 2:
        print("Url empty. Exiting")
        return

    # Url hardening
    arg_url = arg[1]
    cleansed_url = arg_url
    if path_has_drive_component(arg_url):
        change_to_drive_root_directory(arg_url)

    if path_has_back_slash(arg_url) or path_has_drive_component(arg_url):
        cleansed_url = get_cleansed_path(arg_url)

    """Parsing Region
    The regions are processed from map"""
    print("\n\nParsing Regions:")
    root_spidey_to_extract_regions = SimpleCrawler(url=cleansed_url, disable_crawler_log=True)
    root_spidey_to_extract_regions.crawl(resource_processor_callback=extract_regions, crawl_recursively=False)
    print("Done.")

    print("\n\nParsing Countries:")
    for region in REGION_COLLECTION:
        """Parsing Countries from extracted regions"""
        if region.url.endswith('Britain1.html'):
            continue
        reg_dict = {"region": region}
        region_spidey_to_extract_countries = SimpleCrawler(url=region.url,
                                                           disable_crawler_log=True,
                                                           userland_dict=reg_dict)
        region_spidey_to_extract_countries.crawl(resource_processor_callback=extract_countries_in_region,
                                                 crawl_recursively=False)
    print("Done.")

    print("\n\nParsing Classes:")
    for country in COUNTRY_COLLECTION:
        """Parsing classes in each country"""
        if country.url is None:
            INVALID_COUNTRY_HREFS.append({"country": country.country,
                                          "url": country.url})
            continue
        country_dict = {"country": country}
        country_spidey_to_extract_classes = SimpleCrawler(url=country.url,
                                                          disable_crawler_log=True,
                                                          userland_dict=country_dict)
        country_spidey_to_extract_classes.crawl(resource_processor_callback=extract_classes_of_country,
                                                crawl_recursively=False)
        if len(country_spidey_to_extract_classes.unreachable_child_resources) > 0:
            INVALID_COUNTRY_HREFS.append({"country": country.country,
                                          "url": country.url})
    print("Done.")

    print("\n\nParsing Tonals:")
    for class_with_tonals in filter(lambda class_in_coll: class_in_coll.has_tonal is True, CLASS_COLLECTION):
        class_dict = {"class": class_with_tonals}
        tonal_spidey = SimpleCrawler(url=class_with_tonals.tonal_href,
                                     disable_crawler_log=True,
                                     userland_dict=class_dict)
        tonal_spidey.crawl(resource_processor_callback=extract_tonals_of_class,
                           crawl_recursively=False)
    print("Done.")

    print("\n\nDiscrepancy: Unreachable or undefined country hrefs\n")
    for invalid_country_href in INVALID_COUNTRY_HREFS:
        print("    Href `{}` of `{}`.".format(
            invalid_country_href["url"],
            invalid_country_href["country"]))

    print("\n\nDiscrepancy: Some classes in the below files had too few properties than expected\n")
    for too_few_props in TOO_FEW_PROPERTIES:
        print("    " + too_few_props)

    json_publisher.publish(parsed_regions=REGION_COLLECTION,
                           parsed_countries=COUNTRY_COLLECTION,
                           parsed_classes=CLASS_COLLECTION,
                           parsed_tonals=TONAL_COLLECTION,
                           parsed_subtypes=SUBTYPE_COLLECTION,
                           parsed_tonal_types=TONAL_TYPE_COLLECTION)


if __name__ == "__main__":
    parse_from_root()
