"""データ可視化ユーティリティ — seaborn ベースのグラフ描画"""

import matplotlib.pyplot as plt
import seaborn as sns
import japanize_matplotlib  # noqa: F401  日本語フォント対応

# グラフのスタイル設定
sns.set(
    style="whitegrid",
    font="IPAexGothic",
    font_scale=1.5,
    rc={
        "grid.linestyle": "--",
        "axes.linewidth": 1,
        "axes.edgecolor": "black",
        "figure.figsize": (15, 10),
    },
)


def regplot(
    data, x: str, y: str, year: int | None = None, output_dir: str | None = None
):
    """散布図（回帰直線付き）を描画する。

    引数:
        data: クロスセクション DataFrame
        x: x 軸の変数名
        y: y 軸の変数名
        year: 調査年（タイトル・ファイル名に使用）
        output_dir: 保存先フォルダのパス。省略時は保存しない
    """
    fig, ax = plt.subplots()
    sns.regplot(data=data, x=x, y=y, line_kws={"color": "indianred"}, ax=ax)
    plt.tight_layout()
    if output_dir is not None:
        label = f"{year}年における" if year is not None else ""
        fig.savefig(
            f"{output_dir}/{label}{x}と{y}の散布図.png", dpi=300, bbox_inches="tight"
        )
    plt.show()


def lineplot(data, y: str, output_dir: str | None = None):
    """折れ線グラフ（時系列推移）を描画する。

    引数:
        data: 時系列 DataFrame（'調査年' 列を含む）
        y: y 軸の変数名
        output_dir: 保存先フォルダのパス。省略時は保存しない
    """
    fig, ax = plt.subplots()
    sorted_data = data.sort_values(by=["調査年"], ascending=True)
    sns.lineplot(data=sorted_data, x="調査年", y=y, ax=ax)
    plt.xticks(rotation=90)
    plt.tight_layout()
    if output_dir is not None:
        fig.savefig(f"{output_dir}/{y}の推移.png", dpi=300, bbox_inches="tight")
    plt.show()


def histplot(data, x: str, year: int | None = None, output_dir: str | None = None):
    """ヒストグラムを描画する。

    引数:
        data: クロスセクション DataFrame
        x: x 軸の変数名
        year: 調査年（タイトル・ファイル名に使用）
        output_dir: 保存先フォルダのパス。省略時は保存しない
    """
    fig, ax = plt.subplots()
    sns.histplot(data=data, x=x, ax=ax)
    ax.set_ylabel("度数")
    plt.tight_layout()
    if output_dir is not None:
        label = f"{year}年における" if year is not None else ""
        fig.savefig(
            f"{output_dir}/{label}{x}のヒストグラム.png", dpi=300, bbox_inches="tight"
        )
    plt.show()


def barplot(
    data,
    y: str,
    year: int | None = None,
    output_dir: str | None = None,
    top: int | None = 50,
    ascending: bool = False,
):
    """棒グラフ（ランキング）を描画する。

    引数:
        data: クロスセクション DataFrame（'地域' 列を含む）
        y: y 軸の変数名
        year: 調査年（タイトル・ファイル名に使用）
        output_dir: 保存先フォルダのパス。省略時は保存しない
        top: 表示する件数（デフォルト: 50）。並べ替えた後の先頭から top 件を
             表示する。None を指定するとすべて表示する
        ascending: True で昇順（小さい順）に並べる。
                   デフォルトは降順（大きい順）
    """
    if top is not None and top <= 0:
        raise ValueError(f"top は 1 以上の整数で指定してください（{top!r}）。")

    direction = "下位" if ascending else "上位"
    sorted_data = data.sort_values(by=y, ascending=ascending)
    truncated = top is not None and len(sorted_data) > top
    if truncated:
        print(f"注: 全 {len(sorted_data)} 件のうち{direction}{top}件のみ表示します。")
        sorted_data = sorted_data.head(top)

    fig, ax = plt.subplots()
    sns.barplot(data=sorted_data, x="地域", y=y, errorbar=None, ax=ax)
    plt.xticks(rotation=90)
    plt.tight_layout()
    if output_dir is not None:
        label = f"{year}年における" if year is not None else ""
        rank = f"（{direction}{top}件）" if truncated else ""
        fig.savefig(
            f"{output_dir}/{label}{y}のランキング{rank}.png",
            dpi=300,
            bbox_inches="tight",
        )
    plt.show()
