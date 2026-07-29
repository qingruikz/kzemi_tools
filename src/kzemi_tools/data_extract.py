"""データ抽出ユーティリティ — パネル・時系列・クロスセクションデータの抽出"""

import pandas as pd


def extract_panel(df: pd.DataFrame, exclude: str | None = None) -> pd.DataFrame:
    """パネルデータ（全地域・全年）を抽出する。

    地域の合計行（「全国」など）を除いた分析用のパネルを作るのに使う。
    欠損値の補完は行わない（欠損はそのまま欠損として残す）。

    引数:
        df: clean_estat_csv で取得した DataFrame
        exclude: 除外する地域名（例: "全国", "北海道"）。
                 その地域の全ての年の行が除外される。省略時は除外なし。

    戻り値:
        パネル DataFrame

    例:
        >>> panel = extract_panel(df, exclude="全国")
        >>> # 「全国」の行を除いた 都道府県 × 調査年 のパネル
    """
    if exclude is None:
        result = df.copy()
    else:
        if exclude not in df["地域"].values:
            print(
                f"警告: 「{exclude}」に該当するデータが見つかりません"
                f"（除外されていません）。"
            )
        result = df.query("地域 != @exclude")
    if result.empty:
        print("警告: 抽出結果が空です。")
    return result


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

    欠損値の補完は行わない（欠損はそのまま欠損として残す）。

    引数:
        df: clean_estat_csv で取得した DataFrame
        year: 調査年（整数、例: 2016）
        exclude: 除外する地域名（例: "全国", "北海道"）。
                 省略時は除外なし。

    戻り値:
        指定年のクロスセクション DataFrame
    """
    if exclude is not None:
        result = df.query("地域 != @exclude and 調査年 == @year")
    else:
        result = df.query("調査年 == @year")
    if result.empty:
        print(f"警告: 調査年={year} に該当するデータが見つかりません。")
    return result
