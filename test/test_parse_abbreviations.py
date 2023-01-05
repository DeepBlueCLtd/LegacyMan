import unittest

from bs4 import BeautifulSoup

from legacyman_parser.parse_abbreviations import parse_abbreviations, ABBREVIATIONS


def get_soup(html_input: str):
    return BeautifulSoup(html_input, "html.parser")


class TestParseRegions(unittest.TestCase):

    def test_parse_abbreviations(self):
        print("\nAbbreviations should contain only one entry: ", end="")
        ABBREVIATIONS.clear()
        soup = get_soup("""<table><tr><td>Key</td><td>Value</td></tr></table>""")
        parse_abbreviations(soup, None, None, None)
        self.assertEqual(len(ABBREVIATIONS), 1)


if __name__ == '__main__':
    unittest.main()
