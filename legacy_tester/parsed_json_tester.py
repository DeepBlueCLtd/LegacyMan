import json

import legacy_tester.parsed_json_test_definitions as test_defs


def parsed_json_tester(published_json, test_payload):
    test_json = None
    with open(test_payload, 'r') as f:
        test_json = json.loads(f.read())

    if test_json is None:
        print("Payload is empty")
        return

    for test_method, test_payload in test_json.items():
        print("Testing {}".format(test_method))
        getattr(test_defs, test_method)(published_json, test_payload)
