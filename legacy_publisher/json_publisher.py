import operator

import json

from legacy_publisher.json_templates import PlatformType, PlatformSubType, Region, Country, ClassU, TonalType, Tonal

"""This module will handle post parsing enhancements for publishing"""

EXPORT_FILE = 'target/json_publication.js'


def publish(parsed_regions=None, parsed_countries=None, parsed_classes=None, parsed_tonals=None):
    # Hardcode Generic Platform Type
    platform_type = PlatformType(1, "Generic")

    # Extract platform subtypes
    seq = 0
    distinct_subtypes = [*set(map(lambda class_in_coll: class_in_coll.sub_category, parsed_classes))]
    platform_sub_types = []
    for subtype in distinct_subtypes:
        seq = seq + 1
        platform_sub_types.append(PlatformSubType(seq, 1, subtype))

    # Extract regions
    seq = 0
    regions = []
    for region in parsed_regions:
        seq = seq + 1
        regions.append(Region(seq, region.region))

    # Extract countries
    seq = 0
    countries = []
    for country in parsed_countries:
        seq = seq + 1
        countries.append(Country(seq, country.region, country.country))

    # Extract classes
    seq = 0
    classes = []
    for class_u in parsed_classes:
        seq = seq + 1
        classes.append(ClassU(seq, class_u.class_u, class_u.sub_category, class_u.country, None, class_u.power,
                              None, None, None, None, None, None, None))

    # Extract tonal types
    seq = 0
    distinct_tonal_types = [*set(map(lambda tonal_in_coll: tonal_in_coll.tonal_type, parsed_tonals))]
    tonal_types = []
    for tonal_type in distinct_tonal_types:
        seq = seq + 1
        tonal_types.append(TonalType(seq, tonal_type))

    # Extract tonals
    seq = 0
    tonals = []
    for tonal in parsed_tonals:
        seq = seq + 1
        tonals.append(
            Tonal(seq, tonal.class_u.class_u, tonal.tonal_type, tonal.source, tonal.ratio_freq, tonal.harmonics,
                  None, tonal.class_u.country, 1, tonal.class_u.sub_category, None, None, None))

    json_data = {"platform_types": [platform_type], "platform_sub_types": platform_sub_types, "regions": regions,
                 "countries": countries, "classes": classes, "tonal_types": tonal_types, "tonals": tonals}

    # Dump the wrapper to the text file passed as argument
    with open(EXPORT_FILE, 'r+') as f:
        print("\n\n\nJson file: {}".format(EXPORT_FILE))
        f.truncate(0)
        print("Cleared existing contents.")
        f.write("var publicationJsonData=")
        f.write(json.dumps(json_data, default=operator.attrgetter('__dict__'), indent=2 * ' '))
        print("Dumped new content.")
