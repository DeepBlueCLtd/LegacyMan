from urllib.parse import urljoin

from bs4 import BeautifulSoup, PageElement

from crawler.simple_crawler import SimpleCrawler
from legacyman_parser.parse_classes_of_country import ClassU

"""Independent testable parse_classes module
to process class data from non-standard countries
"""
NS_CLASS_COLLECTION = []
NS_SUBTYPE_COLLECTION = {}
NS_NON_STANDARD_COUNTRY = []
NS_TOO_FEW_PROPERTIES = []
NS_CLASS_FOUND_FOR_COUNTRY = {}

_class_table_header_is_identified = False
_current_subtype_id = None

ns_classRowExtractor = None


def extract_classes_of_ns_country(soup: BeautifulSoup = None, parsed_url: str = None, parent_url: str = None,
                                  userland_dict: dict = None) -> []:
    global _class_table_header_is_identified, _current_subtype_id, ns_classRowExtractor
    _class_table_header_is_identified = False
    _current_subtype_id = None
    ns_classRowExtractor = userland_dict.get('class_extractor')
    class_h1 = soup.find_all('h1')
    assert len(class_h1) == 1, "InvalidAssumption: Each ns country page contains only 1 h1 header"
    class_subtypes_list = class_h1[0].find_next_siblings('div')
    assert len(class_subtypes_list) >= 1, "InvalidAssumption: Each ns class listing has one or more entries"
    for ns_sub_type in class_subtypes_list:
        sub_type_url = urljoin(parsed_url, ns_sub_type.find('a')['href'])
        ns_country_spidey_to_extract_classes = SimpleCrawler(url=sub_type_url,
                                                             disable_crawler_log=False,
                                                             userland_dict=userland_dict)
        ns_country_spidey_to_extract_classes.crawl(resource_processor_callback=extract_classes_of_subtype_of_ns_country,
                                                   crawl_recursively=False,
                                                   parent_url=parsed_url)


def extract_classes_of_subtype_of_ns_country(soup: BeautifulSoup = None, parsed_url: str = None, parent_url: str = None,
                                             userland_dict: dict = None) -> []:
    global _class_table_header_is_identified, _current_subtype_id, ns_classRowExtractor
    _class_table_header_is_identified = False
    _current_subtype_id = None
    ns_classRowExtractor = userland_dict.get('class_extractor')
    class_list_all = soup.find_all('div', {"id": "PageLayer"})
    assert len(class_list_all) == 1, "InvalidAssumption: Each country page contains only 1 PageLayer div" \
                                     " that lists classes."
    class_list = class_list_all[0]
    if class_list:
        table_list = class_list.find_all('table')
        assert len(table_list) == 1, "InvalidAssumption: PageLayer div contains only 1 table of classes"
        for row in table_list[0].find_all('tr'):
            process_class_row(row, userland_dict['country'], parsed_url)
    else:
        NS_NON_STANDARD_COUNTRY.append(parsed_url)
    assert _class_table_header_is_identified, "InvalidAssumption: Class Table will mandatorily have table header with " \
                                              "its first column header as text Class (case sensitive)"
    assert NS_CLASS_FOUND_FOR_COUNTRY.get(userland_dict['country'], False), "InvalidAssumption: Country ({}) page will " \
                                                                            "have at least one class." \
        .format(userland_dict['country'])


def process_class_row(row: PageElement, country: dict, parsed_url: str):
    """Check if not _class_table_header_is_identified"""
    global _class_table_header_is_identified, _current_subtype_id
    if not _class_table_header_is_identified:
        """See if this is the header, and set 
        _class_table_header_is_identified accordingly 
        and return"""
        _class_table_header_is_identified = is_this_class_header(row)
        return

    # Check if record is a subtype, as at this point table header is identified
    if is_this_subcategory_data(row):
        # Add to set and set _current_subtype_id flag and return
        _current_subtype_id = identify_or_create_sub_type_id(extract_subcategory(row))
        return

    # Normal record
    if not is_this_class_record(row):
        log_row_as_containing_too_few_class_properties(parsed_url)
        return
    # Extract information and map against _current_subtype_id
    create_new_class_with_extracted_subcategory(row, country, _current_subtype_id, parsed_url)


def identify_or_create_sub_type_id(sub_type: str):
    if sub_type in NS_SUBTYPE_COLLECTION:
        return sub_type, NS_SUBTYPE_COLLECTION[sub_type]
    new_id = len(NS_SUBTYPE_COLLECTION) + 1
    NS_SUBTYPE_COLLECTION[sub_type] = new_id
    return sub_type, new_id


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
    if len(columns) != 1:
        return False
    colspan_val = columns[0].get('colspan', 0)
    if int(colspan_val) != 7:
        return False
    bgcolor_val = columns[0].get('bgcolor', "")
    if bgcolor_val != "#CCCCCC":
        return False
    return True


def extract_subcategory(row: PageElement):
    """It might also have < strong > attribute"""
    columns = row.find_all('td')
    if len(columns) == 0:
        return row.text
    return columns[0].find('strong').text if columns[0].find('strong') is not None else columns[0].text


def is_this_class_record(row: PageElement):
    """ This should have more than one < td >"""
    columns = row.find_all('td')
    if len(columns) == 7:
        return True
    if ns_classRowExtractor.effective_length_of(columns) == 7:
        return True
    return False


def create_new_class_with_extracted_subcategory(row: PageElement, country: dict, current_subtype: str,
                                                parsed_url: str):
    columns = row.find_all('td')
    tonal_href = None
    has_tonal = does_class_contain_tonal(columns[0])
    if has_tonal:
        tonal_href = urljoin(parsed_url, extract_tonal_href(columns[0]))
    # Declare contents of a class
    class_name, designator, power, shaft, bhp, temp, rr = ns_classRowExtractor.retrieve_row(columns)

    seq = len(NS_CLASS_COLLECTION) + 1
    NS_CLASS_COLLECTION.append(ClassU(seq,
                                      class_name,
                                      current_subtype,
                                      country,
                                      designator,
                                      power,
                                      shaft,
                                      bhp,
                                      temp,
                                      rr,
                                      has_tonal,
                                      tonal_href))
    NS_CLASS_FOUND_FOR_COUNTRY[country] = True


def does_class_contain_tonal(table_data: PageElement):
    if table_data.find('a') is not None:
        return True
    return False


def extract_tonal_href(table_data: PageElement):
    return table_data.find('a').get('href')


def log_row_as_containing_too_few_class_properties(parsed_url: str):
    NS_TOO_FEW_PROPERTIES.append(parsed_url)
