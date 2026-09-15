# Experimental development preset

Status: experimental. This extension does not change stable 1.0 semantics.
It separates practical guidance from strict enforcement.

## Purpose and files

The development preset supplies one editable policy for normal project work.
It is selected through the required `org.open-dot-agents.development` extension
in the experimental permissions profile. Older consumers must refuse the
required extension. The extension data is exactly:

```json
{"path": "permissions/development.json"}
```

The path is fixed relative to the canonical `.agents` directory. It cannot
refer outside that directory or follow a symbolic link. The permissions
document must use `default: "ask"`, an empty `rules` array, and coverage of
exactly `shell` and `builtin-tools`. The extension must have `required: true`.
These fields ensure there is one authoring source for development decisions.
They are not a fallback policy that an unaware consumer may activate.

The editable file is `.agents/permissions/development.json`:

```json
{
  "version": "1",
  "preset": "development",
  "project_work": "allow",
  "local_commits": "allow",
  "external_changes": "ask",
  "destructive_work": "ask",
  "protected_paths": [".env", "secrets"]
}
```

All fields are required. Unknown fields, nulls, and duplicate keys are errors.
Decisions are `allow`, `ask`, or `deny`. `protected_paths` contains distinct,
canonical workspace-relative paths. The workspace root itself, absolute paths,
parent traversal, and globs are not valid. Each path protects that file or
directory and its descendants. Missing paths are still protected if created
later. These are requested restrictions on reads and writes, not file filters
applied only when the adapter starts. Empty `protected_paths` removes only
project-specific path restrictions; it does not grant access to host secrets.

## Enforcement modes

The optional enforcement field is either strict or practical. An absent field
means strict. Unknown values and null are errors. Existing strict documents
must not become practical without an explicit configuration change.

Practical mode uses a draft.2 manifest. The decisions below are instructions
to the agent, including protected paths. A practical adapter MUST report each
native boundary it configures and each control that remains guidance or uses
external authority. It MUST NOT report guidance as equivalent enforcement.
The guardrails document is .agents/guardrails/development.md. The adapter
reads that document and the JSON decisions on each plan/apply. Canonical
instructions must refer to them conditionally on profile selection. Native
projection must deliver the guidance or preserve that explicit reference.

The CLI starter defaults to practical mode and creates the guardrails file.
The --enforcement strict option creates the original strict starter. Practical
adoption preserves existing profiles and instructions, backs up changed
canonical files, and moves the manifest to draft.2. It refuses existing
security selections. Practical mode may coexist with tools, skills, and hooks
only when their separate authority and guidance limits are reported.

Codex practical projection configures a native workspace profile with project
and Git writes for allow, read access otherwise, protected-path deny entries,
and command network disabled. Approval uses on-request with user review.
These are configuration claims, not proof of effective session authority.
Operation-level ask and deny decisions remain guidance. The adapter must
report that writes include deletion, Git writes include history changes,
and credentials and other native tools are not isolated by this profile.
Copilot practical projection supplies guidance and preserves existing native
permission settings. It must report that automatic local execution is not
provided by that projection.

The remaining strict requirements below apply to strict mode. Practical mode
retains their desired workflow as guidance without claiming runtime guarantees.

## Decision semantics (strict enforcement; practical guidance)

| Field | Operations |
| --- | --- |
| `project_work` | Read and edit project files; run project tests, builds, and formatters. |
| `local_commits` | Stage changes and create new commits in the current project, including its submodules. |
| `external_changes` | Push, publish, deploy, send messages, and other mutations outside the local project. |
| `destructive_work` | Rewrite existing history, discard unrelated work, or remove unrelated data. |

`local_commits` does not authorize pushes, history rewriting, or arbitrary
Git configuration changes. The meaning of an operation depends on its effects,
not solely on the first command word. A test script that deploys also requires
the external-change decision. A commit hook that publishes requires the same
decision. A local path used as a push destination remains an external change.
An alias, interpreter, subprocess, alternate tool, or background process must
not avoid a decision. If multiple categories apply, `deny > ask > allow`.
Unclassified operations require approval. Denial, missing approval channels,
and approval timeouts prevent the action.

Covered code must not read protected paths or host credential stores, modify
host security, write outside approved project/runtime locations, or change
its own active permission controls without explicit external authority. The
adapter must report native runtime resources and preserve the host's policy.
Harness authentication must be separated from the covered code. No repository
policy grants native trust or overrides administrator or session restrictions.

MCP, hooks, LSP, delegation, apps, and browser actions must not be silently
treated as covered by shell enforcement. An adapter must either prove the
same decisions for active routes or refuse the combined configuration.

## Setup and lifecycle

In strict mode, `agents init --preset development --enforcement strict --experimental` creates the policy in a new
canonical tree. `--adopt` explicitly migrates an existing validated tree,
preserving profile selections, requirements, and instructions. It saves a
private backup of the original manifest, changes stable 1.0 to draft.1, and
retains an existing draft version. Existing security selections or unselected
policy files cause refusal. Failed writes roll back the migration and backup.
`--force` is not accepted. Existing root instructions are preserved. Setup
does not write native configuration, grant trust, or activate permissions.

Plan reports the requested decisions and verified native support separately.
In strict mode, apply must refuse the complete operation before writes when any requested
control lacks an equivalent native mapping. `--force` does not override this
requirement. The direct-shell Codex subset cannot activate this interactive
preset. Validation proves document correctness only.

Removal and migration must report the resulting native defaults, preserve
unrelated configuration, and use ownership checks and rollback. The CLI must
not install a runtime mediation layer to simulate missing native enforcement.

## Strict enforcement acceptance work

- New project setup, editable decisions, validation, and readable plans.
- Explicit migration for existing projects without losing profiles or rules
  (implemented for trees without existing security policy).
- Codex native setup, precedence checks, apply, repeat apply, update, removal,
  conflict handling, and rollback.
- Native automatic edit, test, build, format, staging, and commit cases.
- Native push, publish, deployment, and other external-change approval cases:
  acceptance, rejection, missing channel, and timeout.
- Native indirect routes, protected files, credentials, subprocesses, nested
  Git directories, hooks, and conflicting host policy.
- Copilot activation only where the same contract is preserved.

Passing refusal or schema tests does not complete the native acceptance work.

## Scoped practical apply

For project-scoped Codex, plan/apply --preset development operates only on
the development configuration fields and their ownership entries. It must
state that other profiles and required capabilities remain unchanged and
unverified by that operation. Full repository apply retains all capability
checks. A scoped operation must not remove other owned fields or silently
change a strict security selection.

Explicit --force --backup permits migration of legacy project sandbox keys
and conflicting unowned development fields. It must back up the native file
and preserve unrelated settings. Ownership held by another source and
externally modified owned fields still cause refusal. Removing the selected
development policy through scoped apply removes only its owned fields.
