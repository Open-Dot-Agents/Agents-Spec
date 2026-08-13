# Open-Dot-Agents 1.0 conformance baseline

Install the pinned Draft 2020-12 validator and run the fixture baseline:

```sh
python3 -m pip install -r conformance/requirements.txt
python3 conformance/run.py
```

For the portable machine-readable result contract, run:

```sh
python3 conformance/run.py --format json
```

The runner applies the full JSON Schemas with format checking, validates the
canonical starter manifest and existing JSON fixtures, and checks portable tree
semantics that JSON Schema cannot express. It emits one `PASS` or `FAIL` line
per check and exits non-zero on failure.

## Fixture layout

- `fixtures/canonical-manifest.json` is the interoperable starter manifest.
- `fixtures/selection-*` select exactly one optional portable content profile
  and contain only that profile's content in addition to mandatory
  `.agents/AGENTS.md` instructions.
- `fixtures/baseline-instructions` includes canonical instructions and a nested
  `AGENTS.md` file to demonstrate scoped discovery without an optional profile.
- `fixtures/invalid` contains trees that must be rejected for unsafe skill
  names or skill paths. The unsafe-path fixture intentionally uses a symlink
  from `SKILL.md` outside its skill directory.
- `../examples/basic` and `../examples/invalid` are also part of the run.

This baseline is implementation-neutral fixture evidence, not a claim that
every harness has the same runtime behavior. Native-harness projection and
black-box validation remain adapter-specific. Adapters must also make their
capability-loss declarations for any content they cannot preserve, as required
by the normative specification.
