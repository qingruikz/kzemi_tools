"""estat CSV データクリーナー"""

import re
import pandas as pd


def _parse_column_name(col: str) -> tuple[str, str]:
    """Parse '#A011000_総人口【万人】' → ('総人口', '万人').

    Returns (clean_name, unit). Unit is '' if not found.
    """
    # Remove '#CODE_' prefix
    name = re.sub(r"^#[A-Za-z0-9]+_", "", col)
    # Extract unit from 【...】
    m = re.search(r"【(.+?)】", name)
    unit = m.group(1) if m else ""
    # Remove unit part
    name = re.sub(r"【.+?】", "", name)
    return name, unit


def clean_estat_csv(filepath: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Read an estat CSV, clean column names, and extract units.

    Returns:
        (parsed_df, units_df)
        - parsed_df: cleaned DataFrame (without '/項目' column)
        - units_df: DataFrame with columns ['変数名', '単位']
    """
    df = pd.read_csv(
        filepath,
        encoding="shift-jis",
        skiprows=0,
        na_values=["-", "***"],
        thousands=",",
    )

    # Drop '/項目' column if present
    item_cols = [c for c in df.columns if c.strip().startswith("/")]
    df = df.drop(columns=item_cols)

    # Rename data columns and collect units
    rename_map = {}
    units_records = []
    for col in df.columns:
        if col.startswith("#"):
            clean_name, unit = _parse_column_name(col)
            rename_map[col] = clean_name
            units_records.append({"変数名": clean_name, "単位": unit})

    parsed_df = df.rename(columns=rename_map)

    # Convert '調査年' from '2023年度' to 2023
    if "調査年" in parsed_df.columns:
        parsed_df["調査年"] = parsed_df["調査年"].str.extract(r"(\d+)").astype(int)

    units_df = pd.DataFrame(units_records)

    return parsed_df, units_df
