# Changelog

All notable changes to this specification are documented here.

## Unreleased experimental proposal

- Define draft.2 global source selection, fixed user instruction bindings,
  complete skill package preservation, and explicit inherited source ownership.
  Add global examples and invalid binding cases. Keep stable 1.0 unchanged.

- Clarify user instruction source preservation during reimport and the external
  reference boundary. Add a Copilot user instruction example.
- Draft.2 Copilot project import selects existing `.agents/skills` packages in
  place. A bare shared skill tree can establish draft.2; malformed manifests,
  other unversioned content, and existing policy conflicts still refuse.
- Define draft.2 Copilot project `agent-instructions` artifacts. Preserve
  fixed native file locations and report external reference dependencies.
- Define a fixed Copilot `canonical-instructions` binding. Keep the portable
  source single and retain separate native instruction bodies after relocation.

- Add separate 1.1.0-draft.1 permissions and sandbox schemas, semantics,
  example, and conformance fixtures. The proposal is not ratified.
- Add an explicit optional process runtime grant and a narrow Codex Linux
  example. Existing draft files retain their previous requirements.
- Preserve the 1.0 specification and schemas without changes.

## [1.0.0] - 2026-08-12

### Added

- Initial Open-Dot-Agents 1.0.0 contract.
- Manifest and MCP JSON Schemas.
- Basic conforming example and invalid schema fixtures.
- Standard-library conformance baseline for portable tree semantics.
- Explicit separation between portable specification conformance and native
  adapter support evidence.
- Canonical `.agents/AGENTS.md` instructions, optional nested `AGENTS.md`
  scoping, and root compatibility links for native discovery.
- Structurally aligned `tools` and `skills` profile names.
- Defined repository, producer, consumer, and adapter conformance classes with
  a machine-readable result schema.
