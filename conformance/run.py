#!/usr/bin/env python3
"""Standard-library conformance checks for the Open-Dot-Agents 1.0 fixtures."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


SPEC_ROOT = Path(__file__).resolve().parent.parent
PROFILE_NAME = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
ENVIRONMENT_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
HEADER_NAME = re.compile(r"^[!#$%&'*+\-.^_`|~0-9A-Za-z]+$")
ENVIRONMENT_REFERENCE = re.compile(
    r"^urn:open-dot-agents:env:[A-Za-z_][A-Za-z0-9_]*$"
)
CAPABILITIES = {
    "instructions",
    "skills",
    "mcp.stdio",
    "mcp.remote",
    "mcp.envRef",
}


class ConformanceError(ValueError):
    """A fixture violates a portable 1.0 rule."""


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ConformanceError(f"{path}: invalid JSON: {error}") from error


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ConformanceError(message)


def validate_manifest(value: object, label: str) -> list[str]:
    require(isinstance(value, dict), f"{label}: manifest must be an object")
    require(value.get("version") == "1.0.0", f"{label}: version must be 1.0.0")

    schema = value.get("$schema")
    require(
        schema is None or isinstance(schema, str),
        f"{label}: $schema must be a string when present",
    )
    profiles = value.get("profiles")
    require(
        isinstance(profiles, list) and profiles,
        f"{label}: profiles must be a non-empty array",
    )
    require(
        all(isinstance(profile, str) and PROFILE_NAME.fullmatch(profile) for profile in profiles),
        f"{label}: profiles must contain portable profile strings",
    )
    require(
        len(profiles) == len(set(profiles)),
        f"{label}: profiles must not contain duplicates",
    )
    requires = value.get("requires", [])
    require(
        isinstance(requires, list)
        and all(isinstance(capability, str) and capability in CAPABILITIES for capability in requires),
        f"{label}: requires must contain distinct defined capabilities",
    )
    require(
        len(requires) == len(set(requires)),
        f"{label}: requires must not contain duplicates",
    )
    return profiles


def validate_mcp(value: object, label: str) -> None:
    require(isinstance(value, dict), f"{label}: MCP catalogue must be an object")
    require(
        set(value).issubset({"$schema", "mcpServers"}) and "mcpServers" in value,
        f"{label}: MCP catalogue has unknown or missing properties",
    )
    servers = value["mcpServers"]
    require(isinstance(servers, dict), f"{label}: mcpServers must be an object")
    for name, server in servers.items():
        require(
            isinstance(name, str) and PROFILE_NAME.fullmatch(name),
            f"{label}: unsafe MCP server name {name!r}",
        )
        require(isinstance(server, dict), f"{label}: server {name} must be an object")
        server_type = server.get("type")
        if server_type == "stdio":
            require(
                set(server).issubset({"type", "command", "args", "env"})
                and isinstance(server.get("command"), str)
                and bool(server["command"]),
                f"{label}: stdio server {name} has invalid fields",
            )
            args = server.get("args", [])
            require(
                isinstance(args, list) and all(isinstance(argument, str) for argument in args),
                f"{label}: stdio server {name} has invalid args",
            )
            environment = server.get("env", {})
            require(isinstance(environment, dict), f"{label}: stdio server {name} has invalid env")
            for key, reference in environment.items():
                require(
                    isinstance(key, str)
                    and ENVIRONMENT_NAME.fullmatch(key)
                    and isinstance(reference, str)
                    and ENVIRONMENT_REFERENCE.fullmatch(reference),
                    f"{label}: stdio server {name} has an invalid environment reference",
                )
        elif server_type == "remote":
            require(
                set(server).issubset({"type", "url", "headers"})
                and isinstance(server.get("url"), str),
                f"{label}: remote server {name} has invalid fields",
            )
            parsed_url = urlparse(server["url"])
            require(
                parsed_url.scheme == "https" and bool(parsed_url.netloc),
                f"{label}: remote server {name} has an invalid URL",
            )
            headers = server.get("headers", {})
            require(isinstance(headers, dict), f"{label}: remote server {name} has invalid headers")
            for key, reference in headers.items():
                require(
                    isinstance(key, str)
                    and HEADER_NAME.fullmatch(key)
                    and isinstance(reference, str)
                    and ENVIRONMENT_REFERENCE.fullmatch(reference),
                    f"{label}: remote server {name} has an invalid header reference",
                )
        else:
            raise ConformanceError(f"{label}: server {name} has an invalid type")


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except (OSError, RuntimeError, ValueError):
        return False
    return True


def validate_skills(skills_root: Path, label: str) -> None:
    require(skills_root.is_dir(), f"{label}: skills profile requires a skills directory")
    for skill in skills_root.iterdir():
        require(
            skill.is_dir() and PROFILE_NAME.fullmatch(skill.name),
            f"{label}: unsafe skill name or path {skill.name!r}",
        )
        require(
            is_within(skill, skills_root),
            f"{label}: skill path escapes the skills directory: {skill}",
        )
        skill_file = skill / "SKILL.md"
        require(skill_file.is_file(), f"{label}: skill {skill.name} lacks SKILL.md")
        require(
            is_within(skill_file, skill),
            f"{label}: skill path escapes its directory: {skill_file}",
        )
        for supporting_file in skill.rglob("*"):
            require(
                is_within(supporting_file, skill),
                f"{label}: supporting path escapes its skill directory: {supporting_file}",
            )


def validate_tree(root: Path) -> None:
    agents = root / ".agents"
    label = str(root.relative_to(SPEC_ROOT))
    profiles = validate_manifest(load_json(agents / "manifest.json"), label)
    if "mcp" in profiles:
        validate_mcp(load_json(agents / "tools" / "mcp.json"), label)
    if "skills" in profiles:
        validate_skills(agents / "skills", label)


def validate_schema_documents() -> None:
    manifest_schema = load_json(SPEC_ROOT / "spec/1.0/schemas/manifest.schema.json")
    mcp_schema = load_json(SPEC_ROOT / "spec/1.0/schemas/mcp.schema.json")
    require(
        isinstance(manifest_schema, dict)
        and manifest_schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
        "manifest schema has an invalid 2020-12 declaration",
    )
    require(
        isinstance(mcp_schema, dict)
        and mcp_schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
        "MCP schema has an invalid 2020-12 identifier",
    )


def validate_canonical_manifest() -> None:
    canonical = load_json(SPEC_ROOT / "conformance/fixtures/canonical-manifest.json")
    validate_manifest(canonical, "canonical starter manifest")


def validate_repository_starter() -> None:
    agents = SPEC_ROOT / ".agents"
    profiles = validate_manifest(load_json(agents / "manifest.json"), "SPEC starter")
    require(
        profiles == ["instructions"],
        "SPEC starter: only its checked-in AGENTS.md is selected",
    )
    require((agents / "AGENTS.md").is_file(), "SPEC starter: AGENTS.md is missing")
    validate_tree(SPEC_ROOT)


def validate_independent_selection(root: Path, profile: str) -> None:
    agents = root / ".agents"
    label = str(root.relative_to(SPEC_ROOT))
    profiles = validate_manifest(load_json(agents / "manifest.json"), label)
    require(profiles == [profile], f"{label}: expected only the {profile} profile")
    has_instructions = (agents / "AGENTS.md").is_file()
    has_mcp = (agents / "tools" / "mcp.json").is_file()
    has_skills = (agents / "skills").is_dir()
    expected = {
        "instructions": (True, False, False),
        "mcp": (False, True, False),
        "skills": (False, False, True),
    }[profile]
    require(
        (has_instructions, has_mcp, has_skills) == expected,
        f"{label}: content does not match its selected profile",
    )
    validate_tree(root)


def expect_valid(label: str, check: object) -> bool:
    try:
        check()
    except (ConformanceError, OSError, ValueError) as error:
        print(f"FAIL {label}: {error}")
        return False
    print(f"PASS {label}")
    return True


def expect_invalid(label: str, check: object) -> bool:
    try:
        check()
    except (ConformanceError, OSError, ValueError):
        print(f"PASS {label}")
        return True
    print(f"FAIL {label}: fixture was accepted")
    return False


def main() -> int:
    checks = []
    checks.append(expect_valid("schema JSON", validate_schema_documents))
    checks.append(expect_valid("canonical starter manifest", validate_canonical_manifest))
    checks.append(expect_valid("SPEC starter tree", validate_repository_starter))

    checks.append(expect_valid("basic example", lambda: validate_tree(SPEC_ROOT / "examples/basic")))
    for name in ("instructions", "mcp", "skills"):
        root = SPEC_ROOT / f"conformance/fixtures/selection-{name}"
        checks.append(
            expect_valid(
                f"independent {name} selection",
                lambda root=root, name=name: validate_independent_selection(root, name),
            )
        )

    for path in sorted((SPEC_ROOT / "examples/invalid").glob("manifest-*.json")):
        checks.append(
            expect_invalid(
                f"invalid manifest {path.name}",
                lambda path=path: validate_manifest(load_json(path), str(path)),
            )
        )
    for path in sorted((SPEC_ROOT / "examples/invalid").glob("mcp-*.json")):
        checks.append(
            expect_invalid(
                f"invalid MCP {path.name}",
                lambda path=path: validate_mcp(load_json(path), str(path)),
            )
        )
    for name in ("unsafe-skill-name", "unsafe-skill-path"):
        root = SPEC_ROOT / f"conformance/fixtures/invalid/{name}"
        checks.append(expect_invalid(f"invalid {name}", lambda root=root: validate_tree(root)))

    passed = sum(checks)
    print(f"{passed}/{len(checks)} conformance checks passed")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
