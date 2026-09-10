# Native configuration draft.2

Status: experimental proposal. This draft does not change stable 1.0 or
1.1.0-draft.1. A processor must require an explicit experimental option.
The existing security requirements still apply.

## Native profile

The manifest can select `native`. Each namespace has one
`.agents/native/<namespace>/profile.json` file. This milestone defines
`com.openai.codex` and `com.github.copilot` on Linux.

A profile records `namespace`, `harness_version`, `scope`, `required`, and
`artifacts`. An artifact records `kind`, `source`, and, when needed, `name`.
Sources are regular files below the namespace directory. Paths must not contain
symlinks, parent segments, empty segments, or absolute paths.

The adapter registry determines the output location from the artifact kind,
selected scope, and native home. Profile metadata cannot set an output path.
Unknown optional namespaces, versions, fields, and artifact kinds stay in the
canonical tree and do not activate. Unknown required content blocks activation.
A parser result alone does not establish a setting mapping.
Processors can select known object fields separately from unknown optional
siblings. They must report every omitted field. An array with an unmapped member
must stay inactive unless a mapping establishes that partial selection preserves
its order and meaning. These rules do not authorize modification of source data.

Codex files use TOML. Copilot files use JSON, JSONC, or Markdown, as specified by
the native artifact. A processor must refuse duplicate configuration assignments,
including assignments from different canonical profiles. Existing portable
fields belong in the portable core when conversion is lossless. Native fields
with no established portable meaning stay in their namespace.

## Plugin selection profile

The manifest can select `plugins`. Native plugin and marketplace selection
files use `.agents/plugins/<namespace>/profile.json` and the same metadata
schema as the native profile. The registry maps `config` artifacts to the
selected client's project or user configuration file. No other artifact kind
can write through this profile. Unknown optional artifact kinds remain
inactive; required unmapped content blocks activation.

Codex selection files use TOML roots `plugins` and `marketplaces`. Copilot
selection files use JSON or JSONC roots `enabledPlugins` and
`extraKnownMarketplaces`. Other roots are inactive and must be reported; required
ones block activation. These remain native settings. They do not define a
shared marketplace or plugin identity model. A malformed or unmapped plugin
entry must not be partly activated if omitted fields could affect its behavior.

Import moves new declarative plugin selections into this profile. Existing
canonical native selections remain in their established profile; import must
not duplicate them or change their required status. Codex marketplace
`last_revision` and `last_updated` are external runtime state and must not be
imported as writable configuration. Installed packages, caches, plugin data,
login, trust, and managed policy remain native. Import must not copy those
stores or recurse through a native home.

A source or plugin identifier with embedded credentials must be refused without
printing its value. Apply writes selection configuration only. The processor
must report that a later native startup or refresh can fetch or install enabled
packages. Apply itself must not fetch, install, update, or execute a package.

The portable package format is [Agent Plugins 1.0.0](https://agent-plugins.org/specification),
with root `plugin.json`, fixed `skills/` and `mcp.json` components, and named
native extensions. This package format is separate from the selection profile.
The selection profile does not grant permission to reinterpret or rewrite an
existing marketplace package. Local package loading needs separate support and
conformance evidence; this first selection implementation does not provide it.

## Scope and ownership

Project scope is the default. User scope requires an explicit absolute native
home. The draft.1 `--codex-home` option retains its original meaning.

The processor must merge portable and native content once for each target.
Configuration ownership applies to keys or sections. Standalone assets have file
ownership. Each user ownership record identifies the source repository.
`--force` does not authorize a different repository to replace or remove a
setting. The private ownership registry uses the XDG state directory and is
indexed by vendor and canonical native-home path.

Before a write, the processor must lock the target, reload ownership, and repeat
conflict and authority checks. New user configuration, ownership records, and
private backups use mode `0600`. Existing configuration permissions stay the
same. Configuration, ownership, backup, and removal operations are one
transaction. If an operation fails, completed operations must roll back.
Executable skill assets can use private mode `0700`; they are standalone assets,
not native configuration files. Plan must list the backup operations that apply
will perform.

Import reads recognized files and asset directories. It must not recursively
copy a native home. It must preserve existing portable policy and refuse lossy
conversion. Trust, credentials, managed policy, account state, and live session
databases are external to the writable configuration contract.
An additive import into an existing draft.2 tree must preserve selected profiles,
portable policy files, manifest requirements, and required native status. Equal
values can be retained; conflicting values must cause refusal. Native import
does not implicitly migrate stable or draft.1 trees.

## Activation and security

Apply writes configuration. Login, installation, scheduling, and execution stay
native operations. Plan and capabilities output must distinguish a configuration
mapping from effective native activation. Reports must not contain credential
values.

A native extension cannot weaken a selected portable requirement. Mandatory
`ask` requires approval before every action in its coverage. Native `on-request`
is a separate setting. `network.local: deny` covers filesystem Unix sockets,
abstract Unix sockets, host services, and sandbox loopback.

Each behavioral claim requires a pinned harness version, correlated native
events, and observable effects. A schema check, projection test, or configuration
read does not establish enforcement or full adapter support.

## Reference implementation status

The first implementation provides scoped transactions, ownership, typed setting
mappings, portable MCP and hook projection, and selected assets. It does not yet
implement the complete milestone. The source-linked coverage map in the parent
repository records missing mappings. Agent assets, some structured fields, broad
native asset import, and combined security activation still need work. Release
support and ratification gates do not change.
