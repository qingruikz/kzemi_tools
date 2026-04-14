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
from kzemi_tools import read_csv, clean_estat_csv

raw_df = read_csv("FEI_PREF_250703135154.csv")
df, units = clean_estat_csv(raw_df)

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
| `df` | `DataFrame` | `read_csv` 等で読み込んだ e-Stat の DataFrame |

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

### `extract_time_series` — 時系列データの抽出

指定した地域の時系列データを抽出します。

```python
from kzemi_tools import extract_time_series

# 全国の時系列データ
national_ts = extract_time_series(df, "全国")

# 特定の都道府県・市区町村でも可
sapporo_ts = extract_time_series(df, "北海道 札幌市")
```

**引数**

| 引数 | 型 | 説明 |
|------|----|------|
| `df` | `DataFrame` | `clean_estat_csv` で取得した DataFrame |
| `region` | `str` | 抽出対象の地域名（例: `"全国"`, `"北海道"`, `"北海道 紋別市"`） |

**戻り値** — `DataFrame`（指定地域の時系列データ）

### `extract_cross_section` — クロスセクションデータの抽出

指定した年の横断面データを抽出します。欠損値は後方補完（bfill）で埋めます。

```python
from kzemi_tools import extract_cross_section

# 2016年の都道府県データ（「全国」を除外）
region_cs = extract_cross_section(df, year=2016, exclude="全国")

# 2018年の市区町村データ（「北海道」を除外）
city_cs = extract_cross_section(df, year=2018, exclude="北海道")

# 除外なしで全地域を取得
all_cs = extract_cross_section(df, year=2020)
```

**引数**

| 引数 | 型 | 説明 |
|------|----|------|
| `df` | `DataFrame` | `clean_estat_csv` で取得した DataFrame |
| `year` | `int` | 調査年（整数、例: `2016`） |
| `exclude` | `str \| None` | 除外する地域名（例: `"全国"`, `"北海道"`）。省略時は除外なし |

**戻り値** — `DataFrame`（指定年のクロスセクションデータ）

### `read_csv` — CSV 読み込み

Shift-JIS エンコーディング、欠損値（`"-"`, `"***"`）、桁区切りカンマに対応した設定で CSV を読み込みます。

```python
from kzemi_tools import read_csv

CWD = "/content/drive/MyDrive/卿瑞"
parsed_df = read_csv(CWD + "/処理済みデータ/parsed_data.csv")
```

**引数**

| 引数 | 型 | 説明 |
|------|----|------|
| `filepath` | `str` | CSV ファイルのパス |

**戻り値** — `DataFrame`

## 必要環境

- Python >= 3.10
- pandas
