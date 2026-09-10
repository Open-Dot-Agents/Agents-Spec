# Experimental security profiles: 1.1.0-draft.1

This is a proposal for public review. It is not a ratified standard or a
release. The 1.0 specification and release support gates remain unchanged.
The key words MUST, MUST NOT, SHOULD, and MAY specify requirements of this
draft only. A consumer MUST require explicit experimental opt-in.

## Layout and version

The 1.0 instruction, MCP, hook, and skill rules still apply. This draft adds:

```text
.agents/manifest.json                 version: 1.1.0-draft.1
.agents/permissions/permissions.json  selected by permissions
.agents/sandbox/sandbox.json          selected by sandbox
```

The manifest MUST use this draft's manifest schema. Each selected policy file
MUST exist as a regular file, without a symbolic link in its path. A consumer
MUST reject unknown properties, duplicate JSON keys, and null values in draft
policy files and the draft manifest. Unselected files are inert. Instructions
cannot override these policies. Selecting either profile requires its matching
capability, even when `requires` omits it. A consumer MUST validate selected
1.0 profiles as well. The new profiles are independent: tool approval does not
imply process isolation, and process isolation does not imply tool approval.

See [schemas](schemas/) and the [example](../../examples/security-draft/).

## Permissions

`default` is `deny`, `ask`, or `allow`. `rules` is an array of exact selectors.
A rule has `kind` (`tool` or `process`), `name`, and `effect`. Process rules
also require `args`, including an empty array for a command without arguments.
Tool rules MUST NOT have `args`. A name of `*` matches all names of that kind.
All other names match exactly. A process name identifies the requested
executable; an adapter MUST bind it to the resolved executable and refuse an
ambiguous or mutable executable identity. Rules do not grant access to an
executable solely because its basename matches a trusted program.

Process arguments match the complete vector. They are not shell strings,
regular expressions, or command prefixes. A grant for `git` with `["status"]`
does not grant `git status; other-command`, a shell that runs that text, or
`git status --other-option`. Tool identifiers are portable capability names
where available; vendor tool names require an explicit verified mapping.

When multiple rules match, `deny > ask > allow`. The default applies only
when no rule matches. Rule order has no effect. An adapter MUST NOT convert
`ask` to `allow`. Without an approval channel, or after refusal or timeout,
`ask` means deny. An approval cannot override a matching deny, an administrator
restriction, or a sandbox boundary. Required sandbox access must be satisfied
separately. No policy file can grant repository trust.

## Sandbox

### Filesystem

`filesystem.default` and each rule's `access` are `deny`, `read`, or `write`.
Write includes read. Paths are workspace-relative canonical paths. `.` means
the workspace and its descendants. The schema limits path syntax to ASCII
portable components. Absolute paths, `..`, `./x`, empty components, backslashes,
globs, and environment substitutions are invalid. A rule applies to its path
and descendants at component boundaries. Among matching rules, the most
restrictive access wins: `deny > read > write`. Default applies only if no
rule matches. A child write rule MUST NOT weaken a parent deny or read rule.

At access time an implementation MUST check both the requested path and its
resolved target. Symlinks, hard links, mount points, traversal, and races MUST
NOT bypass a restriction. Targets outside the workspace use the default.
An implementation that cannot enforce these rules MUST refuse activation.
An adapter MUST list native runtime read/write grants separately, including
temporary directories, tool installations, sockets, Git metadata, and caches.
An automatic grant that violates the policy is grounds for refusal.

`filesystem.runtime` is an optional array of explicit runtime grants. An absent
or empty array grants no runtime exception. This draft defines `process`:
native private device and process-information mounts, plus the standard input,
output, and error streams supplied by the caller. An adapter MUST identify the
actual native resources in its plan. This grant permits process runtime I/O;
it MUST NOT authorize new opens of ordinary host files, shared temporary
directories, shared caches, credential stores, or host service sockets beyond
the other policy rules. A native implementation that requires such extra
access MUST refuse unless the policy independently permits that access.
This field is an optional addition within the unratified draft; existing draft
files retain their previous requirements.

### Network

`network.default`, each rule's `effect`, and the `local`, `private`, `web`,
and `remoteMCP` fields use the permissions decisions. A rule has one exact
lowercase ASCII host (DNS name or IPv4 address) and explicit TCP/UDP ports.
No wildcard, URL, protocol prefix, IPv6 literal, or implicit port is allowed
in this draft. IPv6 traffic remains subject to default, local, and private
restrictions. DNS resolution and redirects MUST NOT bypass a deny. Each new
connection and redirect target requires a fresh check. Both host and resolved
IP restrictions apply. A domain grant cannot override a private/local deny.

Loopback, Unix sockets, and same-host targets are local. Non-public IP ranges,
link-local addresses, private ranges, unspecified addresses, multicast, and
IPv4-mapped forms are private. If classification is uncertain, treat the
target as private. `local` and `private` are additional restrictions on the
host decision. `web` and `remoteMCP` are additional restrictions for those
tool classes, including services accessed outside the subprocess sandbox.
The strongest applicable decision wins. Unmatched hosts use `default`.

