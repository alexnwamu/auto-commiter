"""Cache module for storing and retrieving commit messages based on diff hashes.

Uses a local JSON file to cache commit messages for similar diffs,
reducing API calls and improving response time.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Optional
from datetime import datetime


CACHE_DIR = Path.home() / ".autocommit"
CACHE_FILE = CACHE_DIR / "cache.json"
MAX_CACHE_ENTRIES = 500
CACHE_TTL_DAYS = 30


def _ensure_cache_dir() -> None:
    """Create cache directory if it doesn't exist."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _compute_diff_hash(diff: str) -> str:
    """Compute a normalized hash of a diff for cache lookup.
    
    Normalizes the diff by:
    - Removing timestamps and dates that may vary
    - Stripping excessive whitespace
    - Sorting file sections for consistency
    """
    lines = []
    for line in diff.splitlines():
        # Skip lines that often change between identical changes
        if line.startswith("index ") or line.startswith("@@"):
            continue
        # Normalize whitespace
        stripped = line.strip()
        if stripped:
            lines.append(stripped)
    
    normalized = "\n".join(sorted(lines))
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def _load_cache() -> dict:
    """Load cache from disk."""
    _ensure_cache_dir()
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"entries": {}, "stats": {"hits": 0, "misses": 0}}
    return {"entries": {}, "stats": {"hits": 0, "misses": 0}}


def _save_cache(cache: dict) -> None:
    """Save cache to disk."""
    _ensure_cache_dir()
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def _cleanup_old_entries(cache: dict) -> dict:
    """Remove old cache entries and limit cache size."""
    entries = cache.get("entries", {})
    now = datetime.now().timestamp()
    ttl_seconds = CACHE_TTL_DAYS * 24 * 60 * 60
    
    # Remove expired entries
    valid_entries = {
        k: v for k, v in entries.items()
        if now - v.get("timestamp", 0) < ttl_seconds
    }
    
    # If still too many, remove oldest
    if len(valid_entries) > MAX_CACHE_ENTRIES:
        sorted_entries = sorted(
            valid_entries.items(),
            key=lambda x: x[1].get("timestamp", 0),
            reverse=True
        )
        valid_entries = dict(sorted_entries[:MAX_CACHE_ENTRIES])
    
    cache["entries"] = valid_entries
    return cache


def get_cached_message(diff: str, style: str) -> Optional[str]:
    """Look up a cached commit message for the given diff and style.
    
    Args:
        diff: The git diff content
        style: The commit message style
        
    Returns:
        Cached commit message if found, None otherwise
    """
    cache = _load_cache()
    diff_hash = _compute_diff_hash(diff)
    cache_key = f"{diff_hash}:{style}"
    
    entry = cache.get("entries", {}).get(cache_key)
    if entry:
        cache["stats"]["hits"] = cache["stats"].get("hits", 0) + 1
        _save_cache(cache)
        print(f"[cache] Cache hit! Using cached message (hash: {diff_hash[:8]}...)")
        return entry.get("message")
    
    cache["stats"]["misses"] = cache["stats"].get("misses", 0) + 1
    _save_cache(cache)
    return None


def cache_message(diff: str, style: str, message: str) -> None:
    """Store a commit message in the cache.
    
    Args:
        diff: The git diff content
        style: The commit message style
        message: The generated commit message
    """
    cache = _load_cache()
    cache = _cleanup_old_entries(cache)
    
    diff_hash = _compute_diff_hash(diff)
    cache_key = f"{diff_hash}:{style}"
    
    cache.setdefault("entries", {})[cache_key] = {
        "message": message,
        "timestamp": datetime.now().timestamp(),
        "style": style,
    }
    
    _save_cache(cache)
    print(f"[cache] Cached message (hash: {diff_hash[:8]}...)")


def get_cache_stats() -> dict:
    """Get cache statistics."""
    cache = _load_cache()
    stats = cache.get("stats", {})
    entries = cache.get("entries", {})
    return {
        "total_entries": len(entries),
        "hits": stats.get("hits", 0),
        "misses": stats.get("misses", 0),
        "hit_rate": (
            stats.get("hits", 0) / max(1, stats.get("hits", 0) + stats.get("misses", 0))
        ) * 100,
    }


def clear_cache() -> None:
    """Clear all cached entries."""
    _ensure_cache_dir()
    if CACHE_FILE.exists():
        os.remove(CACHE_FILE)
    print("[cache] Cache cleared.")
