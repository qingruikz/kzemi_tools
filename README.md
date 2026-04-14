# kzemi-tools

ゼミ用データ分析ツール集です。

## インストール

```bash
pip install git+https://github.com/qingruikz/kzemi_tools.git
```

## 使い方

### `clean_estat_csv` — e-Stat CSV クリーナー

e-Stat からダウンロードした CSV（Shift-JIS）を読み込み、列名の整形と単位の抽出を行います。

```python
from kzemi_tools import clean_estat_csv

df, units = clean_estat_csv("FEI_PREF_250703135154.csv")

print(units)
#   変数名   単位
# 0 総人口   万人
# 1 面積    km2
# ...

print(df.head())
```

**引数**

| 引数 | 型 | 説明 |
|------|----|------|
| `filepath` | `str` | e-Stat CSV ファイルのパス |

**戻り値** — `(df, units)` のタプル

| 値 | 型 | 説明 |
|----|----|------|
| `df` | `DataFrame` | 列名を整形済みの DataFrame。`/項目` 列は除外され、`調査年` は整数に変換されます |
| `units` | `DataFrame` | `変数名` と `単位` の 2 列を持つ DataFrame |

### `create_output_dir` — 出力フォルダ作成

カレントワーキングディレクトリ内の `出力ファイル/` フォルダに、現在時刻（`YYYYMMDDHHmm`）のサブフォルダを作成します。

```python
from kzemi_tools import create_output_dir

output_path = create_output_dir("/content/drive/MyDrive/卿瑞")
# 出力されるファイルはここに保存： /content/drive/MyDrive/卿瑞/出力ファイル/202604141530
```

**引数**

| 引数 | 型 | 説明 |
|------|----|------|
| `cwd` | `str` | カレントワーキングディレクトリのパス |

**戻り値** — `str`（作成されたフォルダの絶対パス）

## 必要環境

- Python >= 3.10
- pandas
