# Open-Dot-Agents 1.0

## Status and terminology

This is the normative Open-Dot-Agents 1.0 specification. The key words
**MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, and **MAY**
are to be interpreted as described by RFC 2119 and RFC 8174.

An **implementation** is a producer, validator, or adapter. An **adapter**
projects this portable contract to a particular agent harness. A repository is
conforming when its selected profile satisfies this document and both JSON
files, when present, validate against their linked 1.0 schemas.

## Canonical tree

```text
AGENTS.md                         # optional repository instructions
<subdirectory>/AGENTS.md          # optional scoped instructions
.agents/
  manifest.json                 # REQUIRED
  tools/
    mcp.json                    # optional MCP server catalogue
  skills/
    <skill-name>/
      SKILL.md                  # one portable skill
      ...                       # optional skill-local supporting files
```

Paths are relative to the repository root and use `/` separators. The
directories `tools` and `skills` are optional when they contain no selected
content. A skill name MUST match both its directory name and the selected
skill name. Files not described by this tree are outside the portable
contract. An `AGENTS.md` file applies to its containing directory and
descendants. Starting at the repository root, a consumer MUST apply each
`AGENTS.md` encountered on the path to the working file, with the nearest file
taking precedence when instructions conflict.

`.agents/manifest.json` MUST validate against
[`schemas/manifest.schema.json`](schemas/manifest.schema.json) in the
[Agents-Spec repository](https://github.com/Open-Dot-Agents/Agents-Spec).
The `$schema` property is optional. Producers SHOULD use the immutable schema
URL from the `Agents-Spec` `v1.0.0` tag after that tag is published.
`.agents/tools/mcp.json`, if present, MUST validate against
[`schemas/mcp.schema.json`](schemas/mcp.schema.json). JSON Schema validation
does not establish cross-file references; the additional checks in this
document remain required.

## Versioning and manifest

The manifest is the entry point and MUST contain `version: "1.0.0"`.
`version` is the contract version, not an adapter version. Future
incompatible contracts use a new major standard version and schema URI;
compatible additions use a later SemVer minor version under the same major
line.
Implementations MUST reject an unsupported major version rather than guess
its meaning.

The minimal interoperable starter manifest is:

```json
{
  "version": "1.0.0",
  "profiles": ["instructions", "mcp", "skills"]
}
```

`profiles` is a non-empty, duplicate-free array of portable profile strings.
It selects content categories for this repository; it is not a map of
adapter-specific profiles. 1.0 defines `instructions`, `mcp`, and `skills`.
An implementation MUST validate each string's portable-name syntax and MUST
not require all three names. A 1.0 consumer MUST reject an unknown selected
profile before activation. A producer MAY preserve an unknown well-formed
profile while migrating data, but MUST report that it cannot validate or
activate the profile.

The manifest schema validates known fields strictly while permitting unknown
top-level fields. Producers MAY add such fields for forward compatibility;
consumers MUST ignore fields they do not understand and MUST NOT treat them
as native adapter configuration.

## Portable content profiles

### Instructions

When `profiles` contains `instructions`, a consumer MUST load the applicable
root and nested `AGENTS.md` files using the scope and precedence rule above.
The root file is optional. An adapter MUST NOT create a second canonical copy
under `.agents/`. `AGENTS.md` is portable Markdown; this standard intentionally
does not impose a front-matter format.

The profile declaration defines content managed by this standard. It cannot
disable instruction discovery performed independently by a native harness.
An adapter MUST report such native behavior as a limitation instead of
claiming that an absent profile suppresses it.

### MCP

`.agents/tools/mcp.json` is a catalogue, not an instruction to start servers
unless `profiles` contains `mcp`. Selecting `mcp` exposes the complete
catalogue and requires that catalogue to exist. Implementations MUST NOT start
or expose catalogue servers when `mcp` is absent from `profiles`.

The MCP schema defines direct `stdio` and HTTPS `remote` server definitions.
`stdio` commands MUST be invoked as an executable plus argument vector, not
as a shell command string. This standard does not prescribe any vendor-native
MCP file or field mapping; adapters are responsible for faithful projections.

### Skills

When `profiles` contains `skills`, each `.agents/skills/<skill-name>/SKILL.md`
is selected. `SKILL.md` MUST be UTF-8 Markdown. Supporting files MUST remain
below that skill directory. The standard does not define automatic skill
discovery: adapters MUST NOT expose skills when `skills` is absent from
`profiles` unless the loss rules apply.

## Capabilities and loss semantics

Capabilities identify portable features that an adapter can faithfully
represent. The defined names are:

```text
instructions
instructions.scoped
skills
mcp.stdio
mcp.remote
mcp.envRef
```

`instructions.scoped` means that nested discovery and nearest-file precedence
are preserved. `requires` in the manifest declares capabilities required by
that configuration. An adapter MUST verify every required capability before
activation. Independently, an `instructions` profile requires `instructions`,
nested instruction files require `instructions.scoped`, the `skills` profile
requires `skills`, the `mcp` profile containing `stdio`
or `remote` servers requires its corresponding MCP capability, and environment
references require `mcp.envRef`.

An adapter MUST preserve selected content and the meaning of environment
references. If it cannot do so, it MUST refuse activation or report every
lost item clearly before activation. It MUST NOT silently omit content,
broaden a profile selection, replace a secret reference with a literal, or
claim conformance after a lossy projection. Reporting a loss is not itself
conformance for that activation.

## Security constraints

Credentials and other secret values MUST NOT appear in portable files. The
only credential/configuration indirection allowed by the MCP schema is an
environment-reference URI:

```text
urn:open-dot-agents:env:VARIABLE_NAME
```

This URI uses the standard URN URI scheme and identifies an environment
variable by name; it is not its value. It MAY appear only where the MCP schema
permits an environment reference. Adapters MUST resolve it at execution time
from their approved environment or secret mechanism, MUST NOT log its
resolved value, and MUST fail rather than substitute an empty or literal
secret when it is unavailable.

Remote servers MUST use HTTPS. Adapters MUST treat `command`, `args`, remote
URLs, skills, and instructions as repository-controlled input, avoid shell
interpolation for stdio commands, and apply least privilege when granting
filesystem, network, or process access. An adapter MUST NOT infer credentials
from arbitrary instruction text or skill content.

## Conformance

Conformance claims MUST identify one of these classes:

- **repository**: portable files satisfy this specification;
- **producer**: emitted portable files satisfy this specification;
- **consumer**: selected profiles are loaded with the required semantics; or
- **adapter**: a named standard and harness version preserves declared
  capabilities without silent loss.

Machine-readable results MUST validate against
[`schemas/conformance-result.schema.json`](schemas/conformance-result.schema.json).
A result identifies the implementation and standard version, conformance
class, fixture outcomes, and diagnostics. Diagnostic codes are stable public
identifiers; human messages are not an interoperability interface.

The [basic example](../../examples/basic/) is a valid 1.0 tree. The
[invalid fixtures](../../examples/invalid/README.md) are syntactically valid
JSON documents that a 1.0 validator MUST reject for the stated schema reason.
