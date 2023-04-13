import os

from bs4 import BeautifulSoup


def phase_one_regions_parse_not_included_countries(published_json, test_payload):
    parsed_countries = list(map(lambda a: a.country, published_json['countries']))
    for to_be_excluded_countries in test_payload:
        if to_be_excluded_countries in parsed_countries:
            print('Error: {} found in list of phase 1 parsed countries'.format(to_be_excluded_countries))
            return False
    return True


def count_of_tonal_remarks_containing_test_string(published_json, test_payload):
    """test for issue #77
    This is to test whether merged remarks are extracted successfully.
    """
    for unit_payload in test_payload:
        tonals_with_required_remarks = filter(lambda a: unit_payload['test_string'] in a.remarks,
                                              published_json['tonals'])
        if len(list(tonals_with_required_remarks)) != unit_payload['count']:
            print('Error: {} failed to identify exactly {} tonals '
                  'with "{}" in remarks'.format(unit_payload,
                                                unit_payload['count'],
                                                unit_payload['test_string']))
            return False
    return True


def subtypes_should_not_have_string(published_json, test_payload):
    """Test for issue #76
    This is to test if the parser has successfully ignored <td> blocks that don't
    contain attributes pertaining to platform sub type <td>
    """
    for test_string in test_payload:
        plat_sub_types_with_test_string = filter(lambda a: test_string in a.platform_sub_type,
                                                 published_json['platform_sub_types'])
        if len(list(plat_sub_types_with_test_string)) != 0:
            print('Error: Test string "{}" identified in one of the platform subtypes'.format(test_string))
            return False
    return True


def abbreviation_should_have_string(published_json, test_payload):
    """Test for issue #30
    This is to test if abbreviations are parsed properly
    """
    for unit_payload in test_payload:
        abbreviations_with_test_string = filter(lambda a: unit_payload['test_string'] in a.full_form,
                                                published_json['abbreviations'])
        if len(list(abbreviations_with_test_string)) != 1:
            print('Error: Unable to identify exactly {} instance of {}'
                  ' in abbreviations'.format(unit_payload['count'], unit_payload['test_string']))
            return False
    return True


def count_of_class_containing_test_string_in_power_attribute(published_json, test_payload):
    """test for issue #85
    This is to test whether merged power attributes in classes are extracted successfully.
    """
    for unit_payload in test_payload:
        class_with_required_power_attributes = list(filter(lambda a: unit_payload['test_string'] in a.engine,
                                                           published_json['units']))
        if len(class_with_required_power_attributes) != unit_payload['count']:
            print('Error: {} failed to identify exactly {} classes with '
                  '"{}" in engine/power'.format(unit_payload,
                                                unit_payload['count'],
                                                unit_payload['test_string']))
            return False
    return True


def check_classes_for_presence_of(published_json, test_payload):
    """test for issue #85
    This is to test whether merged column between two running merged columns is parsed successfully
    """
    for unit_payload in test_payload:
        class_with_required_name = filter(lambda a: unit_payload in a.title,
                                          published_json['units'])
        if len(list(class_with_required_name)) < 1:
            print('Error: failed to identify classes with name"{}"'.format(unit_payload))
            return False
    return True


def check_class_images_name(published_json, test_payload):
    """test for issue #48
    This is to test automatic renaming of similarly named image files during extraction
    """
    for unit_payload in test_payload:
        actual_images = list(filter(lambda a: unit_payload['image_name_contains'] in a,
                                    list(filter(lambda a: unit_payload['country'] in a.class_u.country.country,
                                                published_json['class_images']))[0].class_images))
        if len(actual_images) != unit_payload['expected_count']:
            print('Class images not renamed as expected. Failed test payload: {}'.format(unit_payload))
            return False
        for image_path in actual_images:
            if not os.path.exists(image_path):
                print('{} image file not found'.format(image_path))
                return False
    return True


