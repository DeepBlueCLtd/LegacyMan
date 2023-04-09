import os
from urllib.parse import urljoin


TARGET_DIRECTORY = urljoin(os.getcwd()+"/", "target/")
JSON_EXPORT_FILE = urljoin(TARGET_DIRECTORY, "json_publication.js")
COPY_FLAGS_TO_DIRECTORY = urljoin(TARGET_DIRECTORY, "flags")
COPY_CLASS_IMAGES_TO_DIRECTORY = urljoin(TARGET_DIRECTORY, "class_images")
