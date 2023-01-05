from bs4 import BeautifulSoup


def phase_one_regions_parse_not_included_countries(published_json, test_payload, misc_details):
    parsed_countries = list(map(lambda a: a.country, published_json['countries']))
    for to_be_excluded_countries in test_payload:
        if to_be_excluded_countries in parsed_countries:
            print('Error: {} found in list of phase 1 parsed countries'.format(to_be_excluded_countries))
            return False
    return True


def count_of_tonal_remarks_containing_test_string(published_json, test_payload, misc_details):
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


def subtypes_should_not_have_string(published_json, test_payload, misc_details):
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


def abbreviation_should_have_string(published_json, test_payload, misc_details):
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


def count_of_class_containing_test_string_in_power_attribute(published_json, test_payload, misc_details):
    """test for issue #85
    This is to test whether merged power attributes in classes are extracted successfully.
    """
    for unit_payload in test_payload:
        class_with_required_power_attributes = filter(lambda a: unit_payload['test_string'] in a.engine,
                                                      published_json['units'])
        if len(list(class_with_required_power_attributes)) != unit_payload['count']:
            print('Error: {} failed to identify exactly {} classes with '
                  '"{}" in engine/power'.format(unit_payload,
                                                unit_payload['count'],
                                                unit_payload['test_string']))
            return False
    return True


def test_assumptions_of_actual_abbreviations_page(published_json, test_payload, misc_details):
    """Test for assumptions in issue #30"""
    """
    This is to test if abbreviations page contains one and only one table
    """
    abbreviation_page_text = None
    with open(misc_details['abbreviations_url'], 'rb') as f:
        abbreviation_page_text = f.read()
    soup = BeautifulSoup(abbreviation_page_text, "html.parser")
    abb_tables = soup.find_all('table')
    actual_number_of_tables = len(abb_tables)
    if actual_number_of_tables != test_payload['number_of_tables']:
        print('Error: Assumption that Abbreviations page has only {} table(s) failed. '
              'Found {} table(s).'.format(test_payload['number_of_tables'], actual_number_of_tables))
        return False
    """
    This is to test if abbreviations table contains only 4 table data per row
    """
    for abbrev_record in abb_tables[0].find_all('tr'):
        actual_number_tdata_elements = len(abbrev_record.find_all('td'))
        if actual_number_tdata_elements != test_payload['number_of_table_data_in_each_row']:
            print('Error: Assumption that Abbreviations table has only {} tdata per row failed. '
                  'Found {} tdata element(s).'.format(test_payload['number_of_table_data_in_each_row'],
                                                      actual_number_tdata_elements))
            return False
    return True


def check_classes_for_presence_of(published_json, test_payload, misc_details):
    """test for issue #85
    This is to test whether merged column between two running merged columns is parsed successfully
    """
    for unit_payload in test_payload:
        class_with_required_name = filter(lambda a: unit_payload in a.title,
                                                      published_json['units'])
        if len(list(class_with_required_name)) < 1:
            print('Error: {} failed to identify classes with name"{}"'.format(unit_payload,))
            return False
    return True
