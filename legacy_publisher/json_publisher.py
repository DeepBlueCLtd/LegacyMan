import json
import operator
import random

from legacy_publisher.json_templates import PlatformType, PropulsionType, PlatformSubType, Region, Country, ClassU, \
    TonalType, Tonal, TonalSource
from legacyman_parser.utils.constants import JSON_EXPORT_FILE

"""This module will handle post parsing enhancements for publishing"""

EXPORT_FILE = JSON_EXPORT_FILE

random.seed(100)


def publish(parsed_regions=None, parsed_countries=None, parsed_classes=None, parsed_tonals=None, parsed_subtypes=None,
            parsed_tonal_types=None, parsed_tonal_sources=None, parsed_abbreviations=None, parsed_flags=None,
            parsed_class_images=None):
    # Hardcode Generic Platform Type
    platform_type = PlatformType(1, "Generic Platform Type")

    # Hardcode Generic Propulsion Type
    propulsion_type = PropulsionType(1, "Generic Propulsion Type")

    # Extract tonal sources
    tonal_sources = []
    for source_value, source_id in parsed_tonal_sources.items():
        tonal_sources.append(TonalSource(source_id, source_value))

    # Extract platform subtypes
    platform_sub_types = []
    for subtype_value, subtype_id in parsed_subtypes.items():
        platform_sub_types.append(PlatformSubType(subtype_id, 1, subtype_value))

    # Extract regions
    regions = []
    for region in parsed_regions:
        regions.append(Region(region.id, region.region))

    # Extract countries
    countries = []
    for country in parsed_countries:
        countries.append(Country(country.id, country.region.id, country.country))

    # Extract classes
    classes = []
    for class_u in parsed_classes:
        image_array_react_image_gallery = []
        image_array_filtered_list = list(filter(lambda a: a.class_u.id == class_u.id, parsed_class_images))
        if image_array_filtered_list:
            image_urls_array = image_array_filtered_list[0].class_images
            image_array_react_image_gallery = list(
                map(lambda b: {"name": class_u.class_u, "url": 'images/'+b.split('target')[1][1:]}, image_urls_array))
        classes.append(
            ClassU(class_u.id, class_u.class_u, class_u.sub_category[1], class_u.country.id, None, class_u.power,
                   None, None, None, None, None, None, None, image_array_react_image_gallery))

    # Extract tonal types
    tonal_types = []
    for tonal_type_value, tonal_type_id in parsed_tonal_types.items():
        tonal_types.append(TonalType(tonal_type_id, tonal_type_value))

    # Extract tonals
    seq = 0
    tonals = []
    for tonal in parsed_tonals:
        seq = seq + 1
        tonals.append(
            Tonal(seq, tonal.class_u.id, tonal.tonal_type[1], tonal.source[1], round(random.uniform(1, 50),
                                                                                     random.choice(range(2, 5))),
                  tonal.harmonics, tonal.remarks, tonal.class_u.country.id, 1, tonal.class_u.sub_category[1],
                  None, None, None))

    def url_cleanser(flag_element):
        url = 'images/'+flag_element.file_location.split('target')[1][1:] if flag_element.file_location is not None else None
        return {"country_id": flag_element.country.id, "url": url}

    cleansed_flags = list(map(url_cleanser, parsed_flags))
    # Set flag to countries
    for flag in cleansed_flags:
        flag_country = list(filter(lambda a: a.id == flag['country_id'], countries))[0]
        flag_country.flag_url = flag['url']
    json_data = {"platform_types": [platform_type], "platform_sub_types": platform_sub_types, "regions": regions,
                 "countries": countries, "propulsion_types": [propulsion_type], "units": classes,
                 "tonal_sources": tonal_sources, "tonal_types": tonal_types, "tonals": tonals,
                 "abbreviations": parsed_abbreviations, "flags": [], "class_images": []}

    # Dump the wrapper to the text file passed as argument
    with open(EXPORT_FILE, 'w') as f:
        print("\n\n\nJson file: {}".format(EXPORT_FILE))
        f.truncate(0)
        print("Cleared existing contents.")
        f.write("var publicationJsonData=")
        f.write(json.dumps(json_data, default=operator.attrgetter('__dict__'), indent=2 * ' '))
        print("Dumped new content.")

    return json_data
