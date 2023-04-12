from urllib.parse import urljoin

from bs4 import BeautifulSoup, PageElement

from crawler.simple_crawler import SimpleCrawler
from legacyman_parser.utils.class_html_template import ClassU


class ClassParser:

    def __init__(self, seq_start):
        self.CLASS_COLLECTION = []
        self.SUBTYPE_COLLECTION = {}
        self.NON_STANDARD_COUNTRY = []
        self.TOO_FEW_PROPERTIES = []
        self.CLASS_FOUND_FOR_COUNTRY = {}
        self._class_table_header_is_identified = False
        self._current_subtype_id = None
        self.classRowExtractor = None
        self.seq = seq_start

    def extract_classes_of_ns_country(self, soup: BeautifulSoup = None, parsed_url: str = None,
                                      parent_url: str = None,
                                      userland_dict: dict = None) -> []:
        self._class_table_header_is_identified = False
        self._current_subtype_id = None
        self.classRowExtractor = userland_dict.get('class_extractor')

        links = soup.find_all('a')

        def has_img_child_filter(tag):
            # filter for links that have image child
            return tag.find('img')

        def src_is_parent_folder_filter(tag):
            # filter for links that start with parent folder
            href = tag.get('href')
            return href.startswith('../')

        def src_is_correct_folder_type_filter(tag):
            # filter for links with relevant folder
            href = tag.get('href')
            bad_titles = ['quicklinksdata', 'platformdata', '_noise']
            return not any([x in href.lower() for x in bad_titles])

        has_img_child = list(filter(has_img_child_filter, links))
        src_is_parent_folder = list(
            filter(src_is_parent_folder_filter, has_img_child))
        class_subtypes_list = list(
            filter(src_is_correct_folder_type_filter, src_is_parent_folder))

        assert len(class_subtypes_list) >= 1, "InvalidAssumption: Each ns class listing has one or more entries => {} Found {}".format(
            parsed_url, len(class_subtypes_list))
        for ns_sub_type in class_subtypes_list:
            sub_type_url = urljoin(parsed_url, ns_sub_type.get('href'))
            ns_country_spidey_to_extract_classes = SimpleCrawler(url=sub_type_url,
                                                                 disable_crawler_log=False,
                                                                 userland_dict=userland_dict)
            ns_country_spidey_to_extract_classes.crawl(
                resource_processor_callback=self.extract_classes_of_subtype_of_ns_country,
                crawl_recursively=False,
                parent_url=parsed_url)

    def extract_classes_of_subtype_of_ns_country(self, soup: BeautifulSoup = None, parsed_url: str = None,
                                                 parent_url: str = None,
                                                 userland_dict: dict = None) -> []:
        self._class_table_header_is_identified = False
        self._current_subtype_id = None

        headings = soup.find_all('h2')
        assert len(headings) == 1, "InvalidAssumption: Each country page contains only one h2. => {} Found {}".format(
            parsed_url, len(headings))

        self._current_subtype_id = self.create_sub_type_id_of_ns_class(headings[0].contents[0],
                                                                       userland_dict.get('country').country, parsed_url)

        # now find the table of classes
        tables = soup.find_all('table')

        def has_correct_first_row_filter(tag):
            # filter for tables with more than one row, that is a colspan 7
            rows = tag.find_all('tr')
            assert len(rows) > 0, "InvalidAssumption: Table has more than one row => {}".format(
                parsed_url)
            first_row = rows[0]
            cells = first_row.find_all('td')
            if len(cells) == 1:
                colspan = cells[0].get('colspan')
                return colspan and colspan == "7"
            else:
                return False

        class_tables = list(filter(has_correct_first_row_filter, tables))

        # note: it is acceptable for zero class tables to be found, since one legitimate class table has 8 cols.  We
        # don't (yet) support it, but the code shouldn't fail.
        assert len(class_tables) <= 1, "InvalidAssumption: Should just have found one table of classes => {} Found: {}".format(
            parsed_url, len(class_tables))

        if len(class_tables) == 1:
            rows = class_tables[0].find_all('tr')

            for row in rows[1:]:
                self.process_class_row(
                    row, userland_dict['country'], parsed_url)
            else:
                self.NON_STANDARD_COUNTRY.append(parsed_url)
            assert self._class_table_header_is_identified, "InvalidAssumption: Class Table will mandatorily have table header with its first column header as text Class (case sensitive) => {}".format(
                parsed_url)
            assert self.CLASS_FOUND_FOR_COUNTRY.get(userland_dict['country'],
                                                    False), "InvalidAssumption: Country ({}) page will have at least one class. => {}".format(userland_dict['country'], parsed_url)

    def extract_classes_of_country(self, soup: BeautifulSoup = None, parsed_url: str = None, parent_url: str = None,
                                   userland_dict: dict = None) -> []:
        self._class_table_header_is_identified = False
        self._current_subtype_id = None
        self.classRowExtractor = userland_dict.get('class_extractor')
        class_list_all = soup.find_all('div', {"id": "PageLayer"})
        assert len(
            class_list_all) == 1, "InvalidAssumption: Each country page contains only 1 PageLayer div that lists classes. => {}. Found {}".format(
            parsed_url, len(class_list_all))
        class_list = class_list_all[0]
        if class_list:
            table_list = class_list.find_all('table')
            assert len(table_list) == 1, "InvalidAssumption: PageLayer div contains only 1 table of classes => {}. Found {}".format(
                parsed_url, len(table_list))
            for row in table_list[0].find_all('tr'):
                self.process_class_row(
                    row, userland_dict['country'], parsed_url)
        else:
            self.NON_STANDARD_COUNTRY.append(parsed_url)
        assert self._class_table_header_is_identified, "InvalidAssumption: Class Table will mandatorily have " \
                                                       "table header with its first column header as text " \
                                                       "Class (case sensitive) => {}".format(
                                                           parsed_url)
        assert self.CLASS_FOUND_FOR_COUNTRY.get(userland_dict['country'],
                                                False), "InvalidAssumption: Country ({}) page will " \
                                                        "have at least one class. => {}" \
            .format(userland_dict['country'], parsed_url)

    def process_class_row(self, row: PageElement, country: dict, parsed_url: str):
        """Check if not _class_table_header_is_identified"""
        if not self._class_table_header_is_identified:
            """See if this is the header, and set
            _class_table_header_is_identified accordingly
            and return"""
            self._class_table_header_is_identified = self.is_this_class_header(
                row)
            return

        # Check if record is a subtype, as at this point table header is identified
        if self.is_this_subcategory_data(row):
            # Add to set and set _current_subtype_id flag and return
            self._current_subtype_id = self.identify_or_create_sub_type_id(
                self.extract_subcategory(row))
            return

        # Normal record
        if not self.is_this_class_record(row):
            self.log_row_as_containing_too_few_class_properties(parsed_url)
            return
        # Extract information and map against _current_subtype_id
        self.create_new_class_with_extracted_subcategory(
            row, country, self._current_subtype_id, parsed_url)

    def identify_or_create_sub_type_id(self, sub_type_str: str):
        sub_type = sub_type_str.replace('/', '-')
        if sub_type in self.SUBTYPE_COLLECTION:
            return sub_type, self.SUBTYPE_COLLECTION[sub_type]
        new_id = len(self.SUBTYPE_COLLECTION) + 1
        self.SUBTYPE_COLLECTION[sub_type] = new_id
        return sub_type, new_id

    def create_sub_type_id_of_ns_class(self, sub_type_str: str, country, parsed_url):
        # note: the sub_type_str is expected to look like `Britain - Composites`
        parts = sub_type_str.replace('/', '-').split(' - ')
        assert len(
            parts) == 2, "InvalidAssumption: h2 contains two elements, separated by '-' => {}. Found {}".format(parsed_url, parts)
        sub_type = parts[1].strip()
        if sub_type in self.SUBTYPE_COLLECTION:
            return sub_type, self.SUBTYPE_COLLECTION[sub_type]
        new_id = len(self.SUBTYPE_COLLECTION) + 1
        self.SUBTYPE_COLLECTION[sub_type] = new_id
        return sub_type, new_id

    @ staticmethod
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

    @ staticmethod
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

    @ staticmethod
    def extract_subcategory(row: PageElement):
        """It might also have < strong > attribute"""
        columns = row.find_all('td')
        if len(columns) == 0:
            return row.text
        return columns[0].find('strong').text if columns[0].find('strong') is not None else columns[0].text

    def is_this_class_record(self, row: PageElement):
        """ This should have more than one < td >"""
        columns = row.find_all('td')
        if len(columns) == 7:
            return True
        if self.classRowExtractor.effective_length_of(columns) == 7:
            return True
        return False

    def create_new_class_with_extracted_subcategory(self, row: PageElement, country: dict, current_subtype: str,
                                                    parsed_url: str):
        columns = row.find_all('td')
        tonal_href = None
        has_link = self.does_have_a_link(columns[0])
        if has_link:
            tonal_href = urljoin(
                parsed_url, self.extract_tonal_href(columns[0]))
        # Declare contents of a class
        class_name, designator, power, shaft, bhp, temp, rr = self.classRowExtractor.retrieve_row(
            columns)

        self.seq = self.seq + 1
        self.CLASS_COLLECTION.append(ClassU(self.seq,
                                            class_name,
                                            current_subtype,
                                            country,
                                            designator,
                                            power,
                                            shaft,
                                            bhp,
                                            temp,
                                            rr,
                                            has_link,
                                            tonal_href))
        self.CLASS_FOUND_FOR_COUNTRY[country] = True

    @ staticmethod
    def does_have_a_link(table_data: PageElement):
        link = table_data.find('a')
        if link is not None:
            href = link.get('href')
            if href is not None:
                return True
        return False

    @ staticmethod
    def extract_tonal_href(table_data: PageElement):
        return table_data.find('a').get('href')

    def log_row_as_containing_too_few_class_properties(self, parsed_url: str):
        self.TOO_FEW_PROPERTIES.append(parsed_url)
