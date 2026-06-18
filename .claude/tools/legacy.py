"""One-time config upgrades — quarantined from linear.py's current behaviour.

These migrate formats that predate stride's current config: the legacy
`.linear_project` pin (superseded by `.stride.json`) and pre-`focus`
configs. They run from `/linear:setup` and have recovery runbooks under
`.claude/commands/linear/recovery/`. Kept apart so `linear.py` reads as
what stride does now, not what it once needed to upgrade from.

The dependency points one way — legacy → current — never the reverse.
"""

from linear import (
    DEFAULT_FOCUS,
    LinearError,
    STRIDE_CONFIG_PATH,
    project_config,
    write_config,
)

LEGACY_CONFIG_PATH = STRIDE_CONFIG_PATH.parent / ".linear_project"


def migrate_from_legacy() -> dict:
    if not LEGACY_CONFIG_PATH.exists():
        return {}
    config = parse_legacy_config(LEGACY_CONFIG_PATH.read_text())
    require_project(config)
    write_config(config)
    LEGACY_CONFIG_PATH.unlink()
    return config


def parse_legacy_config(text: str) -> dict:
    lines = [
        s
        for s in (r.strip() for r in text.splitlines())
        if s and not s.startswith("#")
    ]
    config = {
        k.strip(): v.strip()
        for line in lines
        if "=" in line
        for k, v in [line.split("=", 1)]
    }
    if lines and "=" not in lines[0]:
        config.setdefault("project", lines[0])
    return config


def require_project(config: dict):
    if not config.get("project"):
        raise LinearError(
            f"{LEGACY_CONFIG_PATH} is malformed (no project found) — left in "
            "place. Fix it or delete it and re-run /linear:setup."
        )


def backfill_focus() -> dict:
    config = project_config()
    if config and "focus" not in config:
        config["focus"] = DEFAULT_FOCUS
        write_config(config)
    return config
