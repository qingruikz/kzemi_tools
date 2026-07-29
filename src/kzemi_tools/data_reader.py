"""CSV 読み込み・書き出しユーティリティ"""

import codecs
import os

import pandas as pd

# e-Stat からダウンロードした CSV は Shift-JIS なので最初に試す。
# cp932 は Shift-JIS の Windows 拡張版（①や㎡なども扱える上位互換）なので、
# 厳格な shift_jis の代わりに使う。
_CANDIDATE_ENCODINGS = ("cp932", "utf-8-sig", "utf-8")

_READ_OPTIONS = {"na_values": ["-", "***"], "thousands": ","}


def _detect_encoding(filepath: str) -> str | None:
    """先頭部分のバイト列から UTF-8 系かどうかを判定する。

    戻り値は "utf-8-sig" / "utf-8"、UTF-8 でなければ None。

    UTF-8 のファイルを cp932 で読むと、バイト列次第では例外にならず
    文字化けした文字列がそのまま返ってくる（例: 'ち' が '縺｡' になる）。
    そのため「順番に試して失敗したら次」だけでは不十分。逆に Shift-JIS の
    日本語を UTF-8 で読むとほぼ必ず UnicodeDecodeError になるため、
    先に UTF-8 かどうかを判定しておく。
    """
    with open(filepath, "rb") as f:
        head = f.read(65536)

    if head.startswith(codecs.BOM_UTF8):
        return "utf-8-sig"

    # 読み込んだ末尾でマルチバイト文字が切れていても誤判定しないよう、
    # インクリメンタルデコーダで判定する（final=False で途中の文字は保留される）
    decoder = codecs.getincrementaldecoder("utf-8")()
    try:
        decoder.decode(head)
    except UnicodeDecodeError:
        return None
    return "utf-8"


def read_csv(filepath: str, encoding: str | None = None) -> pd.DataFrame:
    """日本語 CSV ファイルを読み込む。

    欠損値（"-", "***"）、桁区切りカンマに対応した設定で読み込む。
    エンコーディングは Shift-JIS（e-Stat のダウンロード形式）と
    UTF-8 / UTF-8 (BOM 付き) を自動判定する。

    引数:
        filepath: CSV ファイルのパス（例: CWD + '/処理済みデータ/parsed_data.csv'）
        encoding: エンコーディングを明示指定する場合に使う。
                  省略時は自動判定（Shift-JIS 優先）。

    戻り値:
        読み込んだ DataFrame
    """
    if encoding is not None:
        return pd.read_csv(filepath, encoding=encoding, **_READ_OPTIONS)

    detected = _detect_encoding(filepath)
    candidates = [detected] if detected else []
    candidates += [e for e in _CANDIDATE_ENCODINGS if e != detected]

    failures = []
    for enc in candidates:
        try:
            return pd.read_csv(filepath, encoding=enc, **_READ_OPTIONS)
        except UnicodeDecodeError as e:
            failures.append(f"{enc}: {e}")

    detail = "\n  ".join(failures)
    raise ValueError(
        f"エンコーディングを判定できませんでした: {filepath}\n"
        f"  {detail}\n"
        f"encoding 引数で明示的に指定してください。"
    )


def to_csv(
    df: pd.DataFrame,
    filepath: str,
    encoding: str = "utf-8-sig",
) -> str:
    """DataFrame を CSV ファイルに保存する。

    インデックスは書き出さない（index=False）。
    保存先のフォルダが無い場合は自動で作成する。

    デフォルトの "utf-8-sig" は BOM 付き UTF-8。BOM があることで Excel が
    文字コードを正しく認識するため、ダブルクリックしても文字化けしない。
    BOM なしの "utf-8" だと Excel で文字化けするので注意。

    引数:
        df: 保存する DataFrame
        filepath: 保存先のパス（例: CWD + '/処理済みデータ/parsed_data.csv'）
        encoding: エンコーディング（デフォルト: "utf-8-sig"）。
                  Shift-JIS で保存したい場合は "shift_jis" を指定する。

    戻り値:
        保存したファイルのパス
    """
    parent = os.path.dirname(filepath)
    if parent:
        os.makedirs(parent, exist_ok=True)
    df.to_csv(filepath, encoding=encoding, index=False)
    print("保存しました：", filepath)
    return filepath
