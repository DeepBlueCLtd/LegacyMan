import itertools
import os
import shutil
import sys

from crawler.simple_crawler import SimpleCrawler
from legacy_publisher import json_publisher
from legacy_tester.parsed_json_tester import parsed_json_tester
from legacyman_parser.parse_abbreviations import parse_abbreviations, ABBREVIATIONS
from legacyman_parser.parse_class_attributes_from_tonals import extract_class_attributes_from_tonals_page
from legacyman_parser.parse_countries import extract_countries_in_region, COUNTRY_COLLECTION, COUNTRY_TABLE_NOT_FOUND
from legacyman_parser.parse_flag_of_country import extract_flag_of_country, COUNTRY_FLAG_COLLECTION, \
    extract_flag_of_ns_country
from legacyman_parser.parse_images_of_class import extract_class_images, CLASS_IMAGES_COLLECTION
from legacyman_parser.parse_non_standard_countries import extract_non_standard_countries_in_region, \
    NON_STANDARD_COUNTRY_COLLECTION
from legacyman_parser.parse_regions import extract_regions, REGION_DATA
from legacyman_parser.parse_tonals_of_class import extract_tonals_of_class, TONAL_COLLECTION, TONAL_TYPE_COLLECTION, \
    TONAL_SOURCE_COLLECTION, TONAL_TABLE_NOT_FOUND, TONAL_HEADER_NOT_FOUND, DIAGNOSTICS_FOR_SPLIT_TONALS
from legacyman_parser.utils.constants import COPY_CLASS_IMAGES_TO_DIRECTORY, COPY_FLAGS_TO_DIRECTORY
from legacyman_parser.utils.filter_ns_countries_in_region import filter_ns_countries, NS_COUNTRY_IN_REGION_COLLECTION
from legacyman_parser.utils.parse_class_table import ClassParser
from legacyman_parser.utils.parse_merged_rows import MergedRowsExtractor
from legacyman_parser.utils.stateful_suffix_generator import SequenceGenerator

INVALID_COUNTRY_HREFS = []


def path_has_back_slash(path: str):
    # Check if it has backslash
    if '\\' in path:
        return True
    return False


def change_to_drive_root_directory(path: str):
    os.chdir(os.path.splitdrive(path)[0] + "\\")


def get_cleansed_path(path: str):
    return os.path.splitdrive(path)[1].replace("\\", "/")


