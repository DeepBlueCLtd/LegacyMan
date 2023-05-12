import re

tonal_map = {}
# Name to start with alphabet, and then should contain one
# or more of the following characters
# a to z
# 0 to 9
# - (hyphen)
# _ (underscore)
accepted_ref_id_pattern = re.compile(r"^[a-z][a-z0-9-_]+$")

classes_with_illegal_reference_id_characters = []
tonals_with_illegal_reference_id_characters = []


def get_ref_id_for_class(classu):
    # TODO: Introduce string shortening logic
    return (classu.country.country + ":"
            + classu.sub_category[0] + ":"
            + classu.class_u).lower().replace(" ", "").replace("-", "").replace(":", "-")


def get_ref_id_for_tonal(tonal):
    # TODO: Introduce string shortening logic
    return tonal_with_seq((tonal.class_u.country.country + ":"
                           + tonal.class_u.sub_category[0] + ":"
                           + tonal.class_u.class_u + ":"
                           + tonal.tonal_type[0] + ":"
                           + tonal.source[0]
                           ).lower().replace(" ", "")).replace("-", "").replace(":", "-")


def tonal_with_seq(tonal_str):
    if tonal_str in tonal_map:
        tonal_map[tonal_str] = tonal_map[tonal_str] + 1
    else:
        tonal_map[tonal_str] = 1
    return tonal_str + ":" + str(tonal_map[tonal_str])


def get_audited_ref_id_for_class(classu):
    ref_id = get_ref_id_for_class(classu)
    if accepted_ref_id_pattern.match(ref_id) is None:
        classes_with_illegal_reference_id_characters.append(ref_id)
    return ref_id


def get_audited_ref_id_for_tonal(tonal):
    ref_id = get_ref_id_for_tonal(tonal)
    if accepted_ref_id_pattern.match(ref_id) is None:
        tonals_with_illegal_reference_id_characters.append(ref_id)
    return ref_id
