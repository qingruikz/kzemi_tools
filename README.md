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

### `regplot` — 散布図（回帰直線付き）

```python
from kzemi_tools import regplot

regplot(data=region_cs, x="総人口", y="森林面積割合", year=2016, output_dir=output_path)
```

| 引数 | 型 | 説明 |
|------|----|------|
| `data` | `DataFrame` | クロスセクション DataFrame |
| `x` | `str` | x 軸の変数名 |
| `y` | `str` | y 軸の変数名 |
| `year` | `int \| None` | 調査年（タイトル・ファイル名に使用）。省略可 |
| `output_dir` | `str \| None` | 保存先フォルダのパス。省略時は保存しない |

### `lineplot` — 折れ線グラフ（時系列推移）

```python
from kzemi_tools import lineplot

lineplot(data=national_ts, y="総人口", output_dir=output_path)
```

| 引数 | 型 | 説明 |
|------|----|------|
| `data` | `DataFrame` | 時系列 DataFrame（`調査年` 列を含む） |
| `y` | `str` | y 軸の変数名 |
| `output_dir` | `str \| None` | 保存先フォルダのパス。省略時は保存しない |

### `histplot` — ヒストグラム

```python
from kzemi_tools import histplot

histplot(data=region_cs, x="森林面積割合", year=2016, output_dir=output_path)
```

| 引数 | 型 | 説明 |
|------|----|------|
| `data` | `DataFrame` | クロスセクション DataFrame |
| `x` | `str` | x 軸の変数名 |
| `year` | `int \| None` | 調査年（タイトル・ファイル名に使用）。省略可 |
| `output_dir` | `str \| None` | 保存先フォルダのパス。省略時は保存しない |

### `barplot` — 棒グラフ（ランキング）

```python
from kzemi_tools import barplot

barplot(data=region_cs, y="森林面積割合", year=2016, output_dir=output_path)
```

| 引数 | 型 | 説明 |
|------|----|------|
| `data` | `DataFrame` | クロスセクション DataFrame（`地域` 列を含む） |
| `y` | `str` | y 軸の変数名 |
| `year` | `int \| None` | 調査年（タイトル・ファイル名に使用）。省略可 |
| `output_dir` | `str \| None` | 保存先フォルダのパス。省略時は保存しない |

### `print_model_formulas` / `generate_model_formulas` — 回帰モデル式の生成

回帰分析の結果 DataFrame から、各モデルの識別戦略（モデル式）を自動生成します。

```python
from kzemi_tools import print_model_formulas

formulas = print_model_formulas(df_result)
# モデル（1）：財政力指数（都道府県財政） = α + β1 総人口 + 攪乱項
# モデル（2）：財政力指数（都道府県財政） = α + β1 総人口 + β2 総人口の 2 乗 + 攪乱項
# モデル（3）：財政力指数（都道府県財政） = α + β1 総人口 + β2 年平均気温 + 攪乱項
# ...
```

`df_result` の形式:
- **列名**: `"（1）\n被説明変数名"` のように、モデル番号と被説明変数名を `\n` で区切る
- **インデックス**: 説明変数名（空行あり）、`定数項` 以降は統計量（`決定係数` 等）

**引数**

| 引数 | 型 | 説明 |
|------|----|------|
| `df_result` | `DataFrame` | 回帰分析の結果 DataFrame |

**戻り値** — `list[str]`（モデル式の文字列リスト）

> `generate_model_formulas` は表示なしでリストのみ返します。

### `generate_data_source` — データソース表の生成

記述統計量の変数名と単位情報から、データソース表（変数・単位・出典）を生成します。  
`総人口の 2 乗` や `総人口の対数` など派生変数は自動的に元の `総人口` に集約されます。

```python
from kzemi_tools import generate_data_source

data_source = generate_data_source(df_result, units_df, source="e-Stat 社会・人口統計体系")
#     変数    単位              出典
# 0   総人口   万人   e-Stat 社会・人口統計体系
# 1   年平均気温  ﾟC   e-Stat 社会・人口統計体系
# ...
```

**引数**

| 引数 | 型 | 説明 |
|------|----|------|
| `df_summary` | `DataFrame` | 記述統計量または回帰結果の DataFrame（インデックスが変数名） |
| `units` | `DataFrame` | `変数名` と `単位` の 2 列を持つ DataFrame |
| `source` | `str` | 出典（デフォルト: 空文字） |

**戻り値** — `DataFrame`（`変数`, `単位`, `出典` の 3 列）

## 必要環境

- Python >= 3.10
- pandas, matplotlib, seaborn, japanize-matplotlib
