import os
import shutil
import sys

from crawler.simple_crawler import SimpleCrawler
from legacy_publisher import json_publisher
from legacy_tester.parsed_json_tester import parsed_json_tester
from legacyman_parser.parse_abbreviations import parse_abbreviations, ABBREVIATIONS
from legacyman_parser.parse_classes_of_country import extract_classes_of_country, CLASS_COLLECTION, SUBTYPE_COLLECTION, \
    TOO_FEW_PROPERTIES, NON_STANDARD_COUNTRY
from legacyman_parser.parse_countries import extract_countries_in_region, COUNTRY_COLLECTION, COUNTRY_TABLE_NOT_FOUND
from legacyman_parser.parse_flag_of_country import extract_flag_of_country, COUNTRY_FLAG_COLLECTION
from legacyman_parser.parse_images_of_class import extract_class_images, CLASS_IMAGES_COLLECTION
from legacyman_parser.parse_regions import extract_regions, REGION_COLLECTION
from legacyman_parser.parse_tonals_of_class import extract_tonals_of_class, TONAL_COLLECTION, TONAL_TYPE_COLLECTION, \
    TONAL_SOURCE_COLLECTION, TONAL_TABLE_NOT_FOUND, TONAL_HEADER_NOT_FOUND
from legacyman_parser.utils.constants import COPY_CLASS_IMAGES_TO_DIRECTORY
from legacyman_parser.utils.parse_merged_rows import MergedRowsExtractor

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

    # test_payload_for_parsed_json
    kw_args = dict(arg.split('=') for arg in sys.argv[2:])
    test_payload_json = kw_args.get('test_payload_for_parsed_json', None)
    if test_payload_json is not None and not os.path.isfile(test_payload_json):
        print("Cannot find json test payload at {}".format(test_payload_json))
        return

    """Parsing Region
    The regions are processed from map"""
    print("\n\nParsing Regions:")
    root_spidey_to_extract_regions = SimpleCrawler(url=cleansed_url + "/PlatformData/PD_1.html",
                                                   disable_crawler_log=True)
    root_spidey_to_extract_regions.crawl(resource_processor_callback=extract_regions, crawl_recursively=False)
    print("Done. Parsed {} regions.".format(len(REGION_COLLECTION)))

    print("\n\nParsing Countries:")
    for region in REGION_COLLECTION:
        """Parsing Countries from extracted regions"""
        reg_dict = {"region": region}
        region_spidey_to_extract_countries = SimpleCrawler(url=region.url,
                                                           disable_crawler_log=True,
                                                           userland_dict=reg_dict)
        region_spidey_to_extract_countries.crawl(resource_processor_callback=extract_countries_in_region,
                                                 crawl_recursively=False)
    print("Done. Parsed {} countries.".format(len(COUNTRY_COLLECTION)))

    # Assert to ensure case-insensitive (as we're dealing with Win systems) country names are unique.
    # This is required as we'll be using country names to store Flag images
    sorted_list_of_countries = sorted(list(map(lambda a: a.country.upper(), COUNTRY_COLLECTION)))
    assert len(sorted_list_of_countries) \
           == len(set(sorted_list_of_countries)), "InvalidAssumption: Case-insensitive country names " \
                                                  "are unique. The list {} has duplicates.".format(sorted_list_of_countries)

    print("\n\nParsing Classes:")
    for country in COUNTRY_COLLECTION:
        """Parsing classes in each country"""
        if country.url is None:
            INVALID_COUNTRY_HREFS.append({"country": country.country,
                                          "url": country.url})
            continue
        class_row_extractor = MergedRowsExtractor(7)
        country_dict = {"country": country, "class_extractor": class_row_extractor}
        country_spidey_to_extract_classes = SimpleCrawler(url=country.url,
                                                          disable_crawler_log=True,
                                                          userland_dict=country_dict)
        country_spidey_to_extract_classes.crawl(resource_processor_callback=extract_classes_of_country,
                                                crawl_recursively=False)
        country_spidey_to_extract_classes.crawl(resource_processor_callback=extract_flag_of_country,
                                                crawl_recursively=False)
        if len(country_spidey_to_extract_classes.unreachable_child_resources) > 0:
            INVALID_COUNTRY_HREFS.append({"country": country.country,
                                          "url": country.url})
    print("Done. Parsed {} classes and {} flags from {} countries.".format(len(CLASS_COLLECTION),
                                                                           len(COUNTRY_FLAG_COLLECTION),
                                                                           len(COUNTRY_COLLECTION)))

    print("\n\nParsing tonals and class images:")
    # Check and delete existing folder, if exists
    if os.path.exists(COPY_CLASS_IMAGES_TO_DIRECTORY):
        shutil.rmtree(COPY_CLASS_IMAGES_TO_DIRECTORY)
    for class_with_tonals in filter(lambda class_in_coll: class_in_coll.has_tonal is True, CLASS_COLLECTION):
        tonal_row_extractor = MergedRowsExtractor(4)
        class_dict = {"class": class_with_tonals, "tonal_extractor": tonal_row_extractor}
        tonal_spidey = SimpleCrawler(url=class_with_tonals.tonal_href,
                                     disable_crawler_log=True,
                                     userland_dict=class_dict)
        tonal_spidey.crawl(resource_processor_callback=extract_tonals_of_class,
                           crawl_recursively=False)
        tonal_spidey.crawl(resource_processor_callback=extract_class_images,
                           crawl_recursively=False)
    print("Done. Parsed {} tonals and {} class images from {} classes.".format(len(TONAL_COLLECTION),
                                                                               len(CLASS_IMAGES_COLLECTION),
                                                                               len(CLASS_COLLECTION)))

    print("\n\nParsing Abbreviations:")
    abbreviations_url = cleansed_url + "/QuickLinksData/Abbreviations.html"
    root_spidey_to_extract_abbreviations = SimpleCrawler(url=abbreviations_url, disable_crawler_log=True)
    root_spidey_to_extract_abbreviations.crawl(resource_processor_callback=parse_abbreviations, crawl_recursively=False)
    print("Done. Parsed {} abbreviations.".format(len(ABBREVIATIONS)))

    if COUNTRY_TABLE_NOT_FOUND:
        print("\n\nDiscrepancy: Couldn't identify table of countries in these urls\n")
        for country_table_not_found_url in COUNTRY_TABLE_NOT_FOUND:
            print("    " + country_table_not_found_url)

    if INVALID_COUNTRY_HREFS:
        print("\n\nDiscrepancy: Unreachable or undefined country hrefs\n")
        for invalid_country_href in INVALID_COUNTRY_HREFS:
            print("    Href `{}` of `{}`.".format(
                invalid_country_href["url"],
                invalid_country_href["country"]))

    if NON_STANDARD_COUNTRY:
        print("\n\nDiscrepancy: Below urls contain non-standard countries where classes couldn't be identified\n")
        for non_standard_countries in NON_STANDARD_COUNTRY:
            print("    " + non_standard_countries)

    if TOO_FEW_PROPERTIES:
        print("\n\nDiscrepancy: Some classes in the below files had too few properties than expected\n")
        for too_few_props in TOO_FEW_PROPERTIES:
            print("    " + too_few_props)

    if TONAL_HEADER_NOT_FOUND:
        print("\n\nDiscrepancy: Tonal header was not found in these urls\n")
        for no_tonal_header in TONAL_HEADER_NOT_FOUND:
            print("    " + no_tonal_header)

    if TONAL_TABLE_NOT_FOUND:
        print("\n\nDiscrepancy: Tonal table was not found in these urls\n")
        for no_tonal_table in TONAL_TABLE_NOT_FOUND:
            print("    " + no_tonal_table)

    published_json = json_publisher.publish(parsed_regions=REGION_COLLECTION,
                                            parsed_countries=COUNTRY_COLLECTION,
                                            parsed_classes=CLASS_COLLECTION,
                                            parsed_tonals=TONAL_COLLECTION,
                                            parsed_subtypes=SUBTYPE_COLLECTION,
                                            parsed_tonal_types=TONAL_TYPE_COLLECTION,
                                            parsed_tonal_sources=TONAL_SOURCE_COLLECTION,
                                            parsed_abbreviations=ABBREVIATIONS,
                                            parsed_flags=COUNTRY_FLAG_COLLECTION,
                                            parsed_class_images=CLASS_IMAGES_COLLECTION)

    if test_payload_json is not None:
        print("\n\nTest results:")
        if parsed_json_tester(published_json, test_payload_json):
            print("All tests successful.")


if __name__ == "__main__":
    parse_from_root()
