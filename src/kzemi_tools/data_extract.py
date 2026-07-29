"""データ抽出ユーティリティ — パネル・時系列・クロスセクションデータの抽出"""

import pandas as pd


def _exclude_regions(
    df: pd.DataFrame,
    exclude: str | list[str] | None,
) -> pd.DataFrame:
    """exclude で指定した地域の行を除外する。

    df に存在しない地域名が含まれていても何もしない（エラーにも警告にもしない）。
    複数のデータで同じ除外リストを使い回せるようにするため。
    """
    if exclude is None:
        return df
    targets = [exclude] if isinstance(exclude, str) else list(exclude)
    return df[~df["地域"].isin(targets)]


def extract_panel(
    df: pd.DataFrame,
    exclude: str | list[str] | None = None,
) -> pd.DataFrame:
    """パネルデータ（全地域・全年）を抽出する。

    地域の合計行（「全国」など）を除いた分析用のパネルを作るのに使う。
    欠損値の補完は行わない（欠損はそのまま欠損として残す）。

    引数:
        df: clean_estat_csv で取得した DataFrame
        exclude: 除外する地域名。文字列またはそのリスト
                 （例: "全国", ["全国", "北海道"]）。
                 指定した地域の全ての年の行が除外される。省略時は除外なし。

    戻り値:
        パネル DataFrame

    例:
        >>> panel = extract_panel(df, exclude="全国")
        >>> # 「全国」の行を除いた 都道府県 × 調査年 のパネル

        >>> panel = extract_panel(df, exclude=["全国", "北海道"])
    """
    result = _exclude_regions(df, exclude).copy()
    if result.empty:
        print("警告: 抽出結果が空です。")
    return result


def extract_time_series(
    df: pd.DataFrame,
    region: str,
    exclude: str | list[str] | None = None,
) -> pd.DataFrame:
    """指定した地域の時系列データを抽出する。

    引数:
        df: clean_estat_csv で取得した DataFrame
        region: 抽出対象の地域名（例: "全国", "北海道", "北海道 紋別市"）
        exclude: 除外する地域名。文字列またはそのリスト。省略時は除外なし。
                 region で 1 地域に絞り込むため、通常は指定する必要がない。

    戻り値:
        指定地域の時系列 DataFrame
    """
    result = _exclude_regions(df, exclude).query("地域 == @region")
    if result.empty:
        print(f"警告: 「{region}」に該当するデータが見つかりません。")
    return result


def extract_cross_section(
    df: pd.DataFrame,
    year: int,
    exclude: str | list[str] | None = None,
) -> pd.DataFrame:
    """指定した年のクロスセクション（横断面）データを抽出する。

    欠損値の補完は行わない（欠損はそのまま欠損として残す）。

    引数:
        df: clean_estat_csv で取得した DataFrame
        year: 調査年（整数、例: 2016）
        exclude: 除外する地域名。文字列またはそのリスト
                 （例: "全国", ["全国", "北海道"]）。省略時は除外なし。

    戻り値:
        指定年のクロスセクション DataFrame
    """
    result = _exclude_regions(df, exclude).query("調査年 == @year")
    if result.empty:
        print(f"警告: 調査年={year} に該当するデータが見つかりません。")
    return result
