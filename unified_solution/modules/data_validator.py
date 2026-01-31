"""Validation logic for extracted cube data."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from .. import config


EXPECTED_FIELDS = [
    "cube_mark_prefix",
    "cube_number",
    "cube_suffix",
    "report_number",
    "date_cast",
    "compressive_strength",
    "pour_location",
]

CRITICAL_FIELDS = [
    "cube_mark_prefix",
    "cube_number",
    "cube_suffix",
    "compressive_strength",
]


def validate_cube_data(cube_data: List[Dict[str, str]]) -> Dict[str, object]:
    """
    Validate extracted cube data for common issues.

    Returns:
        {
            "errors": [],      # Critical issues
            "warnings": [],    # Non-critical issues
            "stats": {}        # Summary statistics
        }
    """
    errors: List[str] = []
    warnings: List[str] = []

    seen_marks = set()
    counts_by_type: Dict[str, int] = {}
    strength_by_type: Dict[str, List[float]] = {}

    for idx, cube in enumerate(cube_data, start=1):
        missing = [
            field
            for field in EXPECTED_FIELDS
            if field not in cube or cube.get(field) in ("", None)
        ]
        for field in missing:
            message = f"Row {idx}: missing {field}"
            if field in CRITICAL_FIELDS:
                errors.append(message)
            else:
                warnings.append(message)

        prefix = cube.get("cube_mark_prefix", "")
        number = cube.get("cube_number", "")
        suffix = cube.get("cube_suffix", "")
        mark = f"{prefix}{number}{suffix}"
        if mark:
            if mark in seen_marks:
                warnings.append(f"Row {idx}: duplicate cube mark '{mark}'")
            seen_marks.add(mark)

        strength_value = cube.get("compressive_strength", "")
        strength = _parse_strength(strength_value)
        if strength is None:
            if strength_value not in ("", None):
                warnings.append(
                    f"Row {idx}: invalid compressive strength '{strength_value}'"
                )
        else:
            if strength < config.MIN_STRENGTH or strength > config.MAX_STRENGTH:
                warnings.append(
                    f"Row {idx}: strength {strength} MPa outside "
                    f"{config.MIN_STRENGTH}-{config.MAX_STRENGTH} MPa"
                )

        date_cast = cube.get("date_cast", "")
        if date_cast:
            if not _is_valid_date(date_cast):
                warnings.append(f"Row {idx}: invalid date_cast '{date_cast}'")

        cube_type = get_concrete_type(prefix)
        counts_by_type[cube_type] = counts_by_type.get(cube_type, 0) + 1
        if strength is not None:
            strength_by_type.setdefault(cube_type, []).append(strength)

    stats = {
        "total_cubes": len(cube_data),
        "by_type": counts_by_type,
        "avg_strength": {
            t: round(sum(vals) / len(vals), 2)
            for t, vals in strength_by_type.items()
            if vals
        },
    }

    return {"errors": errors, "warnings": warnings, "stats": stats}


def _parse_strength(value: Any) -> Optional[float]:
    if value in ("", None):
        return None
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def _is_valid_date(value: str) -> bool:
    try:
        datetime.strptime(value.strip().title(), "%d-%b-%Y")
        return True
    except ValueError:
        return False


def get_concrete_type(cube_mark_prefix: str) -> str:
    """Determine concrete type from cube mark prefix."""
    mark = (cube_mark_prefix or "").upper()
    is45 = "45D" in mark
    is60 = "60D" in mark
    is_wp = "WP" in mark
    if is45 and is_wp:
        return "45DWP"
    if is60 and is_wp:
        return "60DWP"
    if is45:
        return "45D"
    if is60:
        return "60D"
    return "Unknown"
