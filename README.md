# Open-Dot-Agents Specification

Open-Dot-Agents defines a vendor-neutral, repository-scoped `.agents/`
configuration. Adapters may project this portable contract into native harness
configuration; native paths and formats are not part of this standard.

## 1.0.0

- [Normative 1.0 specification](spec/1.0/SPECIFICATION.md)
- [Manifest JSON Schema](spec/1.0/schemas/manifest.schema.json)
- [MCP JSON Schema](spec/1.0/schemas/mcp.schema.json)
- [Conformance result JSON Schema](spec/1.0/schemas/conformance-result.schema.json)
- [Basic conforming example](examples/basic/)
- [Invalid schema fixtures](examples/invalid/README.md)
- [Conformance baseline](conformance/README.md)
- [Changelog](CHANGELOG.md)

The repository's own [`.agents/`](.agents/) directory is a minimal conforming
configuration.

## Release gate

Before tagging a specification release, run:

```sh
task verify
```

or directly:

```sh
python3 conformance/run.py
```

The root repository release gate also runs JSON validation, compatibility
drift checks, reference CLI tests, and Workbench projection tests. Those
checks do not imply native harness adapter support.
