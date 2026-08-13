#!/usr/bin/env python3
"""Standard-library conformance checks for the Open-Dot-Agents 1.0 fixtures."""

from __future__ import annotations

import json
import re
import sys
from argparse import ArgumentParser
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker


SPEC_ROOT = Path(__file__).resolve().parent.parent
PROFILE_NAME = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
ENVIRONMENT_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
HEADER_NAME = re.compile(r"^[!#$%&'*+\-.^_`|~0-9A-Za-z]+$")
ENVIRONMENT_REFERENCE = re.compile(
    r"^urn:open-dot-agents:env:[A-Za-z_][A-Za-z0-9_]*$"
)
CAPABILITIES = {
    "instructions",
    "instructions.scoped",
    "skills",
    "mcp.stdio",
    "mcp.remote",
    "mcp.envRef",
}
PROFILES = {"tools", "skills"}


class ConformanceError(ValueError):
    """A fixture violates a portable 1.0 rule."""


def schema_validate(value: object, schema_name: str, label: str) -> None:
    schema = load_json(SPEC_ROOT / "spec/1.0/schemas" / schema_name)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        raise ConformanceError(f"{label}: JSON Schema: {errors[0].message}")


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ConformanceError(f"{path}: invalid JSON: {error}") from error


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ConformanceError(message)


