# BricsCAD 社内標準テンプレート

## ファイル構成

```
templates/
  A2_template.dxf   — A2横 (594×420mm) テンプレート
  A3_template.dxf   — A3横 (420×297mm) テンプレート
  A4_template.dxf   — A4横 (297×210mm) テンプレート

scripts/
  create_templates.py  — テンプレート生成スクリプト (Python/ezdxf)
```

## テンプレート内容

### レイヤ構成 (29レイヤ)

| レイヤ名 | 色 | 線種 | 線幅 | 用途 |
|---|---|---|---|---|
| 0 | 白 | Continuous | ByLayer | デフォルト |
| A-WALL | 白 | Continuous | 0.50mm | 壁 |
| A-WALL-FULL | 白 | Continuous | 0.50mm | 壁(仕上含む) |
| A-COLS | 白 | Continuous | 0.70mm | 柱 |
| A-GLAZ | 水色 | Continuous | 0.13mm | ガラス・窓 |
| A-DOOR | 水色 | Continuous | 0.13mm | ドア・建具 |
| A-FLOR | 緑 | Continuous | 0.13mm | 床 |
| A-CEIL | マゼンタ | Continuous | 0.13mm | 天井 |
| A-ROOF | 白 | Continuous | 0.50mm | 屋根 |
| A-STRS | 白 | Continuous | 0.25mm | 階段 |
| A-SITE | 緑 | Continuous | 0.25mm | 外構・敷地 |
| A-GRID | 赤 | CENTER | 0.13mm | 通り芯 |
| A-GRID-SYMB | 赤 | Continuous | 0.13mm | 通り芯記号 |
| A-ANNO-DIMS | 白 | Continuous | 0.13mm | 寸法線 |
| A-ANNO-TEXT | 白 | Continuous | 0.13mm | 文字・注記 |
| A-ANNO-SYMB | 白 | Continuous | 0.13mm | 記号・マーク |
| A-ANNO-TTLB | 白 | Continuous | 0.25mm | 表題欄 |
| A-ANNO-FRAM | 白 | Continuous | 0.50mm | 図枠 |
| A-HATCH | グレー | Continuous | 0.13mm | ハッチング |
| A-HATCH-SOIL | 茶 | Continuous | 0.13mm | ハッチング(土) |
| E-LITE | 黄 | Continuous | 0.13mm | 電気(照明) |
| E-POWR | 黄 | Continuous | 0.13mm | 電気(コンセント) |
| E-COMM | 青 | Continuous | 0.13mm | 電気(通信) |
| P-PIPE-WATER | 水色 | Continuous | 0.13mm | 給水配管 |
| P-PIPE-DRAIN | マゼンタ | Continuous | 0.13mm | 排水配管 |
| P-PIPE-GAS | 赤 | Continuous | 0.13mm | ガス配管 |
| M-HVAC | 緑 | Continuous | 0.13mm | 空調設備 |
| DEFPOINTS | 白 | Continuous | ByLayer | 寸法補助点(印刷なし) |
| _ACS | 白 | Continuous | ByLayer | 補助座標系 |

### 線種

- `Continuous` — 実線
- `CENTER` / `CENTERX2` / `CENTER2` — 一点鎖線
- `DASHED` / `DASHEDX2` / `DASHED2` — 破線
- `HIDDEN` — 隠れ線
- `PHANTOM` / `PHANTOMX2` / `PHANTOM2` — 二点鎖線
- `DASHDOT` / `DOTTED` — 一点鎖線・点線バリアント

### テキストスタイル

| スタイル名 | フォント | 用途 |
|---|---|---|
| Standard | arial.ttf | 標準英数字 |
| JIS_TEXT | msmincho.ttc | 日本語明朝体 |
| JIS_GOTH | msgothic.ttc | 日本語ゴシック体 |
| TITLE | arial.ttf | タイトル用 |
| DIMS | arial.ttf | 寸法数字用 |
| SHX_STD | txt.shx | SHXフォント(互換) |

### 寸法スタイル (JIS準拠)

| スタイル名 | 縮尺 | 文字高 | 矢印 |
|---|---|---|---|
| Standard | — | 2.5mm | 斜めティック |
| JIS-1_20 | 1:20 | 2.5mm相当 | 斜めティック |
| JIS-1_50 | 1:50 | 2.5mm相当 | 斜めティック |
| JIS-1_100 | 1:100 | 2.5mm相当 | 斜めティック |
| JIS-1_200 | 1:200 | 2.5mm相当 | 斜めティック |

### 図枠・表題欄

各用紙サイズに下記を配置：
- **図枠**: 左マージン25mm(綴じ代)、他10mm
- **表題欄** (右下 180×40mm): 会社名・工事名称・図面名称・縮尺・図番・日付・作成者・確認者
- **改訂履歴欄** (右上 80mm幅×5行): Rev・日付・内容・担当
- **中心マーク**: 4辺中央
- **トリミングマーク**: 4隅

## 使用方法

1. BricsCAD で `.dxf` ファイルを開く
2. `SAVEAS` コマンドで `.dwt` (テンプレート形式) として保存
3. オプション → テンプレートフォルダに配置

## テンプレート再生成

```bash
pip install ezdxf
python3 scripts/create_templates.py
```
