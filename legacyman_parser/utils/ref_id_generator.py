def get_ref_id_for_class(classu):
    # TODO: Introduce string shortening logic
    return (classu.country.country + ":"
            + classu.sub_category[0] + ":"
            + classu.class_u).lower().replace(" ", "")


tonal_map = {}


def tonal_with_seq(tonal_str):
    if tonal_str in tonal_map:
        tonal_map[tonal_str] = tonal_map[tonal_str] + 1
    else:
        tonal_map[tonal_str] = 1
    return tonal_str + ":" + str(tonal_map[tonal_str])


def get_ref_id_for_tonal(tonal):
    # TODO: Introduce string shortening logic
    return tonal_with_seq((tonal.class_u.country.country + ":"
                           + tonal.class_u.sub_category[0] + ":"
                           + tonal.class_u.class_u + ":"
                           + tonal.tonal_type[0] + ":"
                           + tonal.source[0]
                           ).lower().replace(" ", ""))
