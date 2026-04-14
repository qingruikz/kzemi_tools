"""e-Stat データクリーナー"""

import re
import pandas as pd


def _parse_column_name(col: str) -> tuple[str, str]:
    """'#A011000_総人口【万人】' → ('総人口', '万人') に変換する。

    戻り値: (整形後の列名, 単位)。単位がない場合は空文字。
    """
    # '#CODE_' プレフィックスを除去
    name = re.sub(r"^#[A-Za-z0-9]+_", "", col)
    # 【...】から単位を抽出
    m = re.search(r"【(.+?)】", name)
    unit = m.group(1) if m else ""
    # 単位部分を除去
    name = re.sub(r"【.+?】", "", name)
    return name, unit


def clean_estat_csv(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """e-Stat の DataFrame の列名を整形し、単位を抽出する。

    引数:
        df: read_csv 等で読み込んだ e-Stat の DataFrame

    戻り値:
        (parsed_df, units_df)
        - parsed_df: 列名整形済みの DataFrame（'/項目' 列は除外、'調査年' は整数に変換）
        - units_df: '変数名' と '単位' の 2 列を持つ DataFrame
    """
    df = df.copy()

    # '/項目' 列を除外
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
