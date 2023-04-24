from bs4 import BeautifulSoup

"""
Independent testable parse tonal class attributes
"""

PROPULSION_ATTRIBUTES_HTML_PUB5_MAPPING = {
    'Cruise Plant': 'power',
    'Boost Plant': None,
    'Reduction Ratio': 'reduction_ratio',
    'R:R': 'reduction_ratio',
    'Max TRPM': None,
    'TRPM Range': None,
    'Shaft x Blade': 'shaft_blade',
    'MTBF': None,
    'BHP': 'bhp',
    'Max SRPM': None,
    'SRPM Range': None
}


def max_four_column_table_filter_outside_quicklinks(tag):
    first_row = tag.find('tr')
    first_cell = first_row.find('td')
    return first_cell and first_cell.get('colspan') == "4"


def extract_class_attributes_from_tonals_page(soup: BeautifulSoup = None, parsed_url: str = None,
                                              parent_url: str = None, userland_dict: dict = None) -> []:
    # Identify Propulsion systems table
    all_tables = soup.find_all('table')
    #   There should be only maximum of 4 columns (<td>'s in <tr>) in the table
    propulsion_system_tables = list(
        filter(max_four_column_table_filter_outside_quicklinks, all_tables))
    #   Assert that there's only such table
    assert len(propulsion_system_tables) == 1, "Invalid assumption: There is always one and only one table " \
                                               "with 4 columns for propulsion systems => {} " \
                                               "Found {}".format(parsed_url, len(
                                                   propulsion_system_tables))

    propulsion_system_table = propulsion_system_tables[0]
    # Extract lookup values and assign to class
    for html_key, class_attribute in PROPULSION_ATTRIBUTES_HTML_PUB5_MAPPING.items():
        if class_attribute is None:
            continue
        propulsion_system_table_data = propulsion_system_table.find(
            'td', text=html_key)
        if propulsion_system_table_data is not None:
            setattr(userland_dict['class'], class_attribute,
                    propulsion_system_table_data.find_next('td').text.strip())
        # Print attributes not found as per lookup
        else:
            print("TONAL ATTRIBUTE PARSE DISCREPANCY: {} not found as tonal attribute in {}".format(
                html_key, parsed_url))
    # TODO A generic attribute parser that can take an expression and assign
    #  (to handle cases where there are two values)
    # TODO Find all mappings and replace None attributes (possibly as part of #100)
