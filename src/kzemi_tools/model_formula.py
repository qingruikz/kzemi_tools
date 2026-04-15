"""回帰モデルの識別戦略（モデル式）生成ユーティリティ"""

import re
import pandas as pd


def generate_model_formulas(df_result: pd.DataFrame) -> list[str]:
    """回帰分析の結果 DataFrame からモデル式の文字列リストを生成する。

    引数:
        df_result: 回帰分析の結果 DataFrame。
                   列名は「（1）\\n被説明変数名」の形式。
                   インデックスは説明変数名（空行あり）、'定数項' 以降は統計量。

    戻り値:
        モデル式の文字列リスト
    """
    # 定数項より前のインデックスから説明変数の候補を取得（NaN・空文字を除く）
    idx_list = df_result.index.tolist()
    if "定数項" in idx_list:
        cutoff = idx_list.index("定数項")
    else:
        cutoff = len(idx_list)
    variable_names = [
        name for name in idx_list[:cutoff]
        if pd.notna(name) and str(name).strip() != ""
    ]

    formulas = []
    for col in df_result.columns:
        # 列名から「モデル番号」と「被説明変数名」を分離
        parts = col.split("\n", maxsplit=1)
        model_label = parts[0].strip()
        dependent_var = parts[1].strip() if len(parts) > 1 else col.strip()

        # このモデルに含まれる説明変数を特定（値が存在する行）
        included_vars = []
        for var in variable_names:
            value = df_result.loc[var, col]
            if pd.notna(value) and str(value).strip() != "":
                included_vars.append(var)

        # 式を組み立て: Y = α + β1 X1 + β2 X2 + ... + 攪乱項
        terms = ["α"]
        for i, var in enumerate(included_vars, start=1):
            terms.append(f"β{i} {var}")
        rhs = " + ".join(terms) + " + 攪乱項"

        formula = f"モデル{model_label}：{dependent_var} = {rhs}"
        formulas.append(formula)

    return formulas


def print_model_formulas(df_result: pd.DataFrame) -> list[str]:
    """回帰分析の結果 DataFrame からモデル式を生成し、表示する。

    引数:
        df_result: 回帰分析の結果 DataFrame

    戻り値:
        モデル式の文字列リスト
    """
    formulas = generate_model_formulas(df_result)
    for formula in formulas:
        print(formula)
    return formulas
