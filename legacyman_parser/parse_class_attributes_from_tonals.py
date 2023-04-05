from bs4 import BeautifulSoup

"""
Independent testable parse tonal class attributes
"""

"""
Property placement in tonals page:

Cruise Plant: 4 * PR32 Diesel Engines => Indexes: 1 and 2
Shaft x Blade: 2 * 4 (GRR) => Indexes: 3 and 4
Boost Plant: None => Indexes: 5 and 6
MTBF: 14hrs & 12 ltr/hr => Indexes: 7 and 8
BHP: 400 hrs => Indexes: 9 and 10
Reduction Ratio: 412.8:1 => Indexes: 11 and 12
Av Temp: ~14 => Indexes: 13 and 14
Max TRPM: 1400 => Indexes: 15 and 16
Max SRPM: 0-1600 => Indexes: 17 and 18
"""


def extract_class_attributes_from_tonals_page(soup: BeautifulSoup = None, parsed_url: str = None,
                                              parent_url: str = None, userland_dict: dict = None) -> []:
    # Find all tables on page
    all_tables = soup.find_all('table')

    def four_col_table_filter(tag):
        # Find first table data and its colspan
        tdata = tag.find('td')
        colspan = tdata.get('colspan')
        return colspan and colspan == '4'
    propulsion_system_tables = list(filter(four_col_table_filter, all_tables))
    assert len(propulsion_system_tables) == 1, "InvalidAssumption: There's always a Tonal Propulsion table with " \
        "colspan 4 => {}. Found {}".found(
            parsed_url, len(propulsion_system_tables))
    propulsion_system_table = propulsion_system_tables[0]
    assert len(propulsion_system_table) % 2 == 1, "InvalidAssumption: Propulsion table is in" \
                                                  " Key, Value format, with header : {}".format(
                                                      parsed_url)
    propulsion_system_table_data = propulsion_system_table.find_all('td')
    # Extracting class properties from tonals page
    userland_dict['class'].power = propulsion_system_table_data[2].text.strip()
    userland_dict['class'].shaft_blade = propulsion_system_table_data[4].text.strip()
    userland_dict['class'].bhp = propulsion_system_table_data[10].text.strip()
    userland_dict['class'].reduction_ratio = propulsion_system_table_data[12].text.strip()
    userland_dict['class'].av_temp = propulsion_system_table_data[14].text.strip()
