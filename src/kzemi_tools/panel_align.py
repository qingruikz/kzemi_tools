"""パネルデータの期ずらしユーティリティ — 滞後変数・先行変数の生成"""

from collections import defaultdict

import pandas as pd


def _validate(
    df: pd.DataFrame,
    columns: dict[str, int],
    id_col: str,
    year_col: str,
) -> None:
    """引数とパネル構造を検証する。問題があれば ValueError を投げる。"""
    missing_keys = [c for c in (id_col, year_col) if c not in df.columns]
    if missing_keys:
        raise ValueError(
            f"列 {missing_keys} が DataFrame にありません。"
            f"id_col と year_col を持つパネルデータを渡してください。"
        )

    if not isinstance(columns, dict) or not columns:
        raise ValueError(
            "columns は {'変数名': 年数} の形式の辞書で指定してください。"
            "（例: columns={'総人口': 3}）"
        )

    missing_vars = [c for c in columns if c not in df.columns]
    if missing_vars:
        raise ValueError(f"変数 {missing_vars} が DataFrame にありません。")

    key_vars = [c for c in columns if c in (id_col, year_col)]
    if key_vars:
        raise ValueError(
            f"{key_vars} はパネルのキー列（id_col / year_col）です。"
            f"滞後・先行変数は作成できません。"
        )

    for col, k in columns.items():
        # bool は int のサブクラスなので明示的に除外する
        if isinstance(k, bool) or not isinstance(k, int) or k <= 0:
            raise ValueError(
                f"「{col}」の年数が不正です（{k!r}）。1 以上の整数で指定してください。"
            )

    if not pd.api.types.is_numeric_dtype(df[year_col]):
        raise ValueError(
            f"「{year_col}」列が数値型ではありません（{df[year_col].dtype}）。"
            f"clean_estat_csv で整数に変換してから使ってください。"
        )

    duplicated = df.duplicated(subset=[id_col, year_col]).sum()
    if duplicated:
        raise ValueError(
            f"（{id_col}, {year_col}）の組み合わせに重複が {duplicated} 件あります。"
            f"1 行 = 1 地域 1 年になるように集約してから使ってください。"
        )


def _warn_missing_years(df: pd.DataFrame, id_col: str, year_col: str) -> None:
    """調査年が連続していない地域があれば警告する（処理は続行）。"""
    spans = df.groupby(id_col)[year_col].agg(["min", "max", "nunique"])
    gapped = spans[spans["max"] - spans["min"] + 1 != spans["nunique"]]
    if not gapped.empty:
        names = "、".join(str(i) for i in gapped.index[:5])
        suffix = " など" if len(gapped) > 5 else ""
        print(
            f"警告: 調査年が連続していない地域があります（{names}{suffix}／"
            f"計 {len(gapped)} 件）。該当する年の値は欠損（NaN）になります。"
        )


def _shift_years(
    df: pd.DataFrame,
    columns: dict[str, int],
    sign: int,
    suffix: str,
    id_col: str,
    year_col: str,
    drop_original: bool,
) -> pd.DataFrame:
    """columns で指定した変数を sign * k 年ずらした列を追加する。

    sign=1 なら過去の値（滞後）、sign=-1 なら将来の値（先行）を持ってくる。
    """
    _validate(df, columns, id_col, year_col)
    _warn_missing_years(df, id_col, year_col)

    # 同じ年数の変数はまとめて 1 回の結合で処理する
    by_offset: dict[int, list[str]] = defaultdict(list)
    for col, k in columns.items():
        by_offset[k].append(col)

    out = df.copy()
    for k, cols in by_offset.items():
        new_names = {c: f"{c}（{k}{suffix}）" for c in cols}
        duplicated_names = [n for n in new_names.values() if n in out.columns]
        if duplicated_names:
            raise ValueError(f"列 {duplicated_names} は既に存在します。")

        # ソース側の年を k 年ずらしてから結合することで、
        # 行の並び順に依存せず「k 年前（後）の値」を貼り付けられる
        src = df[[id_col, year_col, *cols]].copy()
        src[year_col] = src[year_col] + sign * k
        src = src.rename(columns=new_names)
        out = out.merge(src, on=[id_col, year_col], how="left")

    # 結合元は df なので、すべての結合が終わった後に安全に削除できる
    if drop_original:
        out = out.drop(columns=list(columns))

    return out.sort_values(by=[id_col, year_col], ascending=False).reset_index(
        drop=True
    )


def make_lag(
    df: pd.DataFrame,
    columns: dict[str, int],
    id_col: str = "地域",
    year_col: str = "調査年",
    drop_original: bool = False,
) -> pd.DataFrame:
    """指定した変数の「k 年前」の値を列として追加する。

    調査年が連続しているパネルデータ（1 行 = 1 地域 1 年）を前提とする。
    該当する年の行が存在しない場合、その値は欠損（NaN）になる。

    引数:
        df: パネルデータの DataFrame（id_col と year_col を含む）
        columns: {変数名: 年数} の辞書（例: {"総人口": 3, "県内総生産": 5}）
        id_col: 個体を識別する列名（デフォルト: "地域"）
        year_col: 年を表す列名（整数、デフォルト: "調査年"）
        drop_original: True にすると、滞後変数の作成元になった列を削除する
                       （デフォルト: False）

    戻り値:
        滞後変数の列を追加した DataFrame。
        列名は「総人口（3年前）」の形式。
        並び順は（id_col, year_col）の降順に揃えられる。

    例:
        >>> panel = make_lag(df, columns={"総人口": 3, "県内総生産": 5})
        >>> # 「総人口（3年前）」「県内総生産（5年前）」列が追加される

        >>> panel = make_lag(df, columns={"総人口": 3}, drop_original=True)
        >>> # 「総人口（3年前）」が追加され、「総人口」は削除される
    """
    return _shift_years(df, columns, 1, "年前", id_col, year_col, drop_original)


def make_lead(
    df: pd.DataFrame,
    columns: dict[str, int],
    id_col: str = "地域",
    year_col: str = "調査年",
    drop_original: bool = False,
) -> pd.DataFrame:
    """指定した変数の「k 年後」の値を列として追加する。

    調査年が連続しているパネルデータ（1 行 = 1 地域 1 年）を前提とする。
    該当する年の行が存在しない場合、その値は欠損（NaN）になる。

    注意: 将来の値を説明変数に使うことは原則として正当化できない。
    先行変数は被説明変数に対して使うこと（例: 現在の人口構成で
    「5 年後の県内総生産」を説明する）。

    引数:
        df: パネルデータの DataFrame（id_col と year_col を含む）
        columns: {変数名: 年数} の辞書（例: {"県内総生産": 5}）
        id_col: 個体を識別する列名（デフォルト: "地域"）
        year_col: 年を表す列名（整数、デフォルト: "調査年"）
        drop_original: True にすると、先行変数の作成元になった列を削除する
                       （デフォルト: False）

    戻り値:
        先行変数の列を追加した DataFrame。
        列名は「県内総生産（5年後）」の形式。
        並び順は（id_col, year_col）の降順に揃えられる。

    例:
        >>> panel = make_lead(df, columns={"県内総生産": 5})
        >>> # 「県内総生産（5年後）」列が追加される

        >>> panel = make_lead(df, columns={"県内総生産": 5}, drop_original=True)
        >>> # 「県内総生産（5年後）」が追加され、「県内総生産」は削除される
    """
    return _shift_years(df, columns, -1, "年後", id_col, year_col, drop_original)
