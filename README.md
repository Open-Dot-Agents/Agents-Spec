# Open-Dot-Agents Specification

`SPEC/` is the minimal, vendor-neutral representation of repository-scoped AI
agent configuration. A project owns this portable `.agents/` tree; adapters
translate it to a specific harness without making the portable model vendor
dependent.

## Directory layout

```text
.agents/
  AGENTS.md
  tools/
    mcp.json
  skills/
    <skill-name>/
      SKILL.md
```

| Path | Purpose |
| --- | --- |
| `.agents/AGENTS.md` | Shared instructions for agents working in the repository. |
| `.agents/tools/mcp.json` | MCP server definitions. |
| `.agents/skills/<skill-name>/SKILL.md` | A reusable, self-contained skill. |

## MCP servers

MCP server definitions use a top-level `mcpServers` object keyed by server
name. Stdio servers define `type`, `command`, optional `args`, and optional
`env`. Remote servers define `url` and, when needed, `headers`.

```json
{
  "mcpServers": {
    "example": {
      "type": "stdio",
      "command": "example-mcp",
      "args": ["serve"]
    }
  }
}
```

Keep secrets out of this file. Configure any required credentials through the
provider's supported environment or secret-management mechanism.

## Skills

Each skill occupies its own directory and is defined by `SKILL.md`. The skill
content is portable Markdown and should include the instructions, constraints,
and any commands needed to apply that skill. Supporting files may live beside
`SKILL.md` when the skill requires them.

## Adapter mapping

| Harness | MCP configuration | Skills |
| --- | --- | --- |
| GitHub Copilot CLI | `.github/mcp.json` | `.agents/skills` |
| OpenAI Codex | `.codex/config.toml` under `[mcp_servers]` | `.agents/skills` |
| Claude Code | `.mcp.json` | `.claude/skills` |
| OpenCode | `opencode.json` | Native configuration |

The initial `agents` Go CLI supports Copilot CLI and Codex MCP conversions and
portable skills. Claude Code and OpenCode adapters are intentionally deferred.