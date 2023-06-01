import re

valid_characters_pattern = re.compile('[^0-9a-z_-]+')
squash_repeated_underscores = re.compile('_+')
squash_repeated_hyphens = re.compile('-+')


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
    ref_id = re.sub(squash_repeated_underscores, '_', get_ref_id_for_class(classu))
    ref_id = re.sub(squash_repeated_hyphens, '-', ref_id)
    return re.sub(valid_characters_pattern, '', ref_id)
