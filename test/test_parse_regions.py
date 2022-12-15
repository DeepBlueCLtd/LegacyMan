import unittest

from bs4 import BeautifulSoup

from legacyman_parser.parse_regions import extract_regions, REGION_COLLECTION


def get_soup(html_input: str):
    return BeautifulSoup(html_input, "html.parser")


class TestParseRegions(unittest.TestCase):

    def test_parse_region_all_valid_countries(self):
        print("\nCountries containing no .. at the start: ", end="")
        REGION_COLLECTION.clear()
        soup = get_soup("""<area href="Britain/Britain1.html" />""")
        extract_regions(soup, None, None, None)
        self.assertEqual(len(REGION_COLLECTION), 1)

    def test_parse_region_no_valid_countries(self):
        print("\nCountries containing .. at the start: ", end="")
        REGION_COLLECTION.clear()
        soup = get_soup("""<area href="../Britain/Britain1.html" />""")
        extract_regions(soup, None, None, None)
        self.assertEqual(len(REGION_COLLECTION), 0)

    def test_parse_region_some_valid_countries(self):
        print("\nMix of countries starting and not starting with .. as href: ", end="")
        REGION_COLLECTION.clear()
        soup = get_soup("""<area href="../Britain/Britain1.html" />
                           <area href="Britain/Britain1.html" />""")
        extract_regions(soup, None, None, None)
        self.assertEqual(len(REGION_COLLECTION), 1)


if __name__ == '__main__':
    unittest.main()
