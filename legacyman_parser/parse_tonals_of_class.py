from bs4 import BeautifulSoup, PageElement

"""Independent testable parse_tonals module
to process tonals data
"""
TONAL_COLLECTION = []
TONAL_TYPE_COLLECTION = {}

_tonal_table_header_is_identified = False
_current_tonal_type = None


class Tonal:
    def __init__(self, class_u, source, ratio_freq, harmonics, frequency, tonal_type):
        self.class_u = class_u
        self.source = source
        self.ratio_freq = ratio_freq
        self.harmonics = harmonics
        self.frequency = frequency
        self.tonal_type = tonal_type

    def __str__(self):
        return "    {} => [{}], [{}], [{}], [{}]".format(self.tonal_type,
                                                         self.source,
                                                         self.ratio_freq,
                                                         self.harmonics,
                                                         self.frequency)


def extract_tonals_of_class(soup: BeautifulSoup = None, parsed_url: str = None, parent_url: str = None,
                            userland_dict: dict = None) -> []:
    global _tonal_table_header_is_identified, _current_tonal_type
    _tonal_table_header_is_identified = False
    _current_tonal_type = None
    tonal_header = soup.find("td", string="Commonly Detected Sources")
    if tonal_header:
        tonal_table = tonal_header.find_parent("table")
        if tonal_table:
            for row in tonal_table.find_all('tr'):
                process_tonal_row(row, userland_dict['class'])
        else:
            print("Tonal table not found for", parsed_url)
    else:
        print("Tonal Header not found for", parsed_url)


def process_tonal_row(row: PageElement, class_u: any):
    """Check if not _tonal_table_header_is_identified"""
    global _tonal_table_header_is_identified, _current_tonal_type
    if not _tonal_table_header_is_identified:
        """See if this is the header, and set 
        _tonal_table_header_is_identified accordingly 
        and return"""
        _tonal_table_header_is_identified = is_this_tonal_header(row)
        return

    # Check if record is a tonal type, as at this point table header is identified
    if is_this_tonal_type_data(row):
        # Add to set and set _current_tonal_type flag and return
        _current_tonal_type = identify_or_create_tonal_type_id(extract_tonal_type(row))
        return

    # Normal record
    if not is_this_tonal_record(row):
        return
    # Extract information and map against _current_tonal_type
    create_new_tonal_with_extracted_tonal_type(row, class_u, _current_tonal_type)


def identify_or_create_tonal_type_id(tonal_type: str):
    if tonal_type in TONAL_TYPE_COLLECTION:
        return tonal_type, TONAL_TYPE_COLLECTION[tonal_type]
    new_id = len(TONAL_TYPE_COLLECTION) + 1
    TONAL_TYPE_COLLECTION[tonal_type] = new_id
    return tonal_type, new_id


def is_this_tonal_header(row: PageElement):
    """Identify the tonal header:
    first < tr > which contains < td > elements
    with innerHTML as string literals
    "Source", "Ratio/Freq",  "Harmonics", and
    "Remarks" in the same order."""
    header = row.find_all('td')
    # For fields that don't have tonal headers
    if len(header) != 4:
        return False
    if (header[0].text, header[3].text) == (
            "Source", "Remarks"):
        return True
    return False


def is_this_tonal_type_data(row: PageElement):
    """Identify the `Tonal-Type` header:
    first < tr > following tonal header will be the first `Tonal-Type` < tr >
    which might have optional < td > indicating the tonal-type,
    say `Power Related` or `Auxiliary Sources` or `Transient Sources`.
    It MAY also have < strong > attribute"""
    columns = row.find_all('td')
    if len(columns) <= 1:
        return True
    return False


def extract_tonal_type(row: PageElement):
    """It might also have < strong > attribute"""
    columns = row.find_all('td')
    if len(columns) == 0:
        return row.text
    return columns[0].find('strong').text if columns[0].find('strong') is not None else columns[0].text


def is_this_tonal_record(row: PageElement):
    """ This should have exactly 4 < td >"""
    columns = row.find_all('td')
    if len(columns) == 4:
        return True
    return False


def create_new_tonal_with_extracted_tonal_type(row: PageElement, class_u: any, current_tonal_type: str):
    columns = row.find_all('td')
    TONAL_COLLECTION.append(
        Tonal(class_u, columns[0].text, columns[1].text, columns[2].text, columns[3].text, current_tonal_type))
