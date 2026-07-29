# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**kzemi-tools** is a Python toolkit for seminar-based data analysis (ゼミ用データ分析ツール集), designed for university students working with Japanese government statistics (e-Stat). Installed via `pip install git+https://github.com/qingruikz/kzemi_tools.git`. Primary runtime environment is Google Colab.

## Build & Install

```bash
# Install locally in editable mode (for development)
pip install -e .

# Install from GitHub (for students)
pip install git+https://github.com/qingruikz/kzemi_tools.git
```

Uses **src layout** — packages live under `src/kzemi_tools/`, configured via `[tool.setuptools.packages.find] where = ["src"]` in `pyproject.toml`.

No test suite or linter is configured. Manual testing is done via `examples/test.ipynb` (local, uses `sys.path.insert(0, "../src")`). The `examples/` directory is gitignored.

## Architecture

All public functions are re-exported from `__init__.py`. Each module is self-contained with no cross-module dependencies (except `visualize.py` which triggers matplotlib/seaborn setup at import time).

**Data pipeline flow:**
1. `data_reader.read_csv` → raw DataFrame (Shift-JIS, missing values, thousands separator handled)
2. `estat_cleaner.clean_estat_csv` → cleaned DataFrame + units DataFrame
3. `panel_align.make_lag` / `make_lead` → panel DataFrame + lag/lead columns ("総人口（3年前）")
4. `data_extract.extract_time_series` / `extract_cross_section` → subset DataFrames
5. `visualize.regplot/lineplot/histplot/barplot` → plots (display + optional PNG save)
6. `output_dir.create_output_dir` → timestamped output folder (JST timezone)
7. `model_formula.print_model_formulas` → regression model formulas from result table
8. `data_source.generate_data_source` → data source reference table (deduplicates derived variables like "Xの2乗", "Xの対数", "X（3年前）" → "X", including combinations; one row per variable). Reads 出典 per variable from `units_df["出典"]`

**Key design decisions:**
- `clean_estat_csv` takes a DataFrame (not a filepath) — decoupled from reading so `read_csv` can be reused independently
- Visualization functions use `plt.show()` for Colab inline display + optional `output_dir` for file saving
- `create_output_dir` uses JST (UTC+9) hardcoded since students run on Colab (UTC servers)
- `clean_estat_csv` sorts output by `地域`, `調査年` descending; `panel_align` returns the same order so the two are interchangeable in a pipeline
- `panel_align` shifts values by self-joining on `(id_col, year_col + k)` rather than `groupby().shift(k)` — this is independent of row order (output is descending, where `shift` would reverse the sign) and yields NaN instead of a silently wrong value when a year is missing
- No interpolation anywhere in the pipeline. Missing values stay missing (`extract_cross_section` used to `bfill()` dataframe-wide, which leaked values across regions)
- `model_formula` parses column format `"（N）\n被説明変数"` and index structure where rows before `定数項` are explanatory variables, NaN rows are standard errors

## Conventions

- All code comments, docstrings, and user-facing strings must be in **Japanese**
- Dependencies are declared in `pyproject.toml` under `[project] dependencies`
- New modules: create file in `src/kzemi_tools/`, add public functions to `__init__.py` `__all__`
- Update `examples/test.ipynb`, `README.md`, and `examples/demo.ipynb` (demo.ipynb is the student-facing version) when adding features
