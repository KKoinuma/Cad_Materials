"""
BricsCAD 標準テンプレート生成スクリプト
JIS建築CAD標準に準拠したA2/A3/A4テンプレートを作成する
"""

import ezdxf
from ezdxf import colors
from ezdxf.enums import TextEntityAlignment
import math

# ============================================================
# 定数定義
# ============================================================

PAPER_SIZES = {
    "A2": (594, 420),   # 横置き
    "A3": (420, 297),
    "A4": (297, 210),
}

# 図枠マージン (mm)
FRAME_MARGIN_LEFT   = 25  # 綴じ代
FRAME_MARGIN_RIGHT  = 10
FRAME_MARGIN_TOP    = 10
FRAME_MARGIN_BOTTOM = 10

# 表題欄サイズ
TITLE_BLOCK_HEIGHT = 40   # 図面下端からの高さ
TITLE_BLOCK_WIDTH  = 180  # 右端からの幅

# ============================================================
# レイヤ定義 (名前, 色番号, 線種, 線幅[mm*100])
# ACI color: 1=赤,2=黄,3=緑,4=水色,5=青,6=マゼンタ,7=白/黒
# ============================================================

LAYERS = [
    # (name,                color, linetype,     lineweight, description)
    ("0",                   7,    "Continuous",  -3,   "デフォルト"),
    # --- 建築 ---
    ("A-WALL",              7,    "Continuous",  50,   "壁 (仕上なし)"),
    ("A-WALL-FULL",         7,    "Continuous",  50,   "壁 (仕上げ含む)"),
    ("A-COLS",              7,    "Continuous",  70,   "柱"),
    ("A-GLAZ",              4,    "Continuous",  13,   "ガラス・窓"),
    ("A-DOOR",              4,    "Continuous",  13,   "ドア・建具"),
    ("A-FLOR",              3,    "Continuous",  13,   "床"),
    ("A-CEIL",              6,    "Continuous",  13,   "天井"),
    ("A-ROOF",              7,    "Continuous",  50,   "屋根"),
    ("A-STRS",              7,    "Continuous",  25,   "階段"),
    ("A-SITE",              3,    "Continuous",  25,   "外構・敷地"),
    # --- 通り芯 ---
    ("A-GRID",              1,    "CENTER",      13,   "通り芯"),
    ("A-GRID-SYMB",         1,    "Continuous",  13,   "通り芯記号"),
    # --- 注釈 ---
    ("A-ANNO-DIMS",         7,    "Continuous",  13,   "寸法線"),
    ("A-ANNO-TEXT",         7,    "Continuous",  13,   "文字・注記"),
    ("A-ANNO-SYMB",         7,    "Continuous",  13,   "記号・マーク"),
    ("A-ANNO-TTLB",         7,    "Continuous",  25,   "表題欄"),
    ("A-ANNO-FRAM",         7,    "Continuous",  50,   "図枠"),
    # --- ハッチング ---
    ("A-HATCH",             253,  "Continuous",  13,   "ハッチング (コンクリート等)"),
    ("A-HATCH-SOIL",        32,   "Continuous",  13,   "ハッチング (土・地盤)"),
    # --- 設備 ---
    ("E-LITE",              2,    "Continuous",  13,   "電気 (照明)"),
    ("E-POWR",              2,    "Continuous",  13,   "電気 (コンセント・動力)"),
    ("E-COMM",              5,    "Continuous",  13,   "電気 (通信・弱電)"),
    ("P-PIPE-WATER",        4,    "Continuous",  13,   "給水配管"),
    ("P-PIPE-DRAIN",        6,    "Continuous",  13,   "排水配管"),
    ("P-PIPE-GAS",          1,    "Continuous",  13,   "ガス配管"),
    ("M-HVAC",              3,    "Continuous",  13,   "空調設備"),
    # --- 補助 ---
    ("DEFPOINTS",           7,    "Continuous",  -3,   "寸法補助点 (印刷なし)"),
    ("_ACS",                7,    "Continuous",  -3,   "補助座標系"),
]

# ============================================================
# 線種定義
# ============================================================

