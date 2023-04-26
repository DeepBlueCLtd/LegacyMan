import unittest

from bs4 import BeautifulSoup

from legacyman_parser.parse_classes_of_country import CLASS_COLLECTION, extract_classes_of_country
from legacyman_parser.utils.parse_merged_rows import MergedRowsExtractor


def get_soup(html_input: str):
    return BeautifulSoup(html_input, "html.parser")


class TestParseClassesOfCountry(unittest.TestCase):
    def test_extraction_of_merged_class_properties(self):
        class_row_extractor = MergedRowsExtractor(7)
        country_dict = {"country": "country",
                        "class_extractor": class_row_extractor}
        CLASS_COLLECTION.clear()
        soup = get_soup("""
<div id="PageLayer">
        <div>
            <table border="1">
                <tr>
                    <td>Overview of systems in France</td>
                </tr>
                <tr>
                    <td>Class</td>
                    <td>Designator</td>
                    <td>Power</td>
                    <td>Shaft x Blade</td>
                    <td>Max Speed</td>
                    <td >Av TPK</td>
                    <td>Reduction Ratio</td>
                </tr>
                <tr>
                    <td colspan="7" bgcolor="#CCCCCC"><div align="center"><strong>Composite</strong></div></td>
                </tr>
                <tr>
                    <td><a href="../France_Composites/unit_a.html"> Unit_a</a></td>
                    <td>PB</td>
                    <td>2 * V8 Diesel</td>
                    <td>3 x 3</td>
                    <td>34 Kts</td>
                    <td>Unk</td>
                    <td>Unk</td>
                </tr>
                <tr>
                    <td>Unit_b</td>
                    <td>PBF</td>
                    <td>2 * V6 Diesel</td>
                    <td>2 * 4 (FPP)</td>
                    <td>16.6</td>
                    <td>Est 1000</td>
                    <td>BWW</td>
                </tr>
                <tr>
                    <td colspan="7" bgcolor="#CCCCCC"><div align="center"><strong>Legacy</strong></div></td>
                </tr>
                <tr>
                    <td>Unit_c</td>
                    <td>PBA</td>
                    <td rowspan="3">5 * V8 Diesel%TEST-85%</td>
                    <td>1 x 3</td>
                    <td>34 Kts</td>
                    <td>JR</td>
                    <td rowspan="2">Unk%TEST-85%</td>
                </tr>
                <tr>
                    <td><a href="../France_Legacy/unit_d.html">Unit_d</a></td>
                    <td>PBF</td>
                    <td rowspan="2">2 * 4 (FPP)%TEST-85%</td>
                    <td>16.6</td>
                    <td>Est 1000</td>
                </tr>
                <tr>
                    <td>Unit_eww</td>
                    <td>PBF</td>
                    <td>16.6</td>
                    <td>Est 1000</td>
                    <td>BWW</td>
                </tr>
            </table>
        </div>
    </div>
""")
        extract_classes_of_country(soup, None, None, country_dict)
        print("\nExtract classes with merged properties 1 - There should be 5 classes: ", end="")
        self.assertEqual(len(CLASS_COLLECTION), 5)
        print("\nExtract classes with merged properties 1 - There should be 3 v8 diesel TEST 85: ", end="")
        self.assertEqual(
            len(list(filter(lambda a: '%TEST-85%' in a.power, CLASS_COLLECTION))), 3)
        print("\nExtract classes with merged properties 1 - There should be 2 Unk%TEST-85%: ", end="")
        self.assertEqual(len(
            list(filter(lambda a: '%TEST-85%' in a.reduction_ratio, CLASS_COLLECTION))), 2)

    def test_extraction_of_unmerged_class_properties(self):
        class_row_extractor = MergedRowsExtractor(7)
        country_dict = {"country": "country",
                        "class_extractor": class_row_extractor}
        CLASS_COLLECTION.clear()
        soup = get_soup("""
<div id="PageLayer">
        <div>
            <table border="1">
                <tr>
                    <td>Overview of systems in France</td>
                </tr>
                <tr>
                    <td>Class</td>
                    <td>Designator</td>
                    <td>Power</td>
                    <td>Shaft x Blade</td>
                    <td>Max Speed</td>
                    <td >Av TPK</td>
                    <td>Reduction Ratio</td>
                </tr>
                <tr>
                    <td colspan="7" bgcolor="#CCCCCC"><div align="center"><strong>Composite</strong></div></td>
                </tr>
                <tr>
                    <td><a href="../France_Composites/unit_a.html"> Unit_a</a></td>
                    <td>PB</td>
                    <td>2 * V8 Diesel</td>
                    <td>3 x 3</td>
                    <td>34 Kts</td>
                    <td>Unk</td>
                    <td>Unk</td>
                </tr>
            </table>
        </div>
    </div>
""")
        extract_classes_of_country(soup, None, None, country_dict)
        print("\nExtract classes with unmerged properties 1 - There should be 1 class: ", end="")

    def test_extraction_of_classes_not_under_pagelayer(self):
        class_row_extractor = MergedRowsExtractor(7)
        country_dict = {"country": "country",
                        "class_extractor": class_row_extractor}
        CLASS_COLLECTION.clear()
        soup = get_soup("""
<div id="dd">
        <div>
            <table border="1">
                <tr>
                    <td>Overview of systems in France</td>
                </tr>
                <tr>
                    <td>Class</td>
                    <td>Designator</td>
                    <td>Power</td>
                    <td>Shaft x Blade</td>
                    <td>Max Speed</td>
                    <td >Av TPK</td>
                    <td>Reduction Ratio</td>
                </tr>
                <tr>
                    <td colspan="7" bgcolor="#CCCCCC"><div align="center"><strong>Composite</strong></div></td>
                </tr>
                <tr>
                    <td><a href="../France_Composites/unit_a.html"> Unit_a</a></td>
                    <td>PB</td>
                    <td>2 * V8 Diesel</td>
                    <td>3 x 3</td>
                    <td>34 Kts</td>
                    <td>Unk</td>
                    <td>Unk</td>
                </tr>
            </table>
        </div>
    </div>
""")
        extract_classes_of_country(soup, None, None, country_dict)
        print("\nExtract classes not under page layer - There should not be any class: ", end="")


if __name__ == '__main__':
    unittest.main()
