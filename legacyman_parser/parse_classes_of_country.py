from urllib.parse import urljoin

from bs4 import BeautifulSoup, PageElement

"""Independent testable parse_classes module
to process class data
"""
CLASS_COLLECTION = []
SUBTYPE_COLLECTION = {}
NON_STANDARD_COUNTRY = []
TOO_FEW_PROPERTIES = []

_class_table_header_is_identified = False
_current_subtype_id = None

classRowExtractor = None


class ClassU:
    def __init__(self,
                 id,
                 class_u,
                 sub_category,
                 country,
                 designator,
                 power,
                 shaft_blade,
                 bhp,
                 av_temp,
                 reduction_ratio,
                 has_tonal,
                 tonal_href):
        self.id = id
        self.class_u = class_u
        self.sub_category = sub_category
        self.country = country
        self.designator = designator
        self.power = power
        self.shaft_blade = shaft_blade
        self.bhp = bhp
        self.av_temp = av_temp
        self.reduction_ratio = reduction_ratio
        self.has_tonal = has_tonal
        self.tonal_href = tonal_href

    def __str__(self):
        return "{} [{}] of {} is powered by {} " \
               "and has {}, {}, {}, {}, and {}{}".format(self.class_u,
                                                         self.sub_category,
                                                         self.country,
                                                         self.power,
                                                         self.designator,
                                                         self.shaft_blade,
                                                         self.bhp,
                                                         self.av_temp,
                                                         self.reduction_ratio,
                                                         (". Tonal ==> " + self.tonal_href) if
                                                         self.has_tonal else "")


def extract_classes_of_country(soup: BeautifulSoup = None, parsed_url: str = None, parent_url: str = None,
                               userland_dict: dict = None) -> []:
    global _class_table_header_is_identified, _current_subtype_id, classRowExtractor
    _class_table_header_is_identified = False
    _current_subtype_id = None
    classRowExtractor = userland_dict.get('class_extractor')
    class_list = soup.find('div', {"id": "PageLayer"})
    if class_list:
        for row in class_list.find('table').find_all('tr'):
            process_class_row(row, userland_dict['country'], parsed_url)
    else:
        NON_STANDARD_COUNTRY.append(parsed_url)


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
    if sub_type in SUBTYPE_COLLECTION:
        return sub_type, SUBTYPE_COLLECTION[sub_type]
    new_id = len(SUBTYPE_COLLECTION) + 1
    SUBTYPE_COLLECTION[sub_type] = new_id
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
    if classRowExtractor.effective_length_of(columns) == 7:
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
    class_name, designator, power, shaft, bhp, temp, rr = classRowExtractor.retrieve_row(columns)

    seq = len(CLASS_COLLECTION) + 1
    CLASS_COLLECTION.append(ClassU(seq,
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


def does_class_contain_tonal(table_data: PageElement):
    if table_data.find('a') is not None:
        return True
    return False


def extract_tonal_href(table_data: PageElement):
    return table_data.find('a').get('href')


def log_row_as_containing_too_few_class_properties(parsed_url: str):
    TOO_FEW_PROPERTIES.append(parsed_url)