LINETYPES = [
    # (name, description, pattern)
    ("CENTER",   "一点鎖線 __ _ __ _",  [12.0, 6.0, -3.0, 3.0, -3.0]),
    ("DASHED",   "破線 __ __ __",        [6.0, 6.0, -3.0]),
    ("HIDDEN",   "隠れ線 _ _ _ _",       [3.0, 3.0, -1.5]),
    ("PHANTOM",  "二点鎖線 __ . . __ . .", [12.0, 6.0, -3.0, 1.5, -3.0, 1.5, -3.0]),
    ("DOTTED",   "点線 . . . . .",        [0.0, 0.0, -3.0]),
]

# ============================================================
# テキストスタイル定義
# ============================================================

TEXT_STYLES = [
    # (name,     font_file,        big_font,       height, width_factor)
    ("Standard", "arial.ttf",      "",             0,      1.0),
    ("JIS_TEXT", "msmincho.ttc",   "",             0,      1.0),  # 明朝体
    ("JIS_GOTH", "msgothic.ttc",   "",             0,      1.0),  # ゴシック体
    ("TITLE",    "arial.ttf",      "",             0,      1.0),
    ("DIMS",     "arial.ttf",      "",             0,      1.0),
    ("SHX_STD",  "txt.shx",        "bigfont.shx",  0,      1.0),
]

# ============================================================
# 寸法スタイル定義
# ============================================================

def setup_dimstyle(doc, name, text_height=2.5, arrow_size=2.0, scale=1.0):
    """JIS準拠の寸法スタイルを設定"""
    dimstyles = doc.dimstyles
    if name in dimstyles:
        dstyle = dimstyles.get(name)
    else:
        dstyle = dimstyles.new(name)

    dstyle.dxf.dimtxt = text_height    # 文字高さ
    dstyle.dxf.dimasz = arrow_size     # 矢印サイズ
    dstyle.dxf.dimexe = 1.5           # 寸法補助線延長
    dstyle.dxf.dimexo = 1.0           # 寸法補助線オフセット
    dstyle.dxf.dimgap = 1.0           # 寸法文字と線のギャップ
    dstyle.dxf.dimscale = scale        # 全体スケール
    dstyle.dxf.dimdec = 0             # 小数点以下桁数 (0=整数mm)
    dstyle.dxf.dimrnd = 1.0           # 丸め (1mm単位)
    dstyle.dxf.dimclrd = 256          # 寸法線色 (ByLayer)
    dstyle.dxf.dimclre = 256          # 補助線色 (ByLayer)
    dstyle.dxf.dimclrt = 256          # 文字色 (ByLayer)
    dstyle.dxf.dimtad = 1             # 文字を寸法線の上に配置
    dstyle.dxf.dimtoh = 0             # 寸法線外の文字を水平にしない
    dstyle.dxf.dimtih = 0             # 寸法線内の文字を水平にしない
    # 矢印タイプ (0=closed filled, 3=dot, 6=oblique/tick)
    dstyle.dxf.dimblk = "OBLIQUE"    # 建築用斜めティック
    dstyle.dxf.dimblk1 = "OBLIQUE"
    dstyle.dxf.dimblk2 = "OBLIQUE"
    dstyle.dxf.dimtsz = arrow_size    # ティックサイズ
    dstyle.dxf.dimtxsty = "DIMS"
    return dstyle


# ============================================================
# 表題欄描画
# ============================================================

