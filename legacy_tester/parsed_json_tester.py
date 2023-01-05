import json

import legacy_tester.parsed_json_test_definitions as test_defs


def parsed_json_tester(published_json, test_payload):
    test_json = None
    with open(test_payload, 'r') as f:
        test_json = json.loads(f.read())

    if test_json is None:
        print("Payload is empty")
        return False

    for test_method, test_payload_val in test_json.items():
        test_method_val = getattr(test_defs, test_method, None)
        if test_method_val is None:
            print("Test definition for {} not found.".format(test_method))
            continue
        if not test_method_val(published_json, test_payload_val):
            print("Test {} failed.\nStopping further tests.".format(test_method))
            return False

    return True
