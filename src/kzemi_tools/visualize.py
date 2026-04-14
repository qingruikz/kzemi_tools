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


def regplot(data, x: str, y: str, year: int | None = None, output_dir: str | None = None):
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
    if year is not None:
        ax.set_title(f"{year}年における{x}と{y}の散布図")
    plt.tight_layout()
    if output_dir is not None:
        label = f"{year}年における" if year is not None else ""
        fig.savefig(f"{output_dir}/{label}{x}と{y}の散布図.png", dpi=300, bbox_inches="tight")
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
    ax.set_title(f"{y}の推移")
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
    if year is not None:
        ax.set_title(f"{year}年における{x}のヒストグラム")
    plt.tight_layout()
    if output_dir is not None:
        label = f"{year}年における" if year is not None else ""
        fig.savefig(f"{output_dir}/{label}{x}のヒストグラム.png", dpi=300, bbox_inches="tight")
    plt.show()


def barplot(data, y: str, year: int | None = None, output_dir: str | None = None):
    """棒グラフ（ランキング）を描画する。

    引数:
        data: クロスセクション DataFrame（'地域' 列を含む）
        y: y 軸の変数名
        year: 調査年（タイトル・ファイル名に使用）
        output_dir: 保存先フォルダのパス。省略時は保存しない
    """
    fig, ax = plt.subplots()
    sorted_data = data.sort_values(by=y, ascending=False)
    sns.barplot(data=sorted_data, x="地域", y=y, errorbar=None, ax=ax)
    if year is not None:
        ax.set_title(f"{year}年における{y}のランキング")
    plt.xticks(rotation=90)
    plt.tight_layout()
    if output_dir is not None:
        label = f"{year}年における" if year is not None else ""
        fig.savefig(f"{output_dir}/{label}{y}のランキング.png", dpi=300, bbox_inches="tight")
    plt.show()
