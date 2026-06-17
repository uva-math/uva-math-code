"""Configuration and environment helpers for UVA arXiv scripts.

This module intentionally avoids a hard dependency on PyYAML. If PyYAML is
available it is used; otherwise a small parser handles the limited YAML shapes
used by the UVA arXiv config and manual data files.
"""

from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = Path(__file__).with_name("config.yml")
CACHE_DIR = Path(__file__).with_name("cache")
DATA_DIR = Path(__file__).with_name("data")
DOTENV_PATH = REPO_ROOT / ".env"

PATH_ENV_OVERRIDES = {
    "arxiv_db": "ARXIV_DB",
    "arxiv_sources_dir": "ARXIV_SOURCES_DIR",
}

SAFE_ENV_KEYS = (
    "ARXIV_DB",
    "ARXIV_SOURCES_DIR",
    "S2_API_KEY",
    "SEMANTIC_SCHOLAR_API_KEY",
    "CROSSREF_MAILTO",
    "CROSSREF_API_KEY",
    "OPENALEX_EMAIL",
)

REQUIRED_DATA_FILES = (
    "aliases.yml",
    "appointments_overrides.yml",
    "people_manual.yml",
    "affiliation_patterns.yml",
    "accepted_matches.yml",
    "rejected_matches.yml",
    "ambiguous_people.yml",
)


class ConfigError(RuntimeError):
    """Raised when the local UVA arXiv configuration is invalid."""


@dataclass(frozen=True)
class UvaArxivConfig:
    repo_root: Path
    config_path: Path
    raw: dict[str, Any]
    arxiv_db: Path
    arxiv_sources_dir: Path
    homepage_arxiv_scripts: Path
    initial_arxiv_start_date: str
    site_endpoint: str
    people_dirs: dict[str, Path]
    cache_dir: Path
    data_dir: Path


def _strip_comment(line: str) -> str:
    quote: str | None = None
    escaped = False
    for index, char in enumerate(line):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char in {"'", '"'}:
            if quote == char:
                quote = None
            elif quote is None:
                quote = char
            continue
        if char == "#" and quote is None:
            return line[:index]
    return line


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    if value in {"null", "Null", "NULL", "~"}:
        return None
    if value in {"true", "True", "TRUE"}:
        return True
    if value in {"false", "False", "FALSE"}:
        return False
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(part) for part in inner.split(",")]
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def _simple_yaml_lines(text: str) -> list[tuple[int, str, int]]:
    lines: list[tuple[int, str, int]] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if raw_line.strip() == "" or raw_line.lstrip().startswith("#"):
            continue
        if raw_line.startswith("\t"):
            raise ConfigError(f"Tabs are not supported in config YAML at line {line_number}")

        uncommented = _strip_comment(raw_line).rstrip()
        if not uncommented.strip():
            continue

        indent = len(uncommented) - len(uncommented.lstrip(" "))
        lines.append((indent, uncommented.strip(), line_number))
    return lines


def _parse_simple_yaml(text: str) -> Any:
    stripped_text = text.strip()
    if not stripped_text:
        return {}
    if stripped_text == "{}":
        return {}
    if stripped_text == "[]":
        return []
    lines = _simple_yaml_lines(text)
    if not lines:
        return {}
    if len(lines) == 1 and lines[0][1] == "{}":
        return {}
    if len(lines) == 1 and lines[0][1] == "[]":
        return []
    parsed, next_index = _parse_yaml_block(lines, 0, lines[0][0])
    if next_index != len(lines):
        _indent, stripped, line_number = lines[next_index]
        raise ConfigError(f"Unexpected YAML content at line {line_number}: {stripped}")
    return parsed


