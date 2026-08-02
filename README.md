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
#   変数名   単位                                              出典
# 0 総人口   万人  eStat「都道府県・市区町村のすがた(社会・人口統計体系)」データベース
# 1 面積    km2  eStat「都道府県・市区町村のすがた(社会・人口統計体系)」データベース
# ...

print(df.head())
```

**引数**

| 引数 | 型          | 説明                                          |
| ---- | ----------- | --------------------------------------------- |
| `df` | `DataFrame` | `read_csv` 等で読み込んだ e-Stat の DataFrame |

**戻り値** — `(df, units)` のタプル

| 値      | 型          | 説明                                                                                                                   |
| ------- | ----------- | ---------------------------------------------------------------------------------------------------------------------- |
| `df`    | `DataFrame` | 列名を整形済みの DataFrame。`/項目` 列は除外され、`調査年` は整数に変換され、`地域`・`調査年` の降順で並べ替えられます |
| `units` | `DataFrame` | `変数名`・`単位`・`出典` の 3 列を持つ DataFrame                                                                       |

### `create_output_dir` — 出力フォルダ作成

カレントワーキングディレクトリ内の `出力ファイル/` フォルダに、現在時刻（`YYYYMMDDHHmm`）のサブフォルダを作成します。

```python
from kzemi_tools import create_output_dir

output_path = create_output_dir("/content/drive/MyDrive/卿瑞")
# 出力されるファイルはここに保存： /content/drive/MyDrive/卿瑞/出力ファイル/202604141530
```

**引数**

| 引数  | 型    | 説明                                 |
| ----- | ----- | ------------------------------------ |
| `cwd` | `str` | カレントワーキングディレクトリのパス |

**戻り値** — `str`（作成されたフォルダの絶対パス）

### `extract_panel` — パネルデータの抽出

全地域・全年のパネルデータを抽出します。`exclude` に指定した地域は、**全ての年の行が**除外されます。「全国」のような合計行を落として分析用のパネルを作るのに使います。

```python
from kzemi_tools import extract_panel

# 「全国」を除いた 都道府県 × 調査年 のパネル
panel = extract_panel(df, exclude="全国")

# 複数の地域を除外（リストで指定）
panel = extract_panel(df, exclude=["全国", "北海道"])

# 除外なしで全地域を取得
panel = extract_panel(df)
```

**引数**

| 引数      | 型                          | 説明                                                                       |
| --------- | --------------------------- | -------------------------------------------------------------------------- |
| `df`      | `DataFrame`                 | `clean_estat_csv` で取得した DataFrame                                     |
| `exclude` | `str \| list[str] \| None`  | 除外する地域名。文字列またはそのリスト。省略時は除外なし                   |

**戻り値** — `DataFrame`（パネルデータ）

> `exclude` は `extract_time_series` / `extract_cross_section` でも同じ形式で指定できます。データに存在しない地域名が含まれていても無視されるので、複数のデータで同じ除外リストを使い回せます。
>
> 欠損値の補完は行いません。

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

| 引数      | 型                          | 説明                                                            |
| --------- | --------------------------- | --------------------------------------------------------------- |
| `df`      | `DataFrame`                 | `clean_estat_csv` で取得した DataFrame                          |
| `region`  | `str`                       | 抽出対象の地域名（例: `"全国"`, `"北海道"`, `"北海道 紋別市"`） |
| `exclude` | `str \| list[str] \| None`  | 除外する地域名。`region` で 1 地域に絞るため通常は不要          |

**戻り値** — `DataFrame`（指定地域の時系列データ）

### `extract_cross_section` — クロスセクションデータの抽出

指定した年の横断面データを抽出します。欠損値の補完は行いません。

```python
from kzemi_tools import extract_cross_section

# 2016年の都道府県データ（「全国」を除外）
region_cs = extract_cross_section(df, year=2016, exclude="全国")

# 2018年の市区町村データ（「北海道」を除外）
city_cs = extract_cross_section(df, year=2018, exclude="北海道")

