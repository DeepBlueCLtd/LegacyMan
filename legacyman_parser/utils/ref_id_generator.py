import re

valid_characters_pattern = re.compile('[^0-9a-z_-]+')


def get_ref_id_for_class(classu):
    # TODO: Introduce string shortening logic
    return (classu.country.country + "-"
            + classu.sub_category[0] + "-"
            + classu.class_u).lower() \
        .replace(" ", "_") \
        .replace("/", "-") \
        .replace("\\", "-") \
        .replace("(", "-") \
        .replace(")", "-") \
        .replace("&", "-")


def get_cleansed_ref_id_for_class(classu):
    ref_id = get_ref_id_for_class(classu)
    return re.sub(valid_characters_pattern, '', ref_id)
