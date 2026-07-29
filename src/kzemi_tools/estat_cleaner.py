"""e-Stat データクリーナー"""

import re
import pandas as pd

ESTAT_SOURCE = "eStat「都道府県・市区町村のすがた(社会・人口統計体系)」データベース"


def _parse_column_name(col: str) -> tuple[str, str]:
    """'#A011000_総人口【万人】' または 'A011000_総人口【万人】' を
    ('総人口', '万人') に変換する。

    戻り値: (整形後の列名, 単位)。単位がない場合は空文字。
    """
    # 先頭の「#」が省略可能な 'CODE_' プレフィックスを除去
    name = re.sub(r"^#?[A-Za-z0-9]+_", "", col)
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
        - parsed_df: 列名整形済みの DataFrame（'/項目' 列は除外、'調査年' は整数に変換、
          '地域'・'調査年' の降順で並べ替え）
        - units_df: '変数名'・'単位'・'出典' の 3 列を持つ DataFrame
    """
    df = df.copy()

    # '/項目' 列を除外
    item_cols = [c for c in df.columns if c.strip().startswith("/")]
    df = df.drop(columns=item_cols)

    # データ列の列名を整形し、単位を収集
    rename_map = {}
    units_records = []
    for col in df.columns:
        if re.match(r"^#?[A-Za-z0-9]+_", col):
            clean_name, unit = _parse_column_name(col)
            rename_map[col] = clean_name
            units_records.append(
                {"変数名": clean_name, "単位": unit, "出典": ESTAT_SOURCE}
            )

    parsed_df = df.rename(columns=rename_map)

    # Convert '調査年' from '2023年度' to 2023
    if "調査年" in parsed_df.columns:
        parsed_df["調査年"] = parsed_df["調査年"].str.extract(r"(\d+)").astype(int)

    sort_cols = [c for c in ("地域", "調査年") if c in parsed_df.columns]
    if sort_cols:
        parsed_df = parsed_df.sort_values(by=sort_cols, ascending=False).reset_index(
            drop=True
        )

    units_df = pd.DataFrame(units_records, columns=["変数名", "単位", "出典"])

    return parsed_df, units_df
