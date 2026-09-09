# Invalid schema fixtures

Each file is valid JSON but intentionally fails the named 1.0 JSON Schema.
They are fixtures for schema-validation tests, not examples to copy.

| File | Schema | Expected failure |
| --- | --- | --- |
| `manifest-invalid-profile.json` | manifest | Profile entries must be portable profile strings. |
| `manifest-invalid-capability.json` | manifest | `mcp.websocket` is not a defined capability. |
| `mcp-literal-environment.json` | MCP | An environment value must be an `urn:open-dot-agents:env:` reference, not a literal. |
| `mcp-insecure-remote.json` | MCP | Remote URLs must use HTTPS. |
| `mcp-mixed-server.json` | MCP | A server cannot combine `stdio` and `remote` fields. |
| `hooks-unsupported-event.json` | hooks | Hook event names must be defined portable events. |
| `hooks-literal-prompt.json` | hooks | 1.0 hook handlers must be command handlers, not prompt hooks. |

Cross-file failures, such as a selected `tools` profile without a catalogue, are
specified in the normative document and require a conformance checker in
addition to JSON Schema.

The additional `hooks-*.json` fixtures reject null fields, null event arrays,
empty matchers, empty handler lists, negative timeouts, and blank commands.
Both the CLI and the schema validate these fixtures in the root test workflow.
