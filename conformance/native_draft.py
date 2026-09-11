#!/usr/bin/env python3
"""Validate the separate draft.2 schema and negative native metadata cases."""
import copy
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / 'spec/1.1-draft.2/schemas'
BASE = ROOT / 'examples/native-draft/.agents'


def main():
    for path in SCHEMAS.glob('*.json'):
        Draft202012Validator.check_schema(json.loads(path.read_text()))
    manifest = json.loads((BASE / 'manifest.json').read_text())
    profile = json.loads((BASE / 'native/com.openai.codex/profile.json').read_text())
    validators = {name: Draft202012Validator(json.loads((SCHEMAS / (name + '.schema.json')).read_text())) for name in ('manifest', 'native')}
    cases = [('manifest', manifest, True), ('native', profile, True)]
    instructions = ROOT / 'examples/native-agent-instructions/.agents'
    cases.append(('manifest', json.loads((instructions / 'manifest.json').read_text()), True))
    instruction_profile = json.loads((instructions / 'native/com.github.copilot/profile.json').read_text())
    cases.append(('native', instruction_profile, True))
    canonical = ROOT / 'examples/canonical-instructions/.agents'
    cases.append(('manifest', json.loads((canonical/'manifest.json').read_text()), True))
    binding = json.loads((canonical/'native/com.github.copilot/profile.json').read_text())
    cases.append(('native', binding, True))
    for field, value in [('source', 'other.md'), ('name', 'AGENTS.md'), ('name', '')]:
        item = copy.deepcopy(binding)
        item['artifacts'][0][field] = value
        cases.append(('native', item, False))
    for target in ('../AGENTS.md', '/etc/AGENTS.md'):
        item = copy.deepcopy(instruction_profile)
        item['artifacts'][0]['name'] = target
        cases.append(('native', item, False))
    item = copy.deepcopy(instruction_profile)
    item['artifacts'][0]['output'] = '/etc/AGENTS.md'
    cases.append(('native', item, False))
    for key, value in [('namespace', 'invalid'), ('scope', 'system'), ('harness_version', ''), ('required', 'yes'), ('output', '/etc/config')]:
        item = copy.deepcopy(profile); item[key] = value; cases.append(('native', item, False))
    for key in profile:
        item = copy.deepcopy(profile); del item[key]; cases.append(('native', item, False))
    for source in ('../config.toml', '/etc/config', 'dir/../config', 'dir//file', 'dir/./file'):
        item = copy.deepcopy(profile); item['artifacts'][0]['source'] = source; cases.append(('native', item, False))
    item = copy.deepcopy(manifest); item['version'] = '1.1.0-draft.1'; cases.append(('manifest', item, False))
    plugins = ROOT / 'examples/plugins-draft/.agents'
    cases.append(('manifest', json.loads((plugins / 'manifest.json').read_text()), True))
    for path in (plugins / 'plugins').glob('*/profile.json'):
        cases.append(('native', json.loads(path.read_text()), True))
    for directory, version in [('1.0', '1.0.0'), ('1.1-draft', '1.1.0-draft.1')]:
        prior = ROOT / 'spec' / directory / 'schemas/manifest.schema.json'
        validator = Draft202012Validator(json.loads(prior.read_text()))
        assert not validator.is_valid({'version': version, 'profiles': ['plugins']}), 'plugins changed a prior version'
    for index, (name, value, valid) in enumerate(cases):
        assert validators[name].is_valid(value) == valid, (index, name, value)
    print(f'{len(cases)}/{len(cases)} native draft.2 schema cases passed')


if __name__ == '__main__':
    main()