def _parse_yaml_mapping(
    lines: list[tuple[int, str, int]],
    index: int,
    indent: int,
) -> tuple[dict[str, Any], int]:
    parsed: dict[str, Any] = {}
    while index < len(lines):
        line_indent, stripped, line_number = lines[index]
        if line_indent < indent:
            break
        if line_indent > indent:
            raise ConfigError(f"Unexpected YAML indentation at line {line_number}: {stripped}")
        if stripped.startswith("- "):
            break
        if ":" not in stripped:
            raise ConfigError(f"Expected key/value YAML at line {line_number}: {stripped}")

        key, value = stripped.split(":", 1)
        key = key.strip()
        if not key:
            raise ConfigError(f"Empty YAML key at line {line_number}")

        if value.strip() == "":
            index += 1
            if index >= len(lines) or lines[index][0] < indent:
                parsed[key] = None
                continue
            child_indent = lines[index][0]
            if child_indent == indent and lines[index][1].startswith("- "):
                parsed[key], index = _parse_yaml_list(lines, index, child_indent)
            elif child_indent > indent:
                parsed[key], index = _parse_yaml_block(lines, index, child_indent)
            else:
                parsed[key] = None
        else:
            scalar_value = value.strip()
            if scalar_value in {"|", ">"}:
                index += 1
                block_lines: list[str] = []
                while index < len(lines) and lines[index][0] > indent:
                    _child_indent, child_stripped, _child_line_number = lines[index]
                    block_lines.append(child_stripped)
                    index += 1
                separator = "\n" if scalar_value == "|" else " "
                parsed[key] = separator.join(block_lines)
            else:
                parsed[key] = _parse_scalar(value)
                index += 1
    return parsed, index


def _parse_yaml_list(
    lines: list[tuple[int, str, int]],
    index: int,
    indent: int,
) -> tuple[list[Any], int]:
    parsed: list[Any] = []
    while index < len(lines):
        line_indent, stripped, line_number = lines[index]
        if line_indent < indent:
            break
        if line_indent > indent:
            raise ConfigError(f"Unexpected YAML indentation at line {line_number}: {stripped}")
        if not stripped.startswith("- "):
            break

        item = stripped[2:].strip()
        index += 1
        if item == "":
            if index < len(lines) and lines[index][0] > indent:
                value, index = _parse_yaml_block(lines, index, lines[index][0])
            else:
                value = None
            parsed.append(value)
            continue

        if ":" in item:
            key, value = item.split(":", 1)
            item_mapping: dict[str, Any] = {
                key.strip(): _parse_scalar(value) if value.strip() else None
            }
            if index < len(lines) and lines[index][0] > indent:
                nested, index = _parse_yaml_mapping(lines, index, lines[index][0])
                item_mapping.update(nested)
            parsed.append(item_mapping)
        else:
            parsed.append(_parse_scalar(item))
    return parsed, index


def _parse_yaml_block(
    lines: list[tuple[int, str, int]],
    index: int,
    indent: int,
) -> tuple[Any, int]:
    if lines[index][1].startswith("- "):
        return _parse_yaml_list(lines, index, indent)
    return _parse_yaml_mapping(lines, index, indent)


def load_yaml_text(text: str, source: str = "YAML") -> Any:
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError:
        return _parse_simple_yaml(text)

    try:
        loaded = yaml.safe_load(text)
    except yaml.YAMLError:
        return _parse_simple_yaml(text)
    if loaded is None:
        return {}
    return loaded


def load_yaml_mapping_text(text: str, source: str = "YAML") -> dict[str, Any]:
    loaded = load_yaml_text(text, source)
    if not isinstance(loaded, dict):
        raise ConfigError(f"Expected mapping at top level of {source}")
    return loaded


def load_yaml_file(path: Path) -> Any:
    return load_yaml_text(path.read_text(encoding="utf-8"), str(path))


def load_yaml_mapping_file(path: Path) -> dict[str, Any]:
    return load_yaml_mapping_text(path.read_text(encoding="utf-8"), str(path))


def _resolve_path(value: str | os.PathLike[str], repo_root: Path = REPO_ROOT) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return repo_root / path


