from lman_parser import Parser
import sys
import logging
from parser_utils import delete_directory, copy_files
from pathlib import Path
import os
import time


def parse_single_file(root_path, file_path, target_path):
    logging.info(
        f"LegacyMan parser running, with these arguments: {root_path}, {file_path}, {target_path}"
    )

    # remove existing target directory and recreate it
    delete_directory(os.path.join(os.getcwd(), "target/dita"))
    delete_directory(os.path.join(os.getcwd(), "target/html"))
    os.makedirs("target", exist_ok=True)
    target_dir = os.path.join("target", "dita")

    # copy index.dita and welcome.dita from data dir to target/dita

    parser = Parser(Path(root_path).resolve(), Path(target_dir) / "regions")
    parser.only_process_single_file = True

    time1 = time.time()
    parser.write_generic_files = False
    parser.process_regions()
    time2 = time.time()
    logging.info("Done run 1")
    logging.info(f"Run 1 took {time2-time1:.2} seconds")

    parser.files_already_processed = set()
    parser.write_generic_files = True

    output_dita_filename = parser.process_generic_file(Path(file_path).resolve())
    time3 = time.time()
    logging.info("Done run 2 for single file")
    logging.info(f"Run 2 took {time3-time2:.2} seconds")

    parser.run_dita_command(output_dita_filename, run_validator=False)
    time4 = time.time()

    logging.info(f"Running DITA to HTML conversion took {time4-time3:.2} seconds")


if __name__ == "__main__":
    root_path = sys.argv[1]
    single_file_path = sys.argv[2]
    logging_format = "%(levelname)s:  %(message)s"
    if len(sys.argv) == 4:
        logging_level = sys.argv[3]
        if logging_level == "debug":
            logging.basicConfig(level=logging.DEBUG, format=logging_format)
            logging.info("Logging level set to DEBUG")
        elif logging_level == "info":
            logging.basicConfig(level=logging.INFO, format=logging_format)
            logging.info("Logging level set to INFO")
        elif logging_level == "warning":
            logging.basicConfig(level=logging.WARNING, format=logging_format)
            logging.info("Logging level set to WARNING")
    else:
        logging.basicConfig(level=logging.INFO, format=logging_format)
        logging.info("Logging level set to INFO")
    target_path = "./target/html"
    parse_single_file(root_path, single_file_path, target_path)
