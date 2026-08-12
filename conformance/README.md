# Open-Dot-Agents 1.0 conformance baseline

Run the fixture baseline with only the Python standard library:

```sh
python3 conformance/run.py
```

The runner checks that the shipped JSON Schemas parse, validates the canonical
starter manifest and existing JSON fixtures, and checks portable tree
semantics that JSON Schema cannot express. It emits one `PASS` or `FAIL` line
per check and exits non-zero on failure.

## Fixture layout

- `fixtures/canonical-manifest.json` is the interoperable starter manifest.
- `fixtures/selection-*` select exactly one portable content profile and
  contain only that profile's portable content.
- `fixtures/invalid` contains trees that must be rejected for unsafe skill
  names or skill paths. The unsafe-path fixture intentionally uses a symlink
  from `SKILL.md` outside its skill directory.
- `../examples/basic` and `../examples/invalid` are also part of the run.

This baseline is implementation-neutral fixture evidence, not a claim that
every harness has the same runtime behavior. Native-harness projection and
black-box validation remain adapter-specific. Adapters must also make their
capability-loss declarations for any content they cannot preserve, as required
by the normative specification.
