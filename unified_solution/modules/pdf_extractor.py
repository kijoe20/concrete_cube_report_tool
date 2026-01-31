"""PDF extraction logic for concrete cube reports."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

try:
    import pdfplumber
except ImportError as exc:  # pragma: no cover - handled at runtime
    raise ImportError(
        "pdfplumber is required. Install with: pip install pdfplumber"
    ) from exc

logger = logging.getLogger(__name__)


@dataclass
class ParsingCase:
    """Represents a single parsing pattern case for cube data extraction."""

    name: str
    pattern: str
    handler: Callable[[re.Match, List[str], int], Optional[Tuple[Dict[str, str], int]]]


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


def _handle_case1(
    match: re.Match, lines: List[str], i: int, report_number: str, date_cast: str, pour_location: str
) -> Optional[Tuple[Dict[str, str], int]]:
    """Handle case 1: Full cube mark on single line (e.g., 20250621-45D-1A)."""
    full_cube_mark = match.group(1)
    strength = match.group(3)
    prefix, number, suffix = parse_cube_mark(full_cube_mark)
    cube = _build_cube_record(prefix, number, suffix, report_number, date_cast, strength, pour_location)
    return cube, i + 1


def _handle_case2(
    match: re.Match, lines: List[str], i: int, report_number: str, date_cast: str, pour_location: str
) -> Optional[Tuple[Dict[str, str], int]]:
    """Handle case 2: Cube mark without suffix, suffix on next line (e.g., 20250621-45D-1 then A)."""
    if i + 1 >= len(lines):
        return None
    next_line = lines[i + 1].strip()
    if not (len(next_line) == 1 and next_line.isalpha() and next_line.isupper()):
        return None
    cube_mark_base = match.group(1)
    strength = match.group(3)
    suffix = next_line
    full_cube_mark = f"{cube_mark_base}{suffix}"
    prefix, number, _ = parse_cube_mark(full_cube_mark)
    cube = _build_cube_record(prefix, number, suffix, report_number, date_cast, strength, pour_location)
    return cube, i + 2


def _handle_case3(
    match: re.Match, lines: List[str], i: int, report_number: str, date_cast: str, pour_location: str
) -> Optional[Tuple[Dict[str, str], int]]:
    """Handle case 3: Cube mark with trailing dash, number+suffix on next line (e.g., 20250621-45D- then 1A)."""
    if i + 1 >= len(lines):
        return None
    next_line = lines[i + 1].strip()
    id_match = re.match(r"(\d+)([A-Z])$", next_line)
    if not id_match:
        return None
    cube_mark_base = match.group(1)
    number = id_match.group(1)
    suffix = id_match.group(2)
    strength = match.group(3)
    cube = _build_cube_record(cube_mark_base, number, suffix, report_number, date_cast, strength, pour_location)
    return cube, i + 2


def _handle_case4(
    match: re.Match, lines: List[str], i: int, report_number: str, date_cast: str, pour_location: str
) -> Optional[Tuple[Dict[str, str], int]]:
    """Handle case 4: Partial cube mark, dash+number+suffix on next line (e.g., 20250621-45D then -1A)."""
    if i + 1 >= len(lines):
        return None
    next_line = lines[i + 1].strip()
    id_match = re.match(r"-\s*(\d+)([A-Z])$", next_line)
    if not id_match:
        return None
    cube_mark_base = match.group(1)
    number = id_match.group(1)
    suffix = id_match.group(2)
    strength = match.group(3)
    full_cube_mark = f"{cube_mark_base}-{number}{suffix}"
    prefix, _, _ = parse_cube_mark(full_cube_mark)
    cube = _build_cube_record(prefix, number, suffix, report_number, date_cast, strength, pour_location)
    return cube, i + 2


def _handle_case5(
    match: re.Match, lines: List[str], i: int, report_number: str, date_cast: str, pour_location: str
) -> Optional[Tuple[Dict[str, str], int]]:
    """Handle case 5: Partial cube mark, dash+number+suffix two lines down (e.g., 20250621-45D, blank, then -1A)."""
    if i + 2 >= len(lines):
        return None
    next_next_line = lines[i + 2].strip()
    id_match = re.match(r"-\s*(\d+)([A-Z])$", next_next_line)
    if not id_match:
        return None
    cube_mark_base = match.group(1)
    number = id_match.group(1)
    suffix = id_match.group(2)
    strength = match.group(3)
    full_cube_mark = f"{cube_mark_base}-{number}{suffix}"
    prefix, _, _ = parse_cube_mark(full_cube_mark)
    cube = _build_cube_record(prefix, number, suffix, report_number, date_cast, strength, pour_location)
    return cube, i + 3


def _get_parsing_cases(report_number: str, date_cast: str, pour_location: str) -> List[ParsingCase]:
    """Define all parsing cases with their patterns and handlers."""
    return [
        ParsingCase(
            name="case1_full_mark",
            pattern=r"CU\d+\s+(\d{8}-\d+[A-Z]+-\d+[A-Z])\s+.*?\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+S\s+-",
            handler=lambda m, l, i: _handle_case1(m, l, i, report_number, date_cast, pour_location),
        ),
        ParsingCase(
            name="case2_suffix_next_line",
            pattern=r"CU\d+\s+(\d{8}-\d+[A-Z]+-\d+)\s+.*?\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+S\s+-",
            handler=lambda m, l, i: _handle_case2(m, l, i, report_number, date_cast, pour_location),
        ),
        ParsingCase(
            name="case3_number_suffix_next_line",
            pattern=r"CU\d+\s+(\d{8}-\d+[A-Z]+-)\s+.*?\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+S\s+-",
            handler=lambda m, l, i: _handle_case3(m, l, i, report_number, date_cast, pour_location),
        ),
        ParsingCase(
            name="case4_dash_number_suffix_next_line",
            pattern=r"CU\d+\s+(\d{8}-\d+[A-Z]+)\s+.*?\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+S\s+-",
            handler=lambda m, l, i: _handle_case4(m, l, i, report_number, date_cast, pour_location),
        ),
        ParsingCase(
            name="case5_dash_number_suffix_two_lines_down",
            pattern=r"CU\d+\s+(\d{8}-\d+[A-Z]+)\s+.*?\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+S\s+-",
            handler=lambda m, l, i: _handle_case5(m, l, i, report_number, date_cast, pour_location),
        ),
    ]


def _extract_all_cubes_from_text(page_text: str) -> List[Dict[str, str]]:
    """Extract all cube records from page text using defined parsing cases."""
    if not page_text:
        return []

    cubes: List[Dict[str, str]] = []
    report_number = _extract_report_number(page_text)
    date_cast = _extract_date_cast(page_text)
    pour_location = _extract_pour_location(page_text)

    parsing_cases = _get_parsing_cases(report_number, date_cast, pour_location)
    lines = page_text.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        matched = False

        for case in parsing_cases:
            match = re.search(case.pattern, line)
            if match:
                result = case.handler(match, lines, i)
                if result:
                    cube, next_i = result
                    cubes.append(cube)
                    i = next_i
                    matched = True
                    break

        if not matched:
            i += 1

    return cubes
