"""CSV 読み込みユーティリティ"""

import pandas as pd


def read_csv(filepath: str) -> pd.DataFrame:
    """日本語 CSV ファイルを読み込む。

    Shift-JIS エンコーディング、欠損値（"-", "***"）、桁区切りカンマに
    対応した設定で CSV を読み込む。

    引数:
        filepath: CSV ファイルのパス（例: CWD + '/処理済みデータ/parsed_data.csv'）

    戻り値:
        読み込んだ DataFrame
    """
    df = pd.read_csv(
        filepath,
        encoding="shift-jis",
        skiprows=0,
        na_values=["-", "***"],
        thousands=",",
    )
    return df
