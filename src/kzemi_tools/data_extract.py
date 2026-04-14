"""データ抽出ユーティリティ — 時系列・クロスセクションデータの抽出"""

import pandas as pd


def extract_time_series(df: pd.DataFrame, region: str) -> pd.DataFrame:
    """指定した地域の時系列データを抽出する。

    引数:
        df: clean_estat_csv で取得した DataFrame
        region: 抽出対象の地域名（例: "全国", "北海道", "北海道 紋別市"）

    戻り値:
        指定地域の時系列 DataFrame
    """
    result = df.query("地域 == @region")
    if result.empty:
        print(f"警告: 「{region}」に該当するデータが見つかりません。")
    return result


def extract_cross_section(
    df: pd.DataFrame,
    year: int,
    exclude: str | None = None,
) -> pd.DataFrame:
    """指定した年のクロスセクション（横断面）データを抽出する。

    欠損値は後方補完（bfill）で埋めた上で抽出する。

    引数:
        df: clean_estat_csv で取得した DataFrame
        year: 調査年（整数、例: 2016）
        exclude: 除外する地域名（例: "全国", "北海道"）。
                 省略時は除外なし。

    戻り値:
        指定年のクロスセクション DataFrame
    """
    filled = df.bfill()
    if exclude is not None:
        result = filled.query("地域 != @exclude and 調査年 == @year")
    else:
        result = filled.query("調査年 == @year")
    if result.empty:
        print(f"警告: 調査年={year} に該当するデータが見つかりません。")
    return result