def validate_manifest(value: object, label: str) -> list[str]:
    schema_validate(value, "manifest.schema.json", label)
    require(isinstance(value, dict), f"{label}: manifest must be an object")
    require(value.get("version") == "1.0.0", f"{label}: version must be 1.0.0")

    schema = value.get("$schema")
    require(
        schema is None or isinstance(schema, str),
        f"{label}: $schema must be a string when present",
    )
    profiles = value.get("profiles")
    require(
        isinstance(profiles, list),
        f"{label}: profiles must be an array",
    )
    require(
        all(isinstance(profile, str) and PROFILE_NAME.fullmatch(profile) for profile in profiles),
        f"{label}: profiles must contain portable profile strings",
    )
    require(
        len(profiles) == len(set(profiles)),
        f"{label}: profiles must not contain duplicates",
    )
    require(
        set(profiles).issubset(PROFILES),
        f"{label}: profiles contain an unsupported 1.0 profile",
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
    schema_validate(value, "mcp.schema.json", label)
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
    canonical_instructions = agents / "AGENTS.md"
    require(
        canonical_instructions.is_file() and is_within(canonical_instructions, agents),
        f"{label}: canonical .agents/AGENTS.md is missing or unsafe",
    )
    for instructions in root.rglob("AGENTS.md"):
        require(
            instructions.is_file() and is_within(instructions, root),
            f"{label}: unsafe AGENTS.md path {instructions}",
        )
    if "tools" in profiles:
        validate_mcp(load_json(agents / "tools" / "mcp.json"), label)
    if "skills" in profiles:
        validate_skills(agents / "skills", label)


def validate_schema_documents() -> None:
    manifest_schema = load_json(SPEC_ROOT / "spec/1.0/schemas/manifest.schema.json")
    mcp_schema = load_json(SPEC_ROOT / "spec/1.0/schemas/mcp.schema.json")
    result_schema = load_json(
        SPEC_ROOT / "spec/1.0/schemas/conformance-result.schema.json"
    )
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
    require(
        isinstance(result_schema, dict)
        and result_schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
        "conformance result schema has an invalid 2020-12 declaration",
    )


def validate_canonical_manifest() -> None:
    canonical = load_json(SPEC_ROOT / "conformance/fixtures/canonical-manifest.json")
    validate_manifest(canonical, "canonical starter manifest")


def validate_repository_starter() -> None:
    agents = SPEC_ROOT / ".agents"
    profiles = validate_manifest(load_json(agents / "manifest.json"), "SPEC starter")
    require(
        profiles == [],
        "SPEC starter: no optional content profile is selected",
    )
    require((agents / "AGENTS.md").is_file(), "SPEC starter: canonical AGENTS.md is missing")
    validate_tree(SPEC_ROOT)


def validate_independent_selection(root: Path, profile: str) -> None:
    agents = root / ".agents"
    label = str(root.relative_to(SPEC_ROOT))
    profiles = validate_manifest(load_json(agents / "manifest.json"), label)
    require(profiles == [profile], f"{label}: expected only the {profile} profile")
    has_instructions = (agents / "AGENTS.md").is_file()
    has_tools = (agents / "tools" / "mcp.json").is_file()
    has_skills = (agents / "skills").is_dir()
    expected = {
        "tools": (True, True, False),
        "skills": (True, False, True),
    }[profile]
    require(
        (has_instructions, has_tools, has_skills) == expected,
        f"{label}: content does not match its selected profile",
    )
    validate_tree(root)


RESULTS: list[dict[str, object]] = []


def record(label: str, passed: bool, error: object | None = None) -> bool:
    result: dict[str, object] = {"id": label, "passed": passed}
    if error is not None:
        result["diagnostic"] = "ODA-CONFORMANCE-0001"
        result["message"] = str(error)
    RESULTS.append(result)
    return passed


def expect_valid(label: str, check: object, quiet: bool = False) -> bool:
    try:
        check()
    except (ConformanceError, OSError, ValueError) as error:
        if not quiet:
            print(f"FAIL {label}: {error}")
        return record(label, False, error)
    if not quiet:
        print(f"PASS {label}")
    return record(label, True)


def expect_invalid(label: str, check: object, quiet: bool = False) -> bool:
    try:
        check()
    except (ConformanceError, OSError, ValueError):
        if not quiet:
            print(f"PASS {label}")
        return record(label, True)
    error = "fixture was accepted"
    if not quiet:
        print(f"FAIL {label}: {error}")
    return record(label, False, error)


def main() -> int:
    parser = ArgumentParser()
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    quiet = args.format == "json"
    checks = []
    checks.append(expect_valid("schema-json", validate_schema_documents, quiet))
    checks.append(expect_valid("canonical-manifest", validate_canonical_manifest, quiet))
    checks.append(expect_valid("spec-starter", validate_repository_starter, quiet))

    checks.append(expect_valid("example-basic", lambda: validate_tree(SPEC_ROOT / "examples/basic"), quiet))
    checks.append(expect_valid(
        "baseline-instructions",
        lambda: validate_tree(SPEC_ROOT / "conformance/fixtures/baseline-instructions"),
        quiet,
    ))
    for name in ("tools", "skills"):
        root = SPEC_ROOT / f"conformance/fixtures/selection-{name}"
        checks.append(
            expect_valid(
                f"selection-{name}",
                lambda root=root, name=name: validate_independent_selection(root, name),
                quiet,
            )
        )

    for path in sorted((SPEC_ROOT / "examples/invalid").glob("manifest-*.json")):
        checks.append(
            expect_invalid(
                f"invalid-manifest-{path.stem}",
                lambda path=path: validate_manifest(load_json(path), str(path)),
                quiet,
            )
        )
    for path in sorted((SPEC_ROOT / "examples/invalid").glob("mcp-*.json")):
        checks.append(
            expect_invalid(
                f"invalid-mcp-{path.stem}",
                lambda path=path: validate_mcp(load_json(path), str(path)),
                quiet,
            )
        )
    for name in ("unsafe-skill-name", "unsafe-skill-path"):
        root = SPEC_ROOT / f"conformance/fixtures/invalid/{name}"
        checks.append(expect_invalid(f"invalid-{name}", lambda root=root: validate_tree(root), quiet))

    passed = sum(checks)
    if quiet:
        print(json.dumps({
            "schemaVersion": "1.0.0",
            "standardVersion": "1.0.0",
            "implementation": "open-dot-agents-python-runner",
            "implementationVersion": "1.0.0",
            "class": "repository",
            "passed": passed == len(checks),
            "checks": RESULTS,
        }, indent=2))
    else:
        print(f"{passed}/{len(checks)} conformance checks passed")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