# 複数の地域を除外（リストで指定）
region_cs = extract_cross_section(df, year=2016, exclude=["全国", "北海道"])

# 除外なしで全地域を取得
all_cs = extract_cross_section(df, year=2020)
```

**引数**

| 引数      | 型                          | 説明                                                     |
| --------- | --------------------------- | -------------------------------------------------------- |
| `df`      | `DataFrame`                 | `clean_estat_csv` で取得した DataFrame                   |
| `year`    | `int`                       | 調査年（整数、例: `2016`）                               |
| `exclude` | `str \| list[str] \| None`  | 除外する地域名。文字列またはそのリスト。省略時は除外なし |

**戻り値** — `DataFrame`（指定年のクロスセクションデータ）

### `make_lag` / `make_lead` — 滞後変数・先行変数の生成

パネルデータに「〇年前」「〇年後」の値を列として追加します。

**前提条件**

- `id_col`（地域）と `year_col`（調査年）を持つパネルデータであること
- 1 行 = 1 地域 1 年であること（`地域`・`調査年` の組み合わせに重複がないこと）
- `調査年` が連続していること（`2023, 2024, 2025` のように 1 年刻み）

該当する年の行が存在しない場合、その値は欠損（`NaN`）になります。補完は行いません。

```python
from kzemi_tools import make_lag, make_lead

# 3 年前の総人口と 5 年前の県内総生産を追加
panel = make_lag(df, columns={"総人口": 3, "県内総生産": 5})
# → 「総人口（3年前）」「県内総生産（5年前）」列が追加される

# 5 年後の県内総生産を追加
panel = make_lead(df, columns={"県内総生産": 5})
# → 「県内総生産（5年後）」列が追加される

# drop_original=True で、作成元の列を削除する
panel = make_lag(df, columns={"総人口": 3}, drop_original=True)
# → 「総人口（3年前）」が追加され、「総人口」は削除される
```

追加された列はそのまま可視化・回帰分析に使えます。

```python
regplot(data=extract_cross_section(panel, 2025), x="総人口（3年前）", y="県内総生産")
```

**引数**

| 引数 | 型 | 説明 |
|------|----|------|
| `df` | `DataFrame` | パネルデータの DataFrame |
| `columns` | `dict[str, int]` | `{変数名: 年数}` の辞書（例: `{"総人口": 3, "県内総生産": 5}`） |
| `id_col` | `str` | 個体を識別する列名（デフォルト: `"地域"`） |
| `year_col` | `str` | 年を表す列名（整数、デフォルト: `"調査年"`） |
| `drop_original` | `bool` | `True` で作成元の列を削除（デフォルト: `False`） |

**戻り値** — `DataFrame`（元の列 + 滞後・先行変数の列。`地域`・`調査年` の降順に並べ替え）

> 元の `df` は変更されません。
>
> `make_lead` は将来の値を持ってくるため、**原則として被説明変数に対してのみ**使ってください（例: 現在の人口構成で「5 年後の県内総生産」を説明する）。将来の説明変数で現在の被説明変数を説明することは正当化できません。

### `read_csv` — CSV 読み込み

欠損値（`"-"`, `"***"`）、桁区切りカンマに対応した設定で CSV を読み込みます。  
エンコーディングは自動判定されるので、e-Stat からダウンロードした Shift-JIS の CSV でも、`to_csv` で保存した UTF-8 の CSV でもそのまま読めます。

```python
from kzemi_tools import read_csv

CWD = "/content/drive/MyDrive/卿瑞"

# e-Stat の生 CSV（Shift-JIS）
raw_df = read_csv(CWD + "/元データ/FEI_PREF_250703135154.csv")