def path_has_drive_component(path):
    if os.path.splitdrive(path)[0]:
        return True
    return False


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

    uniq_id_gen_country = SequenceGenerator()
    sequence_dict = {'seq': uniq_id_gen_country}
    """Parsing Region
    The regions are processed from map"""
    print("\n\nParsing Regions:")
    root_spidey_to_extract_regions = SimpleCrawler(url=cleansed_url + "/PlatformData/PD_1.html",
                                                   disable_crawler_log=True,
                                                   userland_dict=sequence_dict)
    root_spidey_to_extract_regions.crawl(
        resource_processor_callback=extract_regions, crawl_recursively=False)
    root_spidey_to_extract_regions.crawl(resource_processor_callback=extract_non_standard_countries_in_region,
                                         crawl_recursively=False)
    print("Done. Parsed {} regions and {} non-standard countries. Map URL at {}".format(len(REGION_DATA.regions),
                                                                          len(NON_STANDARD_COUNTRY_COLLECTION), REGION_DATA.url))

    sys.exit("Finished parsing world map")

    print("\n\nParsing Classes from non-standard countries:")
    standard_class_parser = ClassParser(0, {})
    watched_unit_category_country_combination_discrepancy_collector = {}


    ns_class_parser = ClassParser(len(
        standard_class_parser.CLASS_COLLECTION), standard_class_parser.SUBTYPE_COLLECTION)
    for ns_country in NON_STANDARD_COUNTRY_COLLECTION:
        if ns_country.url is None:
            INVALID_COUNTRY_HREFS.append({"country": ns_country.country,
                                          "url": ns_country.url})
            continue
        ns_class_row_extractor = MergedRowsExtractor(7)
        ns_country_dict = {"country": ns_country,
                           "class_extractor": ns_class_row_extractor,
                           "ns_class_parser": ns_class_parser,
                           "ucc_comb_discrepancy_collection": watched_unit_category_country_combination_discrepancy_collector}
        ns_country_spidey_to_extract_classes = SimpleCrawler(url=ns_country.url,
                                                             disable_crawler_log=True,
                                                             userland_dict=ns_country_dict)
        ns_country_spidey_to_extract_classes.crawl(resource_processor_callback=ns_class_parser
                                                   .extract_classes_of_ns_country,
                                                   crawl_recursively=False)
        ns_country_spidey_to_extract_classes.crawl(resource_processor_callback=extract_flag_of_ns_country,
                                                   crawl_recursively=False)
    print("Done. Parsed {} classes from {} "
          "non-standard countries.".format(len(ns_class_parser.CLASS_COLLECTION),
                                           len(NON_STANDARD_COUNTRY_COLLECTION)))

    sys.exit("Finished parsing non-standard countries")

    print("\n\nParsing Countries:")
    for region in REGION_DATA.regions:
        """Parsing Countries from extracted regions"""
        reg_dict = {"region": region, "seq": uniq_id_gen_country}
        region_spidey_to_extract_countries = SimpleCrawler(url=region.url,
                                                           disable_crawler_log=True,
                                                           userland_dict=reg_dict)
        region_spidey_to_extract_countries.crawl(resource_processor_callback=extract_countries_in_region,
                                                 crawl_recursively=False)
    print("Done. Parsed {} countries.".format(len(COUNTRY_COLLECTION)))

    # Assert to ensure case-insensitive (as we're dealing with Win systems) country names are unique.
    # This is required as we'll be using country names to store Flag images
    sorted_list_of_countries = sorted(
        list(map(lambda a: a.country.upper(), COUNTRY_COLLECTION)))
    assert len(sorted_list_of_countries) \
           == len(set(sorted_list_of_countries)), "InvalidAssumption: Case-insensitive " \
                                                  "country names are unique. The list " \
                                                  "{} has duplicates.".format(
        sorted_list_of_countries)

    # Extract non-standard countries within region
    for country in COUNTRY_COLLECTION:
        """Extract non-standard countries within region"""
        if country.url is None:
            continue
        country_dict = {"country": country}
        spidey_to_extract_ns_country_in_region_countries = SimpleCrawler(url=country.url,
                                                                         disable_crawler_log=True,
                                                                         userland_dict=country_dict)
        spidey_to_extract_ns_country_in_region_countries.crawl(resource_processor_callback=filter_ns_countries,
                                                               crawl_recursively=False)

    # Check and delete existing flags folder, if exists
    if os.path.exists(COPY_FLAGS_TO_DIRECTORY):
        shutil.rmtree(COPY_FLAGS_TO_DIRECTORY)
    os.makedirs(COPY_FLAGS_TO_DIRECTORY)
    # Move identified ns countries from standard countries collection to ns countries collection
    for nsv in NS_COUNTRY_IN_REGION_COLLECTION:
        COUNTRY_COLLECTION.remove(nsv)
        NON_STANDARD_COUNTRY_COLLECTION.append(nsv)

    print("\n\nParsing Classes:")
    for country in COUNTRY_COLLECTION:
        """Parsing classes in each country"""
        if country.url is None:
            INVALID_COUNTRY_HREFS.append({"country": country.country,
                                          "url": country.url})
            continue
        class_row_extractor = MergedRowsExtractor(7)
        country_dict = {"country": country,
                        "class_extractor": class_row_extractor,
                        "ucc_comb_discrepancy_collection": watched_unit_category_country_combination_discrepancy_collector}
        country_spidey_to_extract_classes = SimpleCrawler(url=country.url,
                                                          disable_crawler_log=True,
                                                          userland_dict=country_dict)
        country_spidey_to_extract_classes.crawl(resource_processor_callback=standard_class_parser
                                                .extract_classes_of_country,
                                                crawl_recursively=False)
        country_spidey_to_extract_classes.crawl(resource_processor_callback=extract_flag_of_country,
                                                crawl_recursively=False)
        if len(country_spidey_to_extract_classes.unreachable_child_resources) > 0:
            INVALID_COUNTRY_HREFS.append({"country": country.country,
                                          "url": country.url})
    print("Done. Parsed {} classes and {} flags from {} countries.".format(len(standard_class_parser
                                                                               .CLASS_COLLECTION),
                                                                           len(COUNTRY_FLAG_COLLECTION),
                                                                           len(COUNTRY_COLLECTION)))

    print("\n\nParsing tonals and class images:")
    # Check and delete existing folder, if exists
    if os.path.exists(COPY_CLASS_IMAGES_TO_DIRECTORY):
        shutil.rmtree(COPY_CLASS_IMAGES_TO_DIRECTORY)
    for class_with_tonals in filter(lambda class_in_coll: class_in_coll.has_tonal is True,
                                    standard_class_parser.CLASS_COLLECTION):
        tonal_row_extractor = MergedRowsExtractor(4)
        class_dict = {"class": class_with_tonals,
                      "tonal_extractor": tonal_row_extractor}
        tonal_spidey = SimpleCrawler(url=class_with_tonals.tonal_href,
                                     disable_crawler_log=True,
                                     userland_dict=class_dict)
        tonal_spidey.crawl(resource_processor_callback=extract_tonals_of_class,
                           crawl_recursively=False)
        tonal_spidey.crawl(resource_processor_callback=extract_class_images,
                           crawl_recursively=False)
        propulsion_spidey = SimpleCrawler(url=class_dict['class'].propulsion_href,
                                          disable_crawler_log=True,
                                          userland_dict=class_dict)
        propulsion_spidey.crawl(resource_processor_callback=extract_class_attributes_from_tonals_page,
                                crawl_recursively=False)
    standard_tonals = len(TONAL_COLLECTION)
    standard_class_images = sum(
        list(map(lambda a: len(a.class_images), CLASS_IMAGES_COLLECTION)))
    print("Done. Parsed {} tonals and {} class images from {} classes.".format(standard_tonals,
                                                                               standard_class_images,
                                                                               len(standard_class_parser
                                                                                   .CLASS_COLLECTION)))

    print("\n\nParsing tonals and class images of classes of non-standard countries:")
    for ns_class_with_tonals in filter(lambda class_in_coll: class_in_coll.has_tonal is True,
                                       ns_class_parser.CLASS_COLLECTION):
        ns_tonal_row_extractor = MergedRowsExtractor(4)
        class_dict = {"class": ns_class_with_tonals,
                      "tonal_extractor": ns_tonal_row_extractor}
        ns_class_tonal_spidey = SimpleCrawler(url=ns_class_with_tonals.tonal_href,
                                              disable_crawler_log=True,
                                              userland_dict=class_dict)
        ns_class_tonal_spidey.crawl(resource_processor_callback=extract_tonals_of_class,
                                    crawl_recursively=False)
        ns_class_tonal_spidey.crawl(resource_processor_callback=extract_class_images,
                                    crawl_recursively=False)
        ns_class_propulsion_spidey = SimpleCrawler(url=ns_class_with_tonals.propulsion_href,
                                                   disable_crawler_log=True,
                                                   userland_dict=class_dict)
        ns_class_propulsion_spidey.crawl(resource_processor_callback=extract_class_attributes_from_tonals_page,
                                         crawl_recursively=False)
    ns_class_images = sum(list(map(lambda a: len(
        a.class_images), CLASS_IMAGES_COLLECTION))) - standard_class_images
    print("Done. Parsed {} tonals and {} class images from {} "
          "classes of non-standard countries.".format(len(TONAL_COLLECTION) - standard_tonals,
                                                      ns_class_images,
                                                      len(ns_class_parser
                                                          .CLASS_COLLECTION)))

    print("\n\nParsing Abbreviations:")
    abbreviations_url = cleansed_url + "/QuickLinksData/Abbreviations.html"
    root_spidey_to_extract_abbreviations = SimpleCrawler(
        url=abbreviations_url, disable_crawler_log=True)
    root_spidey_to_extract_abbreviations.crawl(
        resource_processor_callback=parse_abbreviations, crawl_recursively=False)
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

    if standard_class_parser.COUNTRIES_WITHOUT_CLASS_TABLE:
        print("\n\nDiscrepancy: Below urls contain non-standard countries where classes couldn't be identified\n")
        for non_standard_countries in standard_class_parser.COUNTRIES_WITHOUT_CLASS_TABLE:
            print("    " + non_standard_countries)

    if standard_class_parser.TOO_FEW_PROPERTIES:
        print("\n\nDiscrepancy: Some classes in the below files had too few properties than expected\n")
        for too_few_props in standard_class_parser.TOO_FEW_PROPERTIES:
            print("    " + too_few_props)

    if TONAL_HEADER_NOT_FOUND:
        print("\n\nDiscrepancy: Tonal header was not found in these urls\n")
        for no_tonal_header in TONAL_HEADER_NOT_FOUND:
            print("    " + no_tonal_header)

    if TONAL_TABLE_NOT_FOUND:
        print("\n\nDiscrepancy: Tonal table was not found in these urls\n")
        for no_tonal_table in TONAL_TABLE_NOT_FOUND:
            print("    " + no_tonal_table)

    if DIAGNOSTICS_FOR_SPLIT_TONALS:
        print("\n\nDiagnostics: Tonal pages with Propulsion in a different page\n")
        print("    There are a total of {} split references\n".format(len(DIAGNOSTICS_FOR_SPLIT_TONALS)))
        for tonal_page, propulsion_href in DIAGNOSTICS_FOR_SPLIT_TONALS.items():
            print("    ", tonal_page, " ==> ", propulsion_href)

    published_json = json_publisher.publish(parsed_regions=REGION_COLLECTION,
                                            parsed_countries=COUNTRY_COLLECTION + NON_STANDARD_COUNTRY_COLLECTION,
                                            parsed_classes=standard_class_parser.CLASS_COLLECTION +
                                                           ns_class_parser.CLASS_COLLECTION,
                                            parsed_tonals=TONAL_COLLECTION,
                                            parsed_subtypes=ns_class_parser.SUBTYPE_COLLECTION,
                                            parsed_tonal_types=TONAL_TYPE_COLLECTION,
                                            parsed_tonal_sources=TONAL_SOURCE_COLLECTION,
                                            parsed_abbreviations=ABBREVIATIONS,
                                            parsed_flags=COUNTRY_FLAG_COLLECTION,
                                            parsed_class_images=CLASS_IMAGES_COLLECTION)

    # Assert assumptions on extracted data
    # Data assumption 1: Classes are unique for a given country and sub category
    max_class_for_given_country_subcat = list(filter(lambda a: a[1] > 1, list(map(lambda a: (a[0], len(list(a[1]))),
                                                                                  itertools.groupby(sorted(
                                                                                      list(map(lambda a: (
                                                                                              a.country.country + "|" +
                                                                                              a.sub_category[
                                                                                                  0] + "|" + a.class_u).lower(),
                                                                                               standard_class_parser.CLASS_COLLECTION + ns_class_parser.CLASS_COLLECTION))),
                                                                                      lambda a: a)))))
    if max_class_for_given_country_subcat:
        print("====")
        print("InvalidAssumption: Classes are unique for a given country and sub category")
        print("The following combinations have more than 1 items")
        for item in max_class_for_given_country_subcat:
            print("   Combination: {}, Count = {}, Referenced from {}"
                  .format(item[0],
                          item[1],
                          watched_unit_category_country_combination_discrepancy_collector[item[0]]))

    if test_payload_json is not None:
        print("\n\nTest results:")
        if parsed_json_tester(published_json, test_payload_json):
            print("All tests successful.")


if __name__ == "__main__":
    parse_from_root()
