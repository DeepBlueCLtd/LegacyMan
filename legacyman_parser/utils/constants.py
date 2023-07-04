import os
from urllib.parse import urljoin

TARGET_DIRECTORY = os.getcwd()+ "/target/"
JSON_EXPORT_FILE = TARGET_DIRECTORY + "data/publication.js"
COPY_FLAGS_TO_DIRECTORY = TARGET_DIRECTORY + "images/flags/"
COPY_CLASS_IMAGES_TO_DIRECTORY = TARGET_DIRECTORY + "images/class_images/"

## dita rxport
# regions.dita
DITA_REGIONS_EXPORT_FILE = TARGET_DIRECTORY + "dita/regions.dita"
