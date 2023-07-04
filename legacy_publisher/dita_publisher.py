import json
import random
from xml.dom import minidom

from legacyman_parser.utils.constants import DITA_REGIONS_EXPORT_FILE
from legacyman_parser.dita.create_regions import create_regions_dita

"""This module will handle post parsing enhancements for DITA publishing"""
DITA_EXPORT_FILE = DITA_REGIONS_EXPORT_FILE

random.seed(100)

def publish_regions(parsed_regions=None):
    # publish regions data
    create_regions_dita(DITA_EXPORT_FILE, parsed_regions)
