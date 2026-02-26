# Repository Introduction and Future Development Plan

## Purpose

This repository automates concrete cube test reporting from source documents to
usable outputs (CSV and formatted Excel), with multiple interface options:

- command line scripts,
- a unified Python package,
- a Streamlit web UI (work in progress),
- and a legacy VBA workflow for Excel users.

The project is strongest when using `unified_solution/`, which already combines
PDF extraction, validation, and workbook generation in one flow.

## Current Solution Landscape

| Directory | Primary role | Maturity | Notes |
| --- | --- | --- | --- |
| `unified_solution/` | End-to-end PDF to Excel pipeline | Stable and recommended | Best candidate for shared core |
| `pdf2csv/` | PDF to pipe-delimited CSV extraction | Stable | Contains parser logic similar to unified solution |
| `python_solution/` | Excel post-processing from an existing Raw sheet | Stable | Useful legacy bridge; narrower scope |
| `VBA_solution/` | In-workbook macro processing | Stable (maintenance mode) | Helpful for Excel-only teams |
| `streamlit_solution/` | Web UI for extraction and report generation | Under development | Useful product direction, currently parser-fragmented |

## Architecture Snapshot (as implemented today)

1. **Extraction**
   - `pdfplumber`-based parsing in `unified_solution/modules/pdf_extractor.py`
   - similar extraction logic in `pdf2csv/cube_extractor.py`
   - multiple experimental parsers in `streamlit_solution/`
2. **Validation**
   - rule-based checks in `unified_solution/modules/data_validator.py`
3. **Transformation and output**
   - workbook generation and merge formatting in
     `unified_solution/modules/excel_writer.py`
4. **Interfaces**
   - CLI entry (`python -m unified_solution`)
   - batch wrapper (`process_batch.bat`)
   - Streamlit UI for manual review/edit/download
   - VBA macro route for legacy workflows

## Key Strengths

- Practical multi-path workflows for different user types.
- The unified parser supports multiple real-world report line-break patterns.
- Minimal dependency footprint and straightforward onboarding.
- Clear business value: removes repetitive manual Excel preparation.

## Key Gaps and Risks

1. **Parsing logic duplication**
   - Similar cube parsing exists in both `unified_solution/` and `pdf2csv/`,
     increasing maintenance cost and drift risk.
2. **Inconsistent data contracts**
   - Unified flow uses semantic keys (for example `cube_mark_prefix`), while
     Streamlit paths use column-style keys (`B`, `C`, `D`, etc.).
3. **No automated test suite**
   - Parser edge cases are handled in code but not protected by regression
     tests.
4. **No CI quality gates**
   - No automated checks for tests, linting, or formatting.
5. **Repository hygiene gaps**
   - Top-level README references MIT licensing, but a root `LICENSE` file is
     absent.

## Recommended Development Direction

Adopt a **single-core, multi-interface architecture**:

- Make `unified_solution/` the canonical business logic layer.
- Refactor `pdf2csv/` and `streamlit_solution/` to call shared core functions
  instead of maintaining separate parser implementations.
- Keep VBA and legacy scripts as compatibility paths, not primary development
  targets.

This keeps feature growth focused and lowers long-term maintenance effort.

## Phased Roadmap

### Phase 0 (Week 1): Foundation and Standards

**Goals**
- Improve repo maintainability and contributor confidence.

**Deliverables**
- Add root `LICENSE` file (MIT, matching README intent).
- Add contribution standards (`CONTRIBUTING.md`, issue templates).
- Introduce basic tooling config (formatter/lint baseline).
- Define and document canonical cube data schema.

### Phase 1 (Weeks 2-3): Core Consolidation

**Goals**
- Remove duplicate parsing behavior and establish a shared API.

**Deliverables**
- Move shared parser functionality into `unified_solution/modules/`.
- Replace `pdf2csv` extraction internals with shared parser calls.
- Add adapter layer in Streamlit to map UI tables to canonical schema.
- Mark duplicated parser functions as deprecated where applicable.

### Phase 2 (Weeks 4-5): Quality and Regression Safety

**Goals**
- Prevent parser regressions and make releases safer.

**Deliverables**
- Add unit tests for cube mark parsing and extraction cases.
- Add fixture-based tests covering current known report variants.
- Add validation tests for date/strength/type checks.
- Add CI workflow to run tests and static checks on pull requests.

### Phase 3 (Weeks 6-8): Streamlit Product Stabilization

**Goals**
- Turn Streamlit into a reliable user-facing interface.

**Deliverables**
- Replace experimental parser routes with shared unified parser.
- Improve extraction error reporting and user guidance in UI.
- Support batch PDF upload with per-file status and downloads.
- Add smoke tests for main Streamlit flow.

### Phase 4 (Post Week 8): Productization and Scale

**Goals**
- Support broader document variability and operational usage.

**Deliverables**
- Add optional OCR fallback for image-based PDFs.
- Introduce configuration-driven parsing rules for new report formats.
- Package as installable CLI tool and/or lightweight service endpoint.
- Add release/versioning process and changelog automation.

## Priority Backlog (Recommended Order)

1. Define canonical schema and data model object.
2. Consolidate parsing logic into one shared module.
3. Add tests for known extraction cases (especially line-break variants).
4. Add CI checks (tests + lint + format).
5. Stabilize Streamlit to consume shared logic only.
6. Add LICENSE and contributor docs.
7. Add sample anonymized PDFs for regression testing.
8. Add batch-level summary report (success, warning, error counts).
9. Add optional CSV output mode to unified CLI.
10. Plan deprecation policy for duplicated legacy paths.

## Success Metrics

- 0 known parser regressions on fixture suite across releases.
- 100% of interfaces (CLI, Streamlit, CSV mode) use shared extraction core.
- Reduced issue volume related to inconsistent outputs between workflows.
- Faster onboarding: new contributor can run tests and one end-to-end command
  within 15 minutes.

## Immediate Next Sprint Suggestion

For the next sprint, prioritize:

1. canonical schema definition,
2. parser consolidation between `unified_solution` and `pdf2csv`,
3. initial regression tests for existing 5 parsing cases,
4. basic CI automation.

These steps give the highest risk reduction and unlock safer feature work.
