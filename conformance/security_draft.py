#!/usr/bin/env python3
"""Independent draft schema checks. These are not native enforcement tests."""
import copy
import json
from pathlib import Path
from jsonschema import Draft202012Validator, ValidationError

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'examples/security-draft/.agents'
SCHEMAS = ROOT / 'spec/1.1-draft/schemas'
PATHS = {'manifest': 'manifest.json', 'permissions': 'permissions/permissions.json',
         'sandbox': 'sandbox/sandbox.json'}


def strict_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate key: ' + key)
        result[key] = value
    return result


def no_null(value):
    if value is None:
        raise ValueError('null is not allowed')
    if isinstance(value, dict):
        for item in value.values():
            no_null(item)
    if isinstance(value, list):
        for item in value:
            no_null(item)


def document(case):
    base = ROOT / 'examples' / case.get('example', 'security-draft') / '.agents'
    value = json.loads((base / PATHS[case['document']]).read_text())
    for change in case.get('changes', []):
        parent = value
        for key in change['path'][:-1]:
            parent = parent[key]
        key = change['path'][-1]
        if change.get('remove'):
            del parent[key]
        else:
            parent[key] = copy.deepcopy(change['value'])
    return case.get('raw', json.dumps(value))


def validate(raw, name):
    value = json.loads(raw, object_pairs_hook=strict_pairs)
    no_null(value)
    schema = json.loads((SCHEMAS / (name + '.schema.json')).read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)


def main():
    cases = json.loads((ROOT / 'conformance/security_cases.json').read_text())
    failed = []
    for case in cases:
        try:
            validate(document(case), case['document'])
            passed = True
        except (ValueError, ValidationError) as error:
            # jsonschema errors and strict JSON errors are validation failures.
            passed = False
            detail = str(error)
        if passed != case['valid']:
            failed.append(case['id'])
            print('FAIL', case['id'], 'accepted' if passed else detail)
    print(f'{len(cases) - len(failed)}/{len(cases)} draft schema cases passed')
    return bool(failed)


if __name__ == '__main__':
    raise SystemExit(main())