A proxy setting is not evidence of enforced isolation. An adapter MUST refuse
if a process can ignore the proxy, use an alternate transport, or reach a
disallowed target. `ask` without an approval channel denies the connection.

### Credentials and coverage

`credentials.environment` is `none` or `inherit`. With `none`, only names in
`allow` may be passed from the approved execution environment. With `inherit`,
all inherited variables may be exposed; `allow` does not narrow that choice.
`credentials.files` is `deny` or `inherit`. Deny requires evidence that native
credential files and credential brokers are not exposed to covered code.
Inherit permits exposure only within filesystem policy. These fields contain
names and requirements, never credential values. A consumer MUST NOT log or
copy secret values into canonical or projected files.

Each profile requires an explicit `coverage` array. The possible scopes are
`builtin-tools`, `shell`, `hooks`, `mcp-local`, `mcp-remote`, `lsp`, and
`delegation`. Coverage applies to descendants and background processes. An
adapter MUST report uncovered scopes; it MUST NOT imply they are protected.
MCP server processes, LSP servers, and delegated agents do not automatically
inherit the main tool sandbox. Filesystem isolation does not prove credential
isolation. Access by the harness itself for authentication must be separated
from access by covered code, or the adapter MUST refuse.

## Extensions and authority

Both policy files accept `extensions`, keyed by a reverse-domain namespace
such as `com.openai.codex` or `com.github.copilot`. Each value has a `required`
boolean and a `data` object. Consumers MUST preserve extension data. An unknown
required extension blocks activation. An unknown optional extension remains
in the canonical file and MUST be reported as inactive. No extension may
weaken a portable restriction, even when a vendor setting has higher native
precedence. Extensions are not a way to store credentials or grant trust.

Repository files request policy. They do not authorize administrator changes,
credential access, native trust-store writes, or bypass flags. Before any
write, an adapter MUST verify its tested native version range, prerequisites,
effective configuration authority, native conflicts, and required scope.
It MUST refuse unknown authority or incompatible controls. Security loss MUST
cause refusal, not a warning followed by activation. The CLI is not a runtime
launcher and MUST NOT install a mediation layer to simulate these controls.

## Planning, import, and removal

A plan MUST report the declared and normalized policy, projected settings,
automatic grants, unresolved controls, and evidence scope. Empty projected
settings after refusal mean no projection, not an enforced deny-all policy.
An empty automatic-grant list after refusal means none were projected; the
native runtime may still have grants. Effective runtime grants must be marked
unknown until verified. Draft validation reports use `schemaVersion` and `standardVersion` equal to
`1.1.0-draft.1` and the draft conformance-result schema. Stable validation
reports retain their 1.0 schema. Reports MUST distinguish validation, refusal,
projection, and observed enforcement.

Import MUST refuse security migration when it cannot recover effective policy
and authority without loss. Force MUST NOT override that refusal. An import
MUST NOT replace a draft manifest with a stable manifest and discard policy.
Apply and sync MUST preflight the complete operation before any file, backup,
or ownership write. Refusal leaves previous native policy active. Direct
native use can still bypass a refused adapter; the adapter does not disable
an installed harness.

Removing a profile selects no policy from that profile. Adapters that own
native security settings MUST remove only those settings, preserve unrelated
content, and use existing conflict and rollback rules. They MUST report the
resulting native defaults and grants before removal. The Codex shell subset
owns only its marked selectors and named profile. Removal makes the recorded
explicit-profile invocation fail because that profile no longer exists. Other
native invocations remain outside that evidence scope. A draft without
selected security profiles can still project its selected 1.0 content with
explicit opt-in.

## Reference implementation and migration

The reference CLI validates and normalizes this draft. It implements a narrow
Codex 0.154.0 Linux amd64 subset for direct `codex sandbox` commands, with
explicit `--codex-home`, pre-existing trust, and a pinned native binary. The
[example](../../examples/codex-linux-security/) declares read access by default,
explicit workspace restrictions, the process runtime grant, subprocess network
denial, and credential inheritance. Optional permissions must allow shell
commands without rules. Ask, deny, exact-command rules, default-deny filesystem,
credential isolation, and other execution scopes remain refused.

This subset binds the exact native invocation and replacement environment in
the plan. It requires a configuration-only native home, refuses unknown native
configuration layers, and does not edit trust. A caller MUST run a fresh plan
check before native execution. Changes by outside actors to authority, mounts,
policy paths, or native binaries invalidate that preflight. A caller-selected
bypass or different native invocation is outside the evidence scope. Repository
policy cannot constrain the host owner or silently authorize a new invocation.

Unknown required extensions receive a separate diagnostic. Copilot and Claude
security activation still refuse. No full security adapter is supported.

To try the draft, copy the example to an isolated test repository and use
`agents validate --experimental`. Use `agents plan --experimental --format json`
to inspect refusal details. Do not change production manifests to the draft
until the required native enforcement is available. A 1.0 consumer rejects the
draft version. Returning to 1.0 requires an explicit decision to remove the
draft requirements; it is not a lossless conversion.

Ratification requires a public proposal, the comment period, and a recorded
maintainer decision under the project governance rules. This document does
not start or complete that process.
