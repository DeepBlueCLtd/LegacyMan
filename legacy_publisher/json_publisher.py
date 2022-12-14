import json
import operator

from legacy_publisher.json_templates import PlatformType, PropulsionType, PlatformSubType, Region, Country, ClassU, \
    TonalType, Tonal, TonalSource

"""This module will handle post parsing enhancements for publishing"""

EXPORT_FILE = 'target/json_publication.js'


def publish(parsed_regions=None, parsed_countries=None, parsed_classes=None, parsed_tonals=None, parsed_subtypes=None,
            parsed_tonal_types=None):
    # Hardcode Generic Platform Type
    platform_type = PlatformType(1, "Generic")

    # Hardcode Generic Propulsion Type
    propulsion_type = PropulsionType(1, "Generic")

    # Hardcode Generic Tonal Source
    tonal_source = TonalSource(1, "Generic")

    # Extract platform subtypes
    platform_sub_types = []
    for subtype_value, subtype_id in parsed_subtypes.items():
        platform_sub_types.append(PlatformSubType(subtype_id, 1, subtype_value))

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
        countries.append(Country(seq, country.region.id, country.country))

    # Extract classes
    classes = []
    for class_u in parsed_classes:
        classes.append(
            ClassU(class_u.id, class_u.class_u, class_u.sub_category[1], class_u.country.id, None, class_u.power,
                   None, None, None, None, None, None, None))

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
            Tonal(seq, tonal.class_u.class_u, tonal.tonal_type[1], tonal.source, tonal.ratio_freq, tonal.harmonics,
                  None, tonal.class_u.country, 1, tonal.class_u.sub_category[1], None, None, None))

    json_data = {"platform_types": [platform_type], "platform_sub_types": platform_sub_types,
                 "propulsion_types": [propulsion_type], "regions": regions, "tonal_sources": [tonal_source],
                 "countries": countries, "units": classes, "tonal_types": tonal_types, "tonals": tonals}

    # Dump the wrapper to the text file passed as argument
    with open(EXPORT_FILE, 'r+') as f:
        print("\n\n\nJson file: {}".format(EXPORT_FILE))
        f.truncate(0)
        print("Cleared existing contents.")
        f.write("var publicationJsonData=")
        f.write(json.dumps(json_data, default=operator.attrgetter('__dict__'), indent=2 * ' '))
        print("Dumped new content.")