# to_csv で保存した CSV（UTF-8 BOM 付き）
parsed_df = read_csv(CWD + "/処理済みデータ/parsed_data.csv")
```

**引数**

| 引数       | 型            | 説明                                                                        |
| ---------- | ------------- | --------------------------------------------------------------------------- |
| `filepath` | `str`         | CSV ファイルのパス                                                          |
| `encoding` | `str \| None` | エンコーディングを明示指定する場合に使用。省略時は自動判定（Shift-JIS 優先） |

**戻り値** — `DataFrame`

> 自動判定は「BOM の有無 → UTF-8 として妥当か → Shift-JIS（cp932）」の順に調べます。UTF-8 のファイルを Shift-JIS として読むと例外が出ずに文字化けするだけのことがあるため、先に UTF-8 かどうかを判定しています。

### `to_csv` — CSV 保存

`DataFrame` を CSV に保存します。インデックスは書き出しません。保存先のフォルダが無い場合は自動で作成します。

```python
from kzemi_tools import to_csv

# デフォルトは UTF-8（BOM 付き）
to_csv(parsed_df, CWD + "/処理済みデータ/parsed_data.csv")

# Shift-JIS で保存したい場合
to_csv(parsed_df, CWD + "/処理済みデータ/parsed_data.csv", encoding="shift_jis")
```

**引数**

| 引数       | 型          | 説明                                            |
| ---------- | ----------- | ----------------------------------------------- |
| `df`       | `DataFrame` | 保存する DataFrame                              |
| `filepath` | `str`       | 保存先のパス                                    |
| `encoding` | `str`       | エンコーディング（デフォルト: `"utf-8-sig"`）   |

**戻り値** — なし（保存先のパスを表示します）

> デフォルトの `"utf-8-sig"` は BOM 付き UTF-8 です。BOM があることで Excel が文字コードを正しく認識するため、ダブルクリックしても文字化けしません。BOM なしの `"utf-8"`（pandas の `df.to_csv` のデフォルト）だと Excel で文字化けするので注意してください。

### `regplot` — 散布図（回帰直線付き）

```python
from kzemi_tools import regplot

regplot(data=region_cs, x="総人口", y="森林面積割合", year=2016, output_dir=output_path)
```

| 引数         | 型            | 説明                                         |
| ------------ | ------------- | -------------------------------------------- |
| `data`       | `DataFrame`   | クロスセクション DataFrame                   |
| `x`          | `str`         | x 軸の変数名                                 |
| `y`          | `str`         | y 軸の変数名                                 |
| `year`       | `int \| None` | 調査年（タイトル・ファイル名に使用）。省略可 |
| `output_dir` | `str \| None` | 保存先フォルダのパス。省略時は保存しない     |

### `lineplot` — 折れ線グラフ（時系列推移）

```python
from kzemi_tools import lineplot

lineplot(data=national_ts, y="総人口", output_dir=output_path)
```

| 引数         | 型            | 説明                                     |
| ------------ | ------------- | ---------------------------------------- |
| `data`       | `DataFrame`   | 時系列 DataFrame（`調査年` 列を含む）    |
| `y`          | `str`         | y 軸の変数名                             |
| `output_dir` | `str \| None` | 保存先フォルダのパス。省略時は保存しない |

### `histplot` — ヒストグラム

```python
from kzemi_tools import histplot

histplot(data=region_cs, x="森林面積割合", year=2016, output_dir=output_path)
```

| 引数         | 型            | 説明                                         |
| ------------ | ------------- | -------------------------------------------- |
| `data`       | `DataFrame`   | クロスセクション DataFrame                   |
| `x`          | `str`         | x 軸の変数名                                 |
| `year`       | `int \| None` | 調査年（タイトル・ファイル名に使用）。省略可 |
| `output_dir` | `str \| None` | 保存先フォルダのパス。省略時は保存しない     |

### `barplot` — 棒グラフ（ランキング）

```python
from kzemi_tools import barplot

barplot(data=region_cs, y="森林面積割合", year=2016, output_dir=output_path)

# 上位 10 件だけ表示
barplot(data=city_cs, y="森林面積割合", top=10)