def draw_title_block(msp, x0, y0, width, height, paper_name):
    """
    右下に表題欄を描画
    x0,y0 = 左下角 (図枠内)
    """
    tb_layer = "A-ANNO-TTLB"
    txt_height_label = 2.0
    txt_height_value = 3.0
    txt_height_title = 4.5

    # 外枠
    msp.add_lwpolyline(
        [(x0, y0), (x0+width, y0), (x0+width, y0+height), (x0, y0+height), (x0, y0)],
        dxfattribs={"layer": tb_layer, "lineweight": 50}
    )

    # 列分割線 (縦)
    # | 会社名/ロゴ | 工事名称 | 図面名称 | 縮尺 | 図番 | 日付 |
    col_widths = [40, 60, 30, 15, 15, 20]  # 計180mm
    col_x = [x0]
    for w in col_widths:
        col_x.append(col_x[-1] + w)

    for cx in col_x[1:-1]:
        msp.add_line(
            (cx, y0), (cx, y0+height),
            dxfattribs={"layer": tb_layer, "lineweight": 25}
        )

    # 行分割線 (横)
    row_heights = [height/2, height/2]
    row_y = [y0, y0 + row_heights[0], y0 + height]

    for ry in row_y[1:-1]:
        msp.add_line(
            (x0, ry), (x0+width, ry),
            dxfattribs={"layer": tb_layer, "lineweight": 25}
        )

    mid_y = row_y[1]

    # ラベルテキスト
    labels_top    = ["会社名", "工事名称",     "図面名称",   "縮尺",   "図番",   "日付"]
    labels_bottom = ["",       "工　事　場　所", "設計・監理者", "作成者", "確認者", "改訂"]

    for i, (label, col_start) in enumerate(zip(labels_top, col_x)):
        cx_center = col_start + col_widths[i] / 2
        # ラベル (小)
        msp.add_text(
            label,
            dxfattribs={
                "layer": tb_layer,
                "height": txt_height_label,
                "style": "Standard",
                "color": 256,
            }
        ).set_placement(
            (cx_center, y0 + height - 3),
            align=TextEntityAlignment.TOP_CENTER
        )

    for i, (label, col_start) in enumerate(zip(labels_bottom, col_x)):
        if not label:
            continue
        cx_center = col_start + col_widths[i] / 2
        msp.add_text(
            label,
            dxfattribs={
                "layer": tb_layer,
                "height": txt_height_label,
                "style": "Standard",
                "color": 256,
            }
        ).set_placement(
            (cx_center, mid_y + (height/2) - 3),
            align=TextEntityAlignment.TOP_CENTER
        )

    # ペーパーサイズ表示
    msp.add_text(
        paper_name,
        dxfattribs={
            "layer": tb_layer,
            "height": txt_height_label,
            "style": "Standard",
            "color": 253,
        }
    ).set_placement(
        (x0 + 3, y0 + height - 3),
        align=TextEntityAlignment.TOP_LEFT
    )


# ============================================================
# 改訂履歴欄
# ============================================================

def draw_revision_block(msp, x0, y0, width, rows=5):
    """図枠右上の改訂欄"""
    layer = "A-ANNO-TTLB"
    row_h = 7
    height = row_h * (rows + 1)

    # 外枠
    msp.add_lwpolyline(
        [(x0, y0), (x0+width, y0), (x0+width, y0+height), (x0, y0+height), (x0, y0)],
        dxfattribs={"layer": layer, "lineweight": 35}
    )

    # ヘッダ
    header = ["Rev", "年月日", "内容", "担当"]
    col_w  = [10, 22, width - 10 - 22 - 15, 15]
    cx = [x0]
    for w in col_w:
        cx.append(cx[-1] + w)

    for x in cx[1:]:
        msp.add_line((x, y0), (x, y0+height), dxfattribs={"layer": layer, "lineweight": 13})

    # ヘッダ行
    header_y = y0 + height - row_h
    msp.add_line((x0, header_y), (x0+width, header_y), dxfattribs={"layer": layer, "lineweight": 25})
    for i, h in enumerate(header):
        msp.add_text(
            h,
            dxfattribs={"layer": layer, "height": 2.0, "style": "Standard"}
        ).set_placement(
            (cx[i] + col_w[i]/2, header_y + row_h/2),
            align=TextEntityAlignment.MIDDLE_CENTER
        )

    # データ行
    for r in range(rows):
        ry = y0 + height - row_h * (r + 2)
        msp.add_line((x0, ry), (x0+width, ry), dxfattribs={"layer": layer, "lineweight": 13})


# ============================================================
# 図枠描画
# ============================================================

