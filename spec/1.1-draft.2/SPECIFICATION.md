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
Sources are regular files below the namespace directory, except for the fixed
canonical instruction binding defined below. Paths must not contain symlinks,
parent segments, empty segments, or absolute paths.

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

### Native agent instruction files

The Copilot project registry defines the `agent-instructions` artifact kind.
Its `name` selects exactly one of `AGENTS.md`, `CLAUDE.md`,
`.claude/CLAUDE.md`, or `GEMINI.md` below the project root. No other path or
scope is registered for this kind. The source is UTF-8 Markdown below the
native namespace. A processor must preserve its bytes and target location.

Plain root instructions can enter the portable core when conversion is
lossless. A processor can preserve a root file with native references, or a
root body that differs from the Copilot instruction body, as a native agent
instruction artifact. It must not discard either body or change a reference
base. Distinct native files are separate assignments; duplicate assignments
to one target remain an error. Existing canonical portable policy must remain
protected during additive import.

Referenced project files remain external dependencies. A processor must report
this requirement. This artifact kind does not authorize arbitrary reference
targets, reference expansion, file copying outside the registry, or trust
changes. Native discovery precedence and reference behavior must be reported
from version-specific evidence. Configuration preservation does not establish
that every stored instruction is active or that a model follows it.

### Canonical instruction binding

In the Copilot project `native` profile, the `canonical-instructions` artifact
binds the portable instruction core to root `AGENTS.md`. Its `source` must be
the literal `AGENTS.md`, which refers to `.agents/AGENTS.md`. The `name` field
must be absent. No other core source or output path is selectable. This is the
only defined exception to namespace-relative artifact sources. The canonical
source must remain a regular file, without indirect links.

The processor projects that core once, at the bound root path. A separate
`instructions` artifact can then project native Markdown to
`.github/copilot-instructions.md`. The processor must not create a second
canonical body in the native namespace. A namespace file named `AGENTS.md` is
a different source from the fixed core reference; the source string alone does
not identify those two files.

A verified root link to the same project's canonical instructions remains in
place. A new target can be a managed regular file with the same body and native
reference base. The processor must preserve foreign ownership, including when
the target is a verified link. Native referenced project files remain external.

An unsupported selected binding stays inactive. If this leaves the mandatory
portable instruction target unmapped, the processor must refuse projection;
it must not silently choose another location. Removal of a binding must also
refuse a known change to a native reference base. The user must retain the
binding or update those references before that transition. These rules do not
authorize changes to native trust or credential stores.

## Shared skills and native discovery reports

The portable `skills` profile keeps its existing Markdown contract. A native
projection check is separate from canonical validation. A processor must not
rewrite skill frontmatter to turn an invalid or unverified native control into
an active one. It can refuse native projection when the selected client cannot
discover a skill. The refusal must identify the source and occur before writes.
It must not claim that it stops direct discovery of an existing project file.

Native plans must distinguish file preservation, discovery, model invocation,
and user invocation when these have different native meanings. They must report
known per-field losses and limitations. A warning is not proof of conformance
or permission enforcement. Reports must not expose credential values.

Unknown annotations in a portable Markdown skill remain source content. A
processor can preserve these bytes with an explicit unmapped-annotation report;
this does not activate or map a native-profile setting. The unknown-content
rules for namespace profiles still apply to those profiles. Shared discovery
does not establish shared metadata semantics between clients.

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

Reimport of a registered user instruction target must preserve an existing
unambiguous artifact declaration and its namespace source. It must not add a
second assignment merely because the native filename differs from that source.
Duplicate declarations for the same user instruction target must cause refusal.
Referenced user instruction files remain external; the processor must report
that dependency without copying them or granting native trust.

Copilot project import recognizes `.agents/skills/` as a native discovery
source. It selects complete existing packages in place, without rewriting
their files or permissions. A missing manifest can establish a new draft.2
tree only when `.agents/` contains recognized skill packages and, optionally,
a regular `AGENTS.md`. Other unversioned canonical content must cause refusal.
An existing manifest must remain subject to its version and validation rules;
an invalid manifest is not an absent manifest. Existing canonical instructions
must remain protected. This exception does not apply to user scope or authorize
imports from parent directories, user homes, or plugin stores.

## Activation and security

Apply writes configuration. Login, installation, scheduling, and execution stay
native operations. Plan and capabilities output must distinguish a configuration
mapping from effective native activation. Reports must not contain credential
values.

Exclusion of external credentials must not activate the remaining native
configuration with weaker authentication. It must not restore a native default
that enables the excluded operation. An adapter must refuse activation or
explicitly disable the complete affected operation and report that change.
Required content still blocks apply; an explicit disabled value is not a
successful mapping of the excluded credentials.

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
