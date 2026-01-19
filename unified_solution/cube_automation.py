"""CLI entry point for unified cube automation."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import config
from modules.data_validator import validate_cube_data
from modules.excel_writer import write_to_excel
from modules.pdf_extractor import extract_cubes_from_pdf


def process_single_pdf(
    pdf_path: str,
    output_path: str,
    validate: bool = False,
    logger: logging.Logger | None = None,
) -> None:
    """Process single PDF to Excel."""
    logger = logger or logging.getLogger(__name__)
    logger.info("Processing: %s", pdf_path)

    cube_data = extract_cubes_from_pdf(pdf_path)
    logger.info("Extracted %s cubes", len(cube_data))

    if validate:
        validation_result = validate_cube_data(cube_data)
        _log_validation_result(validation_result, logger)
        if validation_result["errors"]:
            logger.warning("Validation errors found; output will still be generated.")

    write_to_excel(cube_data, output_path)
    logger.info("Saved: %s", output_path)


def process_batch(
    folder_path: str,
    output_dir: str,
    validate: bool = False,
    logger: logging.Logger | None = None,
) -> None:
    """Process all PDFs in folder."""
    logger = logger or logging.getLogger(__name__)
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    pdf_files = list({*folder.glob("*.pdf"), *folder.glob("*.PDF")})
    pdf_files = sorted(pdf_files, key=lambda p: p.name.lower())

    logger.info("Found %s PDF files", len(pdf_files))
    if not pdf_files:
        raise ValueError("No PDF files found in folder")

    for idx, pdf_file in enumerate(pdf_files, start=1):
        output_name = f"{pdf_file.stem}_processed.xlsx"
        output_path = output_dir_path / output_name
        logger.info("Processing %s/%s: %s", idx, len(pdf_files), pdf_file.name)
        try:
            process_single_pdf(str(pdf_file), str(output_path), validate, logger)
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Error processing %s: %s", pdf_file.name, exc)
            logger.exception("Stack trace")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Automate concrete cube report processing from PDF to Excel"
    )
    parser.add_argument("input", help="Input PDF file or folder path")
    parser.add_argument(
        "output", nargs="?", help="Output Excel file path (single file mode)"
    )
    parser.add_argument("--folder", action="store_true", help="Process all PDFs in folder")
    parser.add_argument("--output-dir", help="Output directory for batch processing")
    parser.add_argument("--validate", action="store_true", help="Enable data validation")

    args = parser.parse_args()

    if args.folder:
        if not args.output_dir:
            parser.error("--output-dir is required when using --folder.")
        log_dir = Path(args.output_dir)
        log_path = log_dir / config.LOG_FILENAME
        logger = _setup_logging(log_path)
        process_batch(args.input, args.output_dir, args.validate, logger)
    else:
        if not args.output:
            parser.error("Output file path is required for single file mode.")
        log_dir = Path(args.output).parent if args.output else Path.cwd()
        log_path = log_dir / config.LOG_FILENAME
        logger = _setup_logging(log_path)
        process_single_pdf(args.input, args.output, args.validate, logger)


def _setup_logging(log_path: Path) -> logging.Logger:
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers = []

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    logger.info("Log file: %s", log_path)
    return logger


def _log_validation_result(result: dict, logger: logging.Logger) -> None:
    errors = result.get("errors", [])
    warnings = result.get("warnings", [])
    stats = result.get("stats", {})

    if errors:
        logger.error("Validation errors:")
        for message in errors:
            logger.error("  - %s", message)

    if warnings:
        logger.warning("Validation warnings:")
        for message in warnings:
            logger.warning("  - %s", message)

    total = stats.get("total_cubes", 0)
    logger.info("Validation stats: total_cubes=%s", total)
    for cube_type, count in stats.get("by_type", {}).items():
        logger.info("  %s: %s cubes", cube_type, count)
    for cube_type, avg_strength in stats.get("avg_strength", {}).items():
        logger.info("  %s: avg_strength=%s MPa", cube_type, avg_strength)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pylint: disable=broad-except
        logging.getLogger(__name__).exception("Fatal error: %s", exc)
        sys.exit(1)