def draw_border(msp, paper_w, paper_h):
    """図枠・外枠・表題欄・改訂欄を一括描画"""
    frame_layer = "A-ANNO-FRAM"

    # 用紙外枠 (参考用・印刷なし)
    msp.add_lwpolyline(
        [(0,0),(paper_w,0),(paper_w,paper_h),(0,paper_h),(0,0)],
        dxfattribs={"layer": "DEFPOINTS", "lineweight": 13}
    )

    # 図枠 (内枠)
    x1 = FRAME_MARGIN_LEFT
    y1 = FRAME_MARGIN_BOTTOM
    x2 = paper_w - FRAME_MARGIN_RIGHT
    y2 = paper_h - FRAME_MARGIN_TOP

    msp.add_lwpolyline(
        [(x1,y1),(x2,y1),(x2,y2),(x1,y2),(x1,y1)],
        dxfattribs={"layer": frame_layer, "lineweight": 70}
    )

    # 表題欄 (右下)
    tb_x0 = x2 - TITLE_BLOCK_WIDTH
    tb_y0 = y1
    draw_title_block(msp, tb_x0, tb_y0, TITLE_BLOCK_WIDTH, TITLE_BLOCK_HEIGHT,
                     f"{int(paper_w)}×{int(paper_h)}")

    # 改訂欄 (右上)
    rev_w = 80
    rev_x0 = x2 - rev_w
    rev_y0 = y2 - (7 * 6)  # 5行 + ヘッダ
    draw_revision_block(msp, rev_x0, rev_y0, rev_w, rows=5)

    # 中心マーク (用紙4辺中央)
    mark_len = 5
    for (mx, my, dx, dy) in [
        (paper_w/2, 0,        0, mark_len),
        (paper_w/2, paper_h,  0, -mark_len),
        (0,         paper_h/2, mark_len, 0),
        (paper_w,   paper_h/2, -mark_len, 0),
    ]:
        msp.add_line(
            (mx, my), (mx+dx, my+dy),
            dxfattribs={"layer": frame_layer, "lineweight": 13}
        )

    # トリミングマーク (4隅)
    corner_len = 10
    for (cx2, cy2) in [(0,0),(paper_w,0),(0,paper_h),(paper_w,paper_h)]:
        sx = 1 if cx2 == 0 else -1
        sy = 1 if cy2 == 0 else -1
        msp.add_line((cx2, cy2), (cx2 + sx*corner_len, cy2),
                     dxfattribs={"layer": frame_layer, "lineweight": 13})
        msp.add_line((cx2, cy2), (cx2, cy2 + sy*corner_len),
                     dxfattribs={"layer": frame_layer, "lineweight": 13})


# ============================================================
# テンプレート生成メイン
# ============================================================