def check_presence_of_common_class_images_in_different_class_folder(published_json, test_payload):
    """test for issue #48
    This is to commonly referenced images across classes are extracted and stored individually for
    different classes
    """
    for unit_payload in test_payload:
        for unit_id in unit_payload['unit_ids']:
            actual_images = list(filter(lambda a: unit_payload['image_name_contains'] in a,
                                        list(filter(lambda a: unit_id == a.class_u.id,
                                                    published_json['class_images']))[0].class_images))
            if len(actual_images) != 1:
                print('Image with name {} not found for {}. Test payload: {}'.format(
                    unit_payload['image_name_contains'], unit_id, unit_payload))
                print(actual_images)
                return False
            for image_path in actual_images:
                if not os.path.exists(image_path):
                    print('{} image file not found'.format(image_path))
                    return False
    return True


def check_presence_of_classes_of_non_standard_countries(published_json, test_payload):
    """test for issue #106
    This is to check if the parser has parsed the classes of a newly added non-standard country
    """
    class_with_required_name = list(filter(lambda a: test_payload['name'] in a.title,
                                           published_json['units']))
    if len(class_with_required_name) != test_payload['count']:
        print('Error: failed to identify exactly {} classes'
              ' with name containing"{}"'.format(test_payload['count'], test_payload['name']))
        return False
    return True


def tally_count_of_classes_of_non_standard_and_standard_countries(published_json, test_payload):
    """test for issue #106
    This is to tally the count of classes of all non-standard and standard countries
    """
    if test_payload['ns_classes'] + test_payload['s_classes'] != len(published_json['units']):
        print('Error: Could not tally counts of classes from standard and non-standard countries. '
              'Defined ns_classes count: {}, Defined standard classes: {}, Found total classes/units: {}'
              .format(test_payload['ns_classes'], test_payload['s_classes'],
                      len(published_json['units'])))
        return False
    return True


def check_for_presence_flags_of_non_standard_countries(published_json, test_payload):
    """test for issue #107
    This is to check if the parser has copied flags of non-standard countries
    """
    flags_array = set(map(lambda a: a.file_location.split("/")[-1], published_json['flags']))
    if not set(test_payload).issubset(flags_array):
        print('Error: failed to extract one or more flags of non-standard '
              'countries. {}'.format(test_payload))
        return False
    return True


def check_for_presence_of_tonals_of_classes_of_ns_countries(published_json, test_payload):
    """test for issue #107
    This is to check if the parser has processed tonals of non-standard countries
    """
    class_with_required_property = list(filter(lambda a: test_payload['name'] in a.engine,
                                               published_json['units']))
    if len(class_with_required_property) != test_payload['count']:
        print('Error: failed to identify exactly {} classes'
              ' with tonal property containing"{}"'.format(test_payload['count'], test_payload['name']))
        return False
    return True


def check_for_presence_of_tonals_of_classes_of_standard_countries(published_json, test_payload):
    """test for issue #162
    This is to check if the parser has processed tonals of standard countries
    """
    class_with_required_property = list(filter(lambda a: test_payload['name'] in a.engine,
                                               published_json['units']))
    if len(class_with_required_property) != test_payload['count']:
        print('Error: failed to identify exactly {} classes'
              ' with tonal property containing"{}"'.format(test_payload['count'], test_payload['name']))
        return False
    return True


def check_for_presence_of_tonals_of_cds_decorated_with_star(published_json, test_payload):
    """test for issue #162
    This is to check if the parser has processed tonals of standard countries
    where Commonly Detected Sources is with a star
    """
    class_with_required_property = list(filter(lambda a: test_payload['name'] in a.harmonics,
                                               published_json['tonals']))
    if len(class_with_required_property) != test_payload['count']:
        print('Error: failed to identify exactly {} tonals'
              ' with harmonics containing"{}"'.format(test_payload['count'], test_payload['name']))
        return False
    return True


def tally_tonal_counts_for_standard_and_non_standard_classes(published_json, test_payload):
    """test for issue #162
    This is to tally the count of tonals of standard and non-standard classes
    """
    if test_payload['ns_tonals'] + test_payload['standard_tonals'] != len(published_json['tonals']):
        print('Error: Could not tally counts of tonals from standard and non-standard classes. '
              'Defined ns_tonals count: {}, Defined standard tonals: {}, Found total tonals: {}'
              .format(test_payload['ns_tonals'], test_payload['standard_tonals'],
                      len(published_json['tonals'])))
        return False
    return True
