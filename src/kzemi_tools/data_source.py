"""データソース表生成ユーティリティ"""

import re
import pandas as pd


def _extract_core_name(var_name: str) -> str:
    """変数名から元の変数名（コア部分）を抽出する。

    例:
        "総人口の 2 乗"   → "総人口"
        "総人口の対数"     → "総人口"
        "総人口"          → "総人口"
        "X1の 3 乗"      → "X1"

    引数:
        var_name: 変数名

    戻り値:
        コア部分の変数名
    """
    # 「〇〇の X 乗」パターンを除去
    name = re.sub(r"の\s*\d+\s*乗$", "", var_name)
    # 「〇〇の対数」パターンを除去
    name = re.sub(r"の対数$", "", name)
    return name.strip()


def generate_data_source(
    df_summary: pd.DataFrame,
    units: pd.DataFrame,
    source: str = "",
) -> pd.DataFrame:
    """記述統計量と単位情報からデータソース表を生成する。

    引数:
        df_summary: 記述統計量の DataFrame（インデックスが変数名）
        units: 変数名と単位の DataFrame（'変数名' と '単位' の 2 列）
        source: 出典（デフォルト: 空文字）

    戻り値:
        '変数', '単位', '出典' の 3 列を持つ DataFrame
    """
    # df_summary のインデックスからコア変数名を抽出し、重複を除去
    seen = set()
    core_names = []
    for var in df_summary.index:
        core = _extract_core_name(str(var))
        if core not in seen:
            seen.add(core)
            core_names.append(core)

    # units から単位を取得
    units_dict = dict(zip(units["変数名"], units["単位"]))

    records = []
    for name in core_names:
        unit = units_dict.get(name, "")
        records.append({"変数": name, "単位": unit, "出典": source})

    return pd.DataFrame(records)