def create_template(paper_name):
    paper_w, paper_h = PAPER_SIZES[paper_name]

    doc = ezdxf.new("R2013", setup=True)
    doc.units = 4  # 4 = mm

    # ヘッダ変数設定
    doc.header["$INSUNITS"]   = 4     # mm
    doc.header["$MEASUREMENT"] = 1    # metric
    doc.header["$LUNITS"]     = 2     # decimal
    doc.header["$LUPREC"]     = 0     # 小数点以下0桁 (mm整数)
    doc.header["$AUNITS"]     = 0     # degrees
    doc.header["$AUPREC"]     = 0
    doc.header["$DIMSCALE"]   = 1.0
    doc.header["$LTSCALE"]    = 1.0
    doc.header["$CELTSCALE"]  = 1.0
    doc.header["$DIMASSOC"]   = 2
    doc.header["$LIMMIN"]     = (0.0, 0.0)
    doc.header["$LIMMAX"]     = (paper_w, paper_h)
    doc.header["$EXTMIN"]     = (0.0, 0.0, 0.0)
    doc.header["$EXTMAX"]     = (paper_w, paper_h, 0.0)
    doc.header["$PSLTSCALE"]  = 0
    doc.header["$PSVPSCALE"]  = 0.0

    # ============ 線種 ============
    ltype_table = doc.linetypes
    for lt_name, lt_desc, lt_pattern in LINETYPES:
        if lt_name not in ltype_table:
            ltype_table.new(lt_name, dxfattribs={
                "description": lt_desc,
                "pattern":     lt_pattern,
                "length":      sum(abs(p) for p in lt_pattern),
            })

    # ============ テキストスタイル ============
    styles = doc.styles
    for st_name, font, bigfont, height, width in TEXT_STYLES:
        if st_name == "Standard":
            s = styles.get("Standard")
        elif st_name in styles:
            s = styles.get(st_name)
        else:
            s = styles.new(st_name)
        try:
            s.dxf.font = font
            if bigfont:
                s.dxf.bigfont = bigfont
            s.dxf.height = height
            s.dxf.width = width
        except Exception:
            pass

    # ============ レイヤ ============
    layer_table = doc.layers
    for ly_name, ly_color, ly_ltype, ly_lw, ly_desc in LAYERS:
        if ly_name == "0":
            ly = layer_table.get("0")
        elif ly_name in layer_table:
            ly = layer_table.get(ly_name)
        else:
            ly = layer_table.new(ly_name)
        try:
            ly.dxf.color       = ly_color
            ly.dxf.linetype    = ly_ltype if ly_ltype in ltype_table else "Continuous"
            ly.dxf.lineweight  = ly_lw
        except Exception:
            pass

    # ============ 寸法スタイル ============
    # 1:50スケール用 (縮尺×テキスト高)
    scales = [
        ("JIS-1_50",   1,    2.5, 2.0, 50),
        ("JIS-1_100",  1,    2.5, 2.0, 100),
        ("JIS-1_200",  1,    2.5, 2.0, 200),
        ("JIS-1_20",   1,    2.5, 2.0, 20),
    ]
    for ds_name, _, txt_h, arr_sz, sc in scales:
        setup_dimstyle(doc, ds_name, text_height=txt_h*sc/20, arrow_size=arr_sz*sc/20, scale=1.0)

    # デフォルト寸法スタイル (Standard)
    setup_dimstyle(doc, "Standard", text_height=2.5, arrow_size=2.0, scale=1.0)

    # ============ モデル空間 ============
    msp = doc.modelspace()
    doc.layers.get("0").dxf.color = 7

    # ============ ペーパー空間レイアウト ============
    # レイアウト設定
    layouts = doc.layouts
    if paper_name in layouts:
        layout = layouts.get(paper_name)
    elif "Layout1" in layouts:
        layout = layouts.get("Layout1")
    else:
        layout = layouts.new(paper_name)
    layout.dxf.limmin = (0, 0)
    layout.dxf.limmax = (paper_w, paper_h)

    # ペーパー空間の図枠を描画
    psp = layout

    # 外枠
    psp.add_lwpolyline(
        [(0,0),(paper_w,0),(paper_w,paper_h),(0,paper_h),(0,0)],
        dxfattribs={"layer": "DEFPOINTS"}
    )

    # 図枠描画
    x1 = FRAME_MARGIN_LEFT
    y1 = FRAME_MARGIN_BOTTOM
    x2 = paper_w - FRAME_MARGIN_RIGHT
    y2 = paper_h - FRAME_MARGIN_TOP

    psp.add_lwpolyline(
        [(x1,y1),(x2,y1),(x2,y2),(x1,y2),(x1,y1)],
        dxfattribs={"layer": "A-ANNO-FRAM", "lineweight": 70}
    )

    # 表題欄
    tb_x0 = x2 - TITLE_BLOCK_WIDTH
    tb_y0 = y1
    draw_title_block(psp, tb_x0, tb_y0, TITLE_BLOCK_WIDTH, TITLE_BLOCK_HEIGHT, paper_name)

    # 改訂欄
    rev_w = 80
    rev_x0 = x2 - rev_w
    rev_y0 = y2 - (7 * 6)
    draw_revision_block(psp, rev_x0, rev_y0, rev_w, rows=5)

    # 中心マーク
    mark_len = 5
    for (mx, my, dx, dy) in [
        (paper_w/2, 0,        0, mark_len),
        (paper_w/2, paper_h,  0, -mark_len),
        (0,         paper_h/2, mark_len, 0),
        (paper_w,   paper_h/2, -mark_len, 0),
    ]:
        psp.add_line(
            (mx, my), (mx+dx, my+dy),
            dxfattribs={"layer": "A-ANNO-FRAM", "lineweight": 13}
        )

    # ============ 保存 ============
    out_path = f"/home/user/Cad_Materials/templates/{paper_name}_template.dxf"
    doc.saveas(out_path)
    print(f"✓ {paper_name} テンプレート作成: {out_path}")
    return out_path


if __name__ == "__main__":
    for paper in ["A2", "A3", "A4"]:
        create_template(paper)
    print("\n全テンプレート生成完了")
