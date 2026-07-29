"""データソース表生成ユーティリティ"""

import re
import pandas as pd


_DERIVED_PATTERNS = [
    # 「〇〇（N 年前）」「〇〇（N 年後）」パターン（半角括弧も許容）
    r"[（(]\s*\d+\s*年[前後]\s*[）)]$",
    # 「〇〇の X 乗」パターン
    r"の\s*\d+\s*乗$",
    # 「〇〇の対数」パターン
    r"の対数$",
]


def _extract_core_name(var_name: str) -> str:
    """変数名から元の変数名（コア部分）を抽出する。

    例:
        "総人口の 2 乗"            → "総人口"
        "総人口の対数"              → "総人口"
        "総人口"                   → "総人口"
        "X1の 3 乗"               → "X1"
        "総人口（3年前）"           → "総人口"
        "県内総生産（5年後）"        → "県内総生産"
        "総人口の対数（3年前）"      → "総人口"
        "総人口（3年前）の対数"      → "総人口"

    引数:
        var_name: 変数名

    戻り値:
        コア部分の変数名
    """
    # 派生パターンが付与された順に依存しないよう、変化がなくなるまで繰り返す
    name = str(var_name).strip()
    while True:
        previous = name
        for pattern in _DERIVED_PATTERNS:
            name = re.sub(pattern, "", name).strip()
        if name == previous:
            return name


def generate_data_source(
    df_summary: pd.DataFrame,
    units: pd.DataFrame,
) -> pd.DataFrame:
    """記述統計量と単位情報からデータソース表を生成する。

    派生変数（「の 2 乗」「の対数」「（N 年前）」「（N 年後）」）は元の変数名に
    集約されるため、1 つの変数につき必ず 1 行になる。

    引数:
        df_summary: 記述統計量または回帰結果の DataFrame（インデックスが変数名）
        units: clean_estat_csv で取得した DataFrame
               （'変数名'・'単位'・'出典' の 3 列）

    戻り値:
        '変数', '単位', '出典' の 3 列を持つ DataFrame
    """
    missing_cols = [c for c in ("変数名", "単位", "出典") if c not in units.columns]
    if missing_cols:
        raise ValueError(
            f"units に列 {missing_cols} がありません。"
            f"clean_estat_csv で取得した units_df を渡してください。"
        )

    # df_summary のインデックスからコア変数名を抽出し、重複を除去
    seen = set()
    core_names = []
    for var in df_summary.index:
        core = _extract_core_name(str(var))
        if core and core not in seen:
            seen.add(core)
            core_names.append(core)

    # units から単位と出典を取得
    units_dict = dict(zip(units["変数名"], units["単位"]))
    source_dict = dict(zip(units["変数名"], units["出典"]))

    records = [
        {
            "変数": name,
            "単位": units_dict.get(name, ""),
            "出典": source_dict.get(name, ""),
        }
        for name in core_names
    ]

    return pd.DataFrame(records, columns=["変数", "単位", "出典"])
