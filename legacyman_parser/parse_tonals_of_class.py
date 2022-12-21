from bs4 import BeautifulSoup, PageElement

"""Independent testable parse_tonals module
to process tonals data
"""
TONAL_COLLECTION = []
TONAL_TYPE_COLLECTION = {}
TONAL_SOURCE_COLLECTION = {}

TONAL_TABLE_NOT_FOUND = []
TONAL_HEADER_NOT_FOUND = []

_tonal_table_header_is_identified = False
_current_tonal_type = None

_current_merged_remarks = None
_no_of_rows_for_which_current_merged_remarks_is_applicable_now = 0


def decrement_and_possibly_reset_current_merged_remarks_flags():
    global _no_of_rows_for_which_current_merged_remarks_is_applicable_now, _current_merged_remarks

    # Decrement the applicable rows by one each time we consume the row
    _no_of_rows_for_which_current_merged_remarks_is_applicable_now -= 1

    if _no_of_rows_for_which_current_merged_remarks_is_applicable_now == 0:
        _current_merged_remarks = None


def set_current_merged_remarks_flags(applicable_rows: int, remarks: str):
    global _no_of_rows_for_which_current_merged_remarks_is_applicable_now, _current_merged_remarks

    _no_of_rows_for_which_current_merged_remarks_is_applicable_now = applicable_rows
    _current_merged_remarks = remarks


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
            TONAL_TABLE_NOT_FOUND.append(parsed_url)
    else:
        TONAL_HEADER_NOT_FOUND.append(parsed_url)


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

    # Some tonals have merged remarks
    if has_effective_number_of_columns(columns):
        return True

    return False


def has_effective_number_of_columns(columns: PageElement):
    if len(columns) == 3 and _no_of_rows_for_which_current_merged_remarks_is_applicable_now >= 1:
        return True
    return False


def create_new_tonal_with_extracted_tonal_type(row: PageElement, class_u: any, current_tonal_type: str):
    columns = row.find_all('td')
    tonal_source = identify_or_create_tonal_source_id(columns[0].text)

    current_remarks = None
    # Check if remarks exist
    if len(columns) == 4:
        # If exists, check if it's merged for subsequent rows and set _current_merged* flags
        current_remarks = columns[3].text
        if 'rowspan' in columns[3].attrs:
            set_current_merged_remarks_flags(int(columns[3]['rowspan']) - 1, current_remarks)
    else:
        # If it doesn't exist, fetch from _current_merged_remarks and call decrement function
        current_remarks = _current_merged_remarks
        decrement_and_possibly_reset_current_merged_remarks_flags()

    TONAL_COLLECTION.append(
        Tonal(class_u, tonal_source, columns[1].text, columns[2].text, current_remarks, current_tonal_type))


def identify_or_create_tonal_source_id(tonal_source: str):
    if tonal_source in TONAL_SOURCE_COLLECTION:
        return tonal_source, TONAL_SOURCE_COLLECTION[tonal_source]
    new_id = len(TONAL_SOURCE_COLLECTION) + 1
    TONAL_SOURCE_COLLECTION[tonal_source] = new_id
    return tonal_source, new_id
