from urllib.parse import urljoin

from bs4 import BeautifulSoup, PageElement

"""Independent unit testable parse_units module
to process unit data
"""
UNIT_COLLECTION = []

_class_table_header_is_identified = False
_current_subtype = None


class Unit:
    def __init__(self, unit, sub_category, country, power, has_tonal, tonal_href):
        self.unit = unit
        self.sub_category = sub_category
        self.country = country
        self.power = power
        self.has_tonal = has_tonal
        self.tonal_href = tonal_href

    def __str__(self):
        return "{} [{}] of {} is powered by {}{}".format(self.unit,
                                                         self.sub_category,
                                                         self.country,
                                                         self.power,
                                                         (". Tonal ==> " + self.tonal_href) if
                                                         self.has_tonal else "")


def extract_classes_of_country(soup: BeautifulSoup = None, parsed_url: str = None, parent_url: str = None,
                               userland_dict: dict = None) -> []:
    global _class_table_header_is_identified, _current_subtype
    _class_table_header_is_identified = False
    _current_subtype = None
    for row in soup.find('div', {"id": "PageLayer"}).find('table').find_all('tr'):
        process_class_row(row, userland_dict['country'], parsed_url)


def process_class_row(row: PageElement, country: str, parsed_url: str):
    """Check if not _class_table_header_is_identified"""
    global _class_table_header_is_identified, _current_subtype
    if not _class_table_header_is_identified:
        """See if this is the header, and set 
        _class_table_header_is_identified accordingly 
        and return"""
        _class_table_header_is_identified = is_this_class_header(row)
        return

    # Check if record is a subtype, as at this point table header is identified
    if is_this_subcategory_data(row):
        # Add to set and set _current_subtype flag and return
        _current_subtype = extract_subcategory(row)
        return

    # Normal record
    if not is_this_class_record(row):
        return
    # Extract information and map against _current_subtype
    create_new_unit_with_extracted_subcategory(row, country, _current_subtype, parsed_url)


def is_this_class_header(row: PageElement):
    """Identify the table header:
    first < tr > which contains < td > element with innerHTML
    as string literal "Class" as its first child/column heading."""
    header = row.find_all('td')
    # For fields that don't have table data, like sub-categories, descriptions etc
    if len(header) <= 0:
        return False
    if header[0].text == "Class":
        return True
    return False


def is_this_subcategory_data(row: PageElement):
    """Identify the `Sub-Category` header:
    first < tr > following table header will be the
    first `Sub-Category` < tr > which will have an optional
    < td > indicating the sub-category,
    say `SC1` or `Composite` or `Legacy`"""
    columns = row.find_all('td')
    if len(columns) <= 1:
        return True
    return False


def extract_subcategory(row: PageElement):
    """It might also have < strong > attribute"""
    columns = row.find_all('td')
    if len(columns) == 0:
        return row.text
    return columns[0].find('strong').text if columns[0].find('strong') is not None else columns[0].text


def is_this_class_record(row: PageElement):
    """ This should have more than one < td >"""
    columns = row.find_all('td')
    if len(columns) > 1:
        return True
    return False


def create_new_unit_with_extracted_subcategory(row: PageElement, country: str, current_subtype: str, parsed_url: str):
    columns = row.find_all('td')
    tonal_href = None
    has_tonal = does_class_contain_tonal(columns[0])
    if has_tonal:
        tonal_href = urljoin(parsed_url, extract_tonal_href(columns[0]))
    UNIT_COLLECTION.append(Unit(columns[0].text, current_subtype, country, columns[2].text, has_tonal, tonal_href))


def does_class_contain_tonal(table_data: PageElement):
    if table_data.find('a') is not None:
        return True
    return False


def extract_tonal_href(table_data: PageElement):
    return table_data.find('a').get('href')