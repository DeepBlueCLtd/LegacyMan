import os


def path_has_drive_component(path):
    if os.path.splitdrive(path)[0]:
        return True
    return False


TARGET_DIRECTORY = "target/" if not path_has_drive_component(os.getcwd()) \
    else os.path.splitdrive(os.getcwd())[0] + "//" + "target/"

JSON_EXPORT_FILE = TARGET_DIRECTORY + "json_publication.js"
COPY_FLAGS_TO_DIRECTORY = TARGET_DIRECTORY + "flags/"
COPY_CLASS_IMAGES_TO_DIRECTORY = TARGET_DIRECTORY + "class_images/"
