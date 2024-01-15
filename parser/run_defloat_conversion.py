from lman_parser import Parser
from pathlib import Path
from bs4 import BeautifulSoup

p = Parser("", "")

# input_file_path = Path("data/Britain_Cmplx/unit_a28.html")
# input_file_path = Path("data/France1/FR_A27_Unit.html")
input_file_path = Path("data/Fr_Legacy/FR_100_unit_charlie.html")
html = input_file_path.read_text()
html_soup = BeautifulSoup(html, "html.parser")

# NEW
# Deal with the floating tables/images in this document by putting them in the correct chunk of whitespace
new_html = p.process_floating_parts(html_soup, input_file_path)
with open("test_converted_output.html", "w") as f:
    f.write(str(new_html))
