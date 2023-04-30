import unittest

from bs4 import BeautifulSoup

from legacyman_parser.parse_abbreviations import parse_abbreviations, ABBREVIATIONS


def get_soup(html_input: str):
    return BeautifulSoup(html_input, "html.parser")


class TestParseAbbreviations(unittest.TestCase):

    def test_parse_abbreviations(self):
        print("\nAbbreviations should contain two entries: ", end="")
        ABBREVIATIONS.clear()
        soup = get_soup("""<div>
                                <table>
                                    <tr>
                                        <td>Key1</td>
                                        <td>Value1</td>
                                        <td>Key2</td>
                                        <td>Value2</td>
                                    </tr>
                                </table>
                                <table>
                                    <tr>
                                        <td>Quicklinks</td>
                                        <td>QuickReferences</td>
                                    </tr>
                                </table>
                            </div>""")
        parse_abbreviations(soup, None, None, None)
        self.assertEqual(len(ABBREVIATIONS), 2)


if __name__ == '__main__':
    unittest.main()
