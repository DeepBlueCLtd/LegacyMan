import re

# Name to start with alphabet, and then should contain one
# or more of the following characters
# a to z
# 0 to 9
# - (hyphen)
# _ (underscore)
accepted_ref_id_pattern = re.compile(r"^[a-z][a-z0-9-_]+$")

classes_with_illegal_reference_id_characters = []


def get_ref_id_for_class(classu):
    # TODO: Introduce string shortening logic
    return (classu.country.country + ":"
            + classu.sub_category[0] + ":"
            + classu.class_u).lower().replace("-", "").replace(":", "-")


def get_audited_ref_id_for_class(classu):
    ref_id = get_ref_id_for_class(classu)
    if accepted_ref_id_pattern.match(ref_id) is None:
        classes_with_illegal_reference_id_characters.append(ref_id)
    return ref_id
