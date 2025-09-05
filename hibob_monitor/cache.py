"""
Cache management for employee data with smart deduplication
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from .models import EmployeeList

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Configuration for cache management."""

    max_entries: int = 5
    deduplicate_consecutive: bool = True


def _deduplicate_consecutive(entries: list[EmployeeList]) -> list[EmployeeList]:
    """Remove consecutive duplicate entries, keeping only first and last."""
    if not entries:
        return entries

    deduplicated = []
    current_group = [entries[0]]

    for entry in entries[1:]:
        if entry == current_group[-1]:  # Same employee data
            current_group.append(entry)
        else:
            # End of current group, add first and last if different
            if len(current_group) == 1:
                deduplicated.append(current_group[0])
            else:
                deduplicated.append(current_group[0])  # First (oldest)
                deduplicated.append(current_group[-1])  # Last (newest)
            current_group = [entry]

    # Handle the last group
    if len(current_group) == 1:
        deduplicated.append(current_group[0])
    else:
        deduplicated.append(current_group[0])  # First (oldest)
        deduplicated.append(current_group[-1])  # Last (newest)

    return deduplicated


def load_cache(cache_file: Path) -> list[EmployeeList]:
    """Load cached employee data history from JSON file."""
    if not cache_file.exists():
        return []

    try:
        with cache_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
            entries_data = data.get("entries", [])
            return [EmployeeList.from_dict(entry_data) for entry_data in entries_data]
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("⚠️  Warning: Could not load cache from %s: %s", cache_file, e)
        return []


def get_latest_cache(cache_file: Path) -> EmployeeList | None:
    """Get the most recent cached employee list."""
    entries = load_cache(cache_file)
    return entries[-1] if entries else None


def save_cache(
    employee_list: EmployeeList, cache_file: Path, config: CacheConfig | None = None
) -> None:
    """Save employee data to cache with smart deduplication."""
    if config is None:
        config = CacheConfig()

    try:
        # Load existing cache
        existing_entries = load_cache(cache_file)

        # Add new entry
        all_entries = [*existing_entries, employee_list]

        # Apply deduplication if enabled
        if config.deduplicate_consecutive:
            all_entries = _deduplicate_consecutive(all_entries)

        # Trim to max entries (keep most recent)
        if len(all_entries) > config.max_entries:
            all_entries = all_entries[-config.max_entries :]

        # Create directory if it doesn't exist
        cache_file.parent.mkdir(parents=True, exist_ok=True)

        # Save to file
        cache_data = {
            "cache_config": {
                "max_entries": config.max_entries,
                "deduplicate_consecutive": config.deduplicate_consecutive,
            },
            "entries": [entry.to_dict() for entry in all_entries],
        }

        with cache_file.open("w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)

    except OSError as e:
        logger.warning("⚠️  Warning: Could not save cache to %s: %s", cache_file, e)
