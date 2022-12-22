def phase_one_regions_parse_not_included_countries(published_json, test_payload):
    parsed_countries = list(map(lambda a: a.country, published_json['countries']))
    for to_be_excluded_countries in test_payload:
        if to_be_excluded_countries in parsed_countries:
            print('Error: {} found in list of phase 1 parsed countries'.format(to_be_excluded_countries))
            return False
    return True


def unit_of_subtype_of_country_should_contain_exactly_x_tonals_remarks_containing_y(published_json, test_payload):
    for unit_payload in test_payload:
        country_id_to_check = next(filter(lambda a: a.country == unit_payload['country'],
                                          published_json['countries'])).id
        subtype_id_to_check = next(filter(lambda a: a.platform_sub_type == unit_payload['sub'],
                                          published_json['platform_sub_types'])).id
        unit_id_to_check = next(filter(lambda a: a.title == unit_payload['unit'] and
                                                 a.platform_sub_type_id == subtype_id_to_check and
                                                 a.country_id == country_id_to_check,
                                       published_json['units'])).id
        tonals_to_check = filter(lambda a: a.unit_id == unit_id_to_check, published_json['tonals'])
        tonals_with_required_remarks = filter(lambda a: a.remarks.find(unit_payload['remarks_suffix']) >= 0,
                                              tonals_to_check)
        if len(list(tonals_with_required_remarks)) != unit_payload['count']:
            print('Error: {} failed to identify {} tonals with {} remarks suffix'.format(unit_payload,
                                                                                         unit_payload['count'],
                                                                                         unit_payload['remarks_suffix']))
            return False
    return True
