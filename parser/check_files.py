from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Comment, Doctype
import random
import argparse


from parser_utils import sanitise_filename


def search_for_strings(html_soup, output):
    if type(html_soup) in (Comment, Doctype):
        return
    for element in html_soup.children:
        if type(element) is NavigableString:
            s = str(element).strip().replace("&", "&amp;")
            if s.startswith("Click the picture") or s.startswith("LIMIT OF THE PAGE"):
                continue
            if len(s) > 0:
                output.append(s)
        else:
            search_for_strings(element, output)


def select_random_text_from_file(path, n):
    html = Path(path).read_text()
    html_soup = BeautifulSoup(html, "html.parser")

    output = []
    search_for_strings(html_soup, output)

    output = list(filter(lambda x: len(x) > 40, output))

    if n == "all":
        return output
    else:
        if len(output) < int(n):
            return output

        return random.choices(output, k=int(n))


def check_file(source_path, source_root, target_root, text_n=10):
    text = select_random_text_from_file(source_path, n=text_n)

    target_path = (
        target_root / "dita" / "regions" / source_path.relative_to(source_root)
    ).with_suffix(".dita")
    target_path = Path(sanitise_filename(target_path))

    if not target_path.exists():
        print(
            f"#### ERROR: Couldn't find a target file at {target_path} for source file at {source_path}"
        )
        print()
        return

    target_content = target_path.read_text()

    for t in text:
        if t not in target_content:
            print(f"Couldn't find source text from {source_path} in target document {target_path}.")
            print(f"Source text:\n{t}\n")


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(usage="%(prog)s [OPTION] SOURCE_PATH TARGET_PATH")
    parser.add_argument("SOURCE_PATH", help="Path to the source data")
    parser.add_argument("TARGET_PATH", help="Path to the target (converted) data")
    parser.add_argument(
        "--files",
        default=5,
        help="Either an integer, to process that number of random files, or 'all' to process all files (default: 5)",
    )
    parser.add_argument(
        "--text",
        default=10,
        help="Either an integer, to read that number of random text strings from each file or 'all' to read all valid text strings from the file",
    )
    return parser


if __name__ == "__main__":
    parser = init_argparse()
    args = parser.parse_args()

    source_root = Path(args.SOURCE_PATH)
    target_root = Path(args.TARGET_PATH)

    print(f"Checking files with:")
    print(f"  source_path = {args.SOURCE_PATH}")
    print(f"  target_path = {args.TARGET_PATH}")
    print(f"  files = {args.files}")
    print(f"  text = {args.text}")
    print()

    all_html_files = list(source_root.rglob("*.html"))

    if args.files == "all":
        chosen_html_files = all_html_files
    else:
        chosen_html_files = random.choices(all_html_files, k=int(args.files))

    for filename in chosen_html_files:
        check_file(filename, source_root, target_root, text_n=args.text)
