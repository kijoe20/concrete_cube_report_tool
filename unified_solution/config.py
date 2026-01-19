"""Configuration settings for the unified cube automation tool."""

RAW_SHEET = "Raw"

EXCEL_HEADERS = [
    "Cube Mark Prefix",
    "Cube Number",
    "Cube Suffix",
    "Report Number",
    "Date Cast",
    "Compressive Strength (MPa)",
    "Pour Location",
]

CONCRETE_TYPES = ["45D", "60D", "45DWP", "60DWP"]

# Validation thresholds
MIN_STRENGTH = 20.0  # MPa
MAX_STRENGTH = 100.0  # MPa

# Column letters for merging
POUR_LOCATION_COL = "G"

# Merge columns to match legacy Excel output
MERGE_COLS = ["A", "B", "D", "E"]

# Default log file name
LOG_FILENAME = "cube_automation.log"
