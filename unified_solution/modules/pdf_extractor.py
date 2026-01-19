"""PDF extraction logic for concrete cube reports."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import pdfplumber
except ImportError as exc:  # pragma: no cover - handled at runtime
    raise ImportError(
        "pdfplumber is required. Install with: pip install pdfplumber"
    ) from exc

logger = logging.getLogger(__name__)


def parse_cube_mark(cube_mark: str) -> Tuple[str, str, str]:
    """
    Split cube mark into prefix, number, and suffix components.

    Example:
        "20250621-45D-1A" -> ("20250621-45D-", "1", "A")
    """
    pattern = r"^(.+?-)(\d+)([A-Z])$"
    match = re.match(pattern, cube_mark or "")
    if match:
        return match.group(1), match.group(2), match.group(3)

    logger.warning("Could not parse cube mark '%s'", cube_mark)
    return cube_mark or "", "", ""


def extract_cubes_from_pdf(pdf_path: str) -> List[Dict[str, str]]:
    """
    Extract cube data from PDF report.

    Returns:
        List of dictionaries with keys:
        - cube_mark_prefix, cube_number, cube_suffix
        - report_number, date_cast, compressive_strength, pour_location
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    all_cubes: List[Dict[str, str]] = []
    try:
        with pdfplumber.open(str(path)) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                try:
                    page_text = page.extract_text() or ""
                except Exception as exc:
                    logger.warning(
                        "Failed to extract text from page %s: %s",
                        page_number,
                        exc,
                    )
                    continue

                cubes = _extract_all_cubes_from_text(page_text)
                if cubes:
                    logger.info("Page %s: %s cubes extracted", page_number, len(cubes))
                    all_cubes.extend(cubes)
                else:
                    logger.info("Page %s: no cubes found", page_number)
    except Exception as exc:  # pragma: no cover - external dependency errors
        raise RuntimeError(f"Failed to process PDF '{pdf_path}': {exc}") from exc

    if not all_cubes:
        raise ValueError("No cube data extracted from PDF")

    return all_cubes


def _extract_report_number(text: str) -> str:
    patterns = [
        r"Report\s+No\.?:?\s*([A-Z0-9]+)",
        r"Report\s+Number:?\s*([A-Z0-9]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


def _extract_date_cast(text: str) -> str:
    pattern = r"(?:Date\s+Cast\s*:\s*)(\d{2}-[A-Za-z]{3}-\d{4})"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1)
    return ""


def _extract_pour_location(text: str) -> str:
    patterns = [
        r"(?:Pour\sLocation|Location)\s*:\s*(.+?)(?=\nDate\sCast|\Z)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            location = match.group(1).strip()
            return " ".join(location.split())
    return ""


def _build_cube_record(
    prefix: str,
    number: str,
    suffix: str,
    report_number: str,
    date_cast: str,
    strength: str,
    pour_location: str,
) -> Dict[str, str]:
    return {
        "cube_mark_prefix": prefix,
        "cube_number": number,
        "cube_suffix": suffix,
        "report_number": report_number,
        "date_cast": date_cast,
        "compressive_strength": strength,
        "pour_location": pour_location,
    }


def _extract_all_cubes_from_text(page_text: str) -> List[Dict[str, str]]:
    if not page_text:
        return []

    cubes: List[Dict[str, str]] = []
    report_number = _extract_report_number(page_text)
    date_cast = _extract_date_cast(page_text)
    pour_location = _extract_pour_location(page_text)

    lines = page_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        case1_match = re.search(
            r"CU\d+\s+(\d{8}-\d+[A-Z]+-\d+[A-Z])\s+.*?\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+S\s+-",
            line,
        )
        if case1_match:
            full_cube_mark = case1_match.group(1)
            strength = case1_match.group(3)
            prefix, number, suffix = parse_cube_mark(full_cube_mark)
            cubes.append(
                _build_cube_record(
                    prefix,
                    number,
                    suffix,
                    report_number,
                    date_cast,
                    strength,
                    pour_location,
                )
            )
            i += 1
            continue

        case2_match = re.search(
            r"CU\d+\s+(\d{8}-\d+[A-Z]+-\d+)\s+.*?\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+S\s+-",
            line,
        )
        if case2_match:
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if len(next_line) == 1 and next_line.isalpha() and next_line.isupper():
                    cube_mark_base = case2_match.group(1)
                    strength = case2_match.group(3)
                    suffix = next_line
                    full_cube_mark = f"{cube_mark_base}{suffix}"
                    prefix, number, _ = parse_cube_mark(full_cube_mark)
                    cubes.append(
                        _build_cube_record(
                            prefix,
                            number,
                            suffix,
                            report_number,
                            date_cast,
                            strength,
                            pour_location,
                        )
                    )
                    i += 2
                    continue

        case3_match = re.search(
            r"CU\d+\s+(\d{8}-\d+[A-Z]+-)\s+.*?\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+S\s+-",
            line,
        )
        if case3_match:
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                id_match = re.match(r"(\d+)([A-Z])$", next_line)
                if id_match:
                    cube_mark_base = case3_match.group(1)
                    number = id_match.group(1)
                    suffix = id_match.group(2)
                    strength = case3_match.group(3)
                    cubes.append(
                        _build_cube_record(
                            cube_mark_base,
                            number,
                            suffix,
                            report_number,
                            date_cast,
                            strength,
                            pour_location,
                        )
                    )
                    i += 2
                    continue

        case4_match = re.search(
            r"CU\d+\s+(\d{8}-\d+[A-Z]+)\s+.*?\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+S\s+-",
            line,
        )
        if case4_match:
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                id_match = re.match(r"-\s*(\d+)([A-Z])$", next_line)
                if id_match:
                    cube_mark_base = case4_match.group(1)
                    number = id_match.group(1)
                    suffix = id_match.group(2)
                    strength = case4_match.group(3)
                    full_cube_mark = f"{cube_mark_base}-{number}{suffix}"
                    prefix, _, _ = parse_cube_mark(full_cube_mark)
                    cubes.append(
                        _build_cube_record(
                            prefix,
                            number,
                            suffix,
                            report_number,
                            date_cast,
                            strength,
                            pour_location,
                        )
                    )
                    i += 2
                    continue

        case5_match = re.search(
            r"CU\d+\s+(\d{8}-\d+[A-Z]+)\s+.*?\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+S\s+-",
            line,
        )
        if case5_match:
            if i + 2 < len(lines):
                next_next_line = lines[i + 2].strip()
                id_match = re.match(r"-\s*(\d+)([A-Z])$", next_next_line)
                if id_match:
                    cube_mark_base = case5_match.group(1)
                    number = id_match.group(1)
                    suffix = id_match.group(2)
                    strength = case5_match.group(3)
                    full_cube_mark = f"{cube_mark_base}-{number}{suffix}"
                    prefix, _, _ = parse_cube_mark(full_cube_mark)
                    cubes.append(
                        _build_cube_record(
                            prefix,
                            number,
                            suffix,
                            report_number,
                            date_cast,
                            strength,
                            pour_location,
                        )
                    )
                    i += 3
                    continue

        i += 1

    return cubes