# 小さい順に並べて下位 20 件を表示
barplot(data=city_cs, y="森林面積割合", top=20, ascending=True)

# 件数を絞らずすべて表示
barplot(data=region_cs, y="森林面積割合", top=None)
```

| 引数         | 型            | 説明                                                             |
| ------------ | ------------- | ---------------------------------------------------------------- |
| `data`       | `DataFrame`   | クロスセクション DataFrame（`地域` 列を含む）                    |
| `y`          | `str`         | y 軸の変数名                                                     |
| `year`       | `int \| None` | 調査年（タイトル・ファイル名に使用）。省略可                     |
| `output_dir` | `str \| None` | 保存先フォルダのパス。省略時は保存しない                         |
| `top`        | `int \| None` | 表示する件数（デフォルト: `50`）。`None` ですべて表示            |
| `ascending`  | `bool`        | `True` で昇順（小さい順）。デフォルトは降順（大きい順）          |

> 市区町村データのように件数が多い場合、すべて表示すると軸ラベルが読めなくなるため、デフォルトで `50` 件に制限しています。件数を絞ったときはその旨が表示され、保存ファイル名にも `（上位50件）` のように付きます。

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

| 引数        | 型          | 説明                     |
| ----------- | ----------- | ------------------------ |
| `df_result` | `DataFrame` | 回帰分析の結果 DataFrame |

**戻り値** — `list[str]`（モデル式の文字列リスト）

> `generate_model_formulas` は表示なしでリストのみ返します。

### `generate_data_source` — データソース表の生成

記述統計量の変数名と単位情報から、データソース表（変数・単位・出典）を生成します。  
出典は `units_df` の `出典` 列から変数ごとに引かれます（`clean_estat_csv` が自動で付与）。

`総人口の 2 乗`、`総人口の対数`、`総人口（3年前）`、`総人口（5年後）` など派生変数は自動的に元の `総人口` に集約されます。`総人口の対数（3年前）` のように複合していても集約されます。集約後は重複が除かれるため、**1 つの変数につき必ず 1 行**になります。

回帰結果の表を渡した場合、`定数項` 以降の統計量（`決定係数`・`自由度修正済み決定係数`・`観測数` など）と、標準誤差の行（インデックスが `NaN` や空文字）は自動的に除外されます。

```python
from kzemi_tools import generate_data_source

data_source = generate_data_source(df_result, units_df)
#     変数    単位                                              出典
# 0   総人口   万人  eStat「都道府県・市区町村のすがた(社会・人口統計体系)」データベース
# 1   年平均気温  ﾟC                                          気象庁
# ...
```

`compact=True` にすると、出典を出現順に `a`, `b`, `c`… の記号で表示し、対応を示す注釈文を表示します。出典が長いときに表を読みやすくするためのオプションです。

```python
data_source = generate_data_source(df_result, units_df, compact=True)
# （注）1）データの出典について、aはeStat「都道府県・市区町村のすがた(社会・人口統計体系)」データベース、bは気象庁を意味する。
#     変数    単位  出典
# 0   総人口   万人   a
# 1   年平均気温  ﾟC   b
```

**引数**

| 引数         | 型          | 説明                                                                         |
| ------------ | ----------- | ---------------------------------------------------------------------------- |
| `df_summary` | `DataFrame` | 記述統計量または回帰結果の DataFrame（インデックスが変数名）                 |
| `units`      | `DataFrame` | `clean_estat_csv` で取得した `変数名`・`単位`・`出典` の 3 列を持つ DataFrame |
| `compact`    | `bool`      | `True` で出典を `a`, `b`, `c`… の記号にし、注釈文を表示（デフォルト: `False`） |

**戻り値** — `DataFrame`（`変数`, `単位`, `出典` の 3 列）

> 出典を差し替えたい場合は、`units_df["出典"]` を書き換えてから渡してください。

## 必要環境

- Python >= 3.10
- pandas, matplotlib, seaborn, japanize-matplotlib