def load_dotenv(path: Path = DOTENV_PATH, override: bool = False) -> dict[str, bool]:
    """Load a simple KEY=VALUE dotenv file without returning secret values."""
    loaded: dict[str, bool] = {}
    if not path.exists():
        return loaded

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = _strip_comment(raw_line).strip()
        if not line:
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            continue
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        if override or key not in os.environ:
            os.environ[key] = value
        loaded[key] = True
    return loaded


def normalize_api_env() -> None:
    if not os.environ.get("S2_API_KEY") and os.environ.get("SEMANTIC_SCHOLAR_API_KEY"):
        os.environ["S2_API_KEY"] = os.environ["SEMANTIC_SCHOLAR_API_KEY"]


def safe_env_status(keys: tuple[str, ...] = SAFE_ENV_KEYS) -> dict[str, bool]:
    normalize_api_env()
    return {key: bool(os.environ.get(key)) for key in keys}


def dotenv_is_gitignored(repo_root: Path = REPO_ROOT) -> bool:
    gitignore = repo_root / ".gitignore"
    if not gitignore.exists():
        return False
    for raw_line in gitignore.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line in {".env", "*.env", ".env*"}:
            return True
    return False


def ensure_local_dirs(cache_dir: Path = CACHE_DIR, data_dir: Path = DATA_DIR) -> tuple[Path, Path]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir, data_dir


def missing_data_files(data_dir: Path = DATA_DIR) -> list[Path]:
    return [data_dir / name for name in REQUIRED_DATA_FILES if not (data_dir / name).exists()]


def load_config(
    config_path: Path = CONFIG_PATH,
    repo_root: Path = REPO_ROOT,
    load_env_file: bool = True,
    ensure_dirs: bool = False,
) -> UvaArxivConfig:
    if load_env_file:
        load_dotenv(repo_root / ".env")
    normalize_api_env()

    raw = load_yaml_mapping_file(config_path)
    for key, env_key in PATH_ENV_OVERRIDES.items():
        if os.environ.get(env_key):
            raw[key] = os.environ[env_key]

    required = (
        "arxiv_db",
        "arxiv_sources_dir",
        "homepage_arxiv_scripts",
        "initial_arxiv_start_date",
        "site_endpoint",
        "people_dirs",
    )
    missing = [key for key in required if key not in raw]
    if missing:
        raise ConfigError(f"Missing required config keys: {', '.join(missing)}")
    if not isinstance(raw["people_dirs"], dict):
        raise ConfigError("people_dirs must be a mapping")

    if ensure_dirs:
        ensure_local_dirs()

    return UvaArxivConfig(
        repo_root=repo_root,
        config_path=config_path,
        raw=raw,
        arxiv_db=_resolve_path(str(raw["arxiv_db"]), repo_root),
        arxiv_sources_dir=_resolve_path(str(raw["arxiv_sources_dir"]), repo_root),
        homepage_arxiv_scripts=_resolve_path(str(raw["homepage_arxiv_scripts"]), repo_root),
        initial_arxiv_start_date=str(raw["initial_arxiv_start_date"]),
        site_endpoint=str(raw["site_endpoint"]),
        people_dirs={
            key: _resolve_path(str(value), repo_root)
            for key, value in raw["people_dirs"].items()
        },
        cache_dir=CACHE_DIR,
        data_dir=DATA_DIR,
    )


def _format_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-check UVA arXiv config loading.")
    parser.add_argument("--no-env", action="store_true", help="Do not load ignored .env values.")
    args = parser.parse_args()

    config = load_config(load_env_file=not args.no_env, ensure_dirs=True)
    missing = missing_data_files(config.data_dir)

    print("config: ok")
    print(f"config_path: {_format_path(config.config_path)}")
    print(f"cache_dir: {_format_path(config.cache_dir)}")
    print(f"data_dir: {_format_path(config.data_dir)}")
    print(f"dotenv_ignored: {dotenv_is_gitignored(config.repo_root)}")
    for key, present in safe_env_status().items():
        print(f"{key}: {'present' if present else 'missing'}")
    if missing:
        print("missing_data_files: " + ", ".join(_format_path(path) for path in missing))
        return 1
    print("data_files: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
