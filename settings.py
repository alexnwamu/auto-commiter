"""Persistent settings manager for auto-commiter.

Stores user preferences like default style, model preferences, and flags
in a JSON config file in the user's home directory.
"""

import json
from pathlib import Path
from typing import Any, Optional


SETTINGS_DIR = Path.home() / ".autocommit"
SETTINGS_FILE = SETTINGS_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "style": "conventional",
    "auto_push": False,
    "auto_stage": True,
    "use_cache": True,
    "model": "auto",  # 'auto', 'rule-based', 'openai'
    "max_diff_for_rules": 5000,
    "show_diff_preview": False,
    "confirm_before_commit": True,
}


def _ensure_settings_dir() -> None:
    """Create settings directory if it doesn't exist."""
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)


def _load_settings() -> dict:
    """Load settings from disk."""
    _ensure_settings_dir()
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**DEFAULT_SETTINGS, **saved}
        except (json.JSONDecodeError, IOError):
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()


def _save_settings(settings: dict) -> None:
    """Save settings to disk."""
    _ensure_settings_dir()
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


def get_setting(key: str, default: Any = None) -> Any:
    """Get a specific setting value.
    
    Args:
        key: The setting key
        default: Default value if key doesn't exist
        
    Returns:
        The setting value
    """
    settings = _load_settings()
    return settings.get(key, default if default is not None else DEFAULT_SETTINGS.get(key))


def set_setting(key: str, value: Any) -> None:
    """Set a specific setting value.
    
    Args:
        key: The setting key
        value: The value to set
    """
    settings = _load_settings()
    settings[key] = value
    _save_settings(settings)
    print(f"[settings] Set {key} = {value}")


def get_all_settings() -> dict:
    """Get all current settings."""
    return _load_settings()


def reset_settings() -> None:
    """Reset all settings to defaults."""
    _save_settings(DEFAULT_SETTINGS.copy())
    print("[settings] Settings reset to defaults.")


def update_settings(**kwargs) -> None:
    """Update multiple settings at once.
    
    Args:
        **kwargs: Key-value pairs of settings to update
    """
    settings = _load_settings()
    for key, value in kwargs.items():
        if key in DEFAULT_SETTINGS:
            settings[key] = value
    _save_settings(settings)
