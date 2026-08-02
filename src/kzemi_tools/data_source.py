"""データソース表生成ユーティリティ"""

import re
import string

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


def _variable_names(df_summary: pd.DataFrame) -> list[str]:
    """インデックスから変数名だけを取り出す。

    回帰結果の表では '定数項' 以降が統計量（決定係数・観測数など）、
    NaN や空文字の行が標準誤差なので、いずれも変数名から除外する。
    """
    idx_list = df_summary.index.tolist()
    cutoff = idx_list.index("定数項") if "定数項" in idx_list else len(idx_list)
    return [
        str(name)
        for name in idx_list[:cutoff]
        if pd.notna(name) and str(name).strip() != ""
    ]


def _letter(index: int) -> str:
    """0 → 'a'、1 → 'b'、…、25 → 'z'、26 → 'aa' のラベルを返す。"""
    label = ""
    while True:
        label = string.ascii_lowercase[index % 26] + label
        index = index // 26 - 1
        if index < 0:
            return label


def _compact_sources(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """出典を出現順の a, b, c… に置き換え、注釈文とあわせて返す。"""
    labels: dict[str, str] = {}
    for source in df["出典"]:
        if pd.isna(source) or str(source).strip() == "":
            continue
        if source not in labels:
            labels[source] = _letter(len(labels))

    df = df.copy()
    df["出典"] = [labels.get(s, "") for s in df["出典"]]

    if not labels:
        return df, ""
    body = "、".join(f"{letter}は{source}" for source, letter in labels.items())
    return df, f"（注）1）データの出典について、{body}を意味する。"


def generate_data_source(
    df_summary: pd.DataFrame,
    units: pd.DataFrame,
    compact: bool = False,
) -> pd.DataFrame:
    """記述統計量と単位情報からデータソース表を生成する。

    派生変数（「の 2 乗」「の対数」「（N 年前）」「（N 年後）」）は元の変数名に
    集約されるため、1 つの変数につき必ず 1 行になる。

    回帰結果の表を渡した場合、'定数項' 以降の統計量（決定係数・観測数など）と
    標準誤差の行（インデックスが NaN や空文字）は自動的に除外される。

    引数:
        df_summary: 記述統計量または回帰結果の DataFrame（インデックスが変数名）
        units: clean_estat_csv で取得した DataFrame
               （'変数名'・'単位'・'出典' の 3 列）
        compact: True にすると出典を出現順に a, b, c… の記号で表示し、
                 記号の対応を示す注釈文を表示する（デフォルト: False）

    戻り値:
        '変数', '単位', '出典' の 3 列を持つ DataFrame
    """
    missing_cols = [c for c in ("変数名", "単位", "出典") if c not in units.columns]
    if missing_cols:
        raise ValueError(
            f"units に列 {missing_cols} がありません。"
            f"clean_estat_csv で取得した units_df を渡してください。"
        )

    # 変数名からコア変数名を抽出し、重複を除去
    seen = set()
    core_names = []
    for var in _variable_names(df_summary):
        core = _extract_core_name(var)
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

    result = pd.DataFrame(records, columns=["変数", "単位", "出典"])

    if compact:
        result, note = _compact_sources(result)
        if note:
            print(note)

    return result
