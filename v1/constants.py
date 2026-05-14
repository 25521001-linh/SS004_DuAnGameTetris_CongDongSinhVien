# constants.py — Hằng số cho game Tetris Building V1

# ── Kích thước board ──────────────────────────────────────────────
BOARD_COLS = 10
BOARD_ROWS = 20
CELL_SIZE  = 32          # pixels mỗi ô

# ── Kích thước cửa sổ ─────────────────────────────────────────────
PANEL_W    = 180         # panel bên phải (Next, Score, Level)
SCREEN_W   = BOARD_COLS * CELL_SIZE + PANEL_W
SCREEN_H   = BOARD_ROWS * CELL_SIZE

FPS = 60

# ── Màu sắc (R, G, B) ─────────────────────────────────────────────
BLACK      = (  0,   0,   0)
WHITE      = (255, 255, 255)
GRAY       = (128, 128, 128)
DARK_GRAY  = ( 40,  40,  40)
BORDER_COL = ( 80,  80,  80)

# Màu 7 tetromino chuẩn
PIECE_COLORS = {
    'I': ( 49, 199, 239),   # cyan
    'O': (247, 211,   8),   # yellow
    'T': (173,  77, 156),   # purple
    'S': ( 66, 182,  66),   # green
    'Z': (239,  32,  41),   # red
    'J': ( 90,  90, 200),   # blue
    'L': (239, 121,  33),   # orange
}

# Màu vữa (Mortar)
MORTAR_SOLID_COLOR   = (180, 160, 120)   # vữa cứng — vàng đất
MORTAR_LIQUID_COLOR  = (220, 200,  80)   # vữa lỏng — vàng tươi
MORTAR_COAT_COLOR    = (200, 180,  60)   # lớp phủ vữa trên gạch
CRACK_COLOR          = (100,  70,  40)   # màu vết nứt

# ── Tốc độ rơi (giây mỗi bước/hàng) ──────────────────────────────
FALL_SPEEDS = {
    1:  1.00,  2:  0.85,  3:  0.72,  4:  0.60,  5:  0.50,
    6:  0.42,  7:  0.35,  8:  0.28,  9:  0.22, 10:  0.17,
}
DEFAULT_FALL_SPEED = 0.05

SOFT_DROP_MULTIPLIER = 10

# ── Vữa (Mortar) — theo GDD ───────────────────────────────────────
# Thời gian vữa chảy = cố định theo hệ thống, KHÔNG thay đổi theo level
MORTAR_MELT_TIME   = 2.5    # giây trước khi vữa hóa lỏng (GDD: 2-3 giây)
MORTAR_RATIO       = 0.25   # 25% khả năng spawn mortar (GDD: tỉ lệ gạch:vữa = 3:1)

# ── Điểm số — theo GDD ────────────────────────────────────────────
# Gạch thường (không dính vữa): +1 điểm
# Khối liên kết (Gạch + Vữa):  +2 điểm cho MỖI Ô
# Khối cứng (Vữa + Vữa):      +N điểm (N = số vữa tạo thành khối cứng)
SCORE_BRICK          = 1
SCORE_LINKED_PER_CELL = 2
SCORE_HARD_PER_UNIT  = 1

# ── Combo — theo GDD ──────────────────────────────────────────────
# Hệ số combo: nhân đôi sau mỗi nhịp
# Nhịp 1: x1, Nhịp 2: x2, Nhịp 3: x4, Nhịp 4: x8, ...
COMBO_BASE_MULTIPLIER = 1

# ── Loại ô (cell type) ────────────────────────────────────────────
CELL_EMPTY   = 0
CELL_BRICK   = 1    # gạch thường (HP 1)
CELL_MORTAR  = 2    # vữa đang cứng/chờ chảy (HP 1)
CELL_LINKED  = 3    # gạch đã bị vữa phủ (HP 2 → crack → HP 1)
CELL_HARD    = 4    # vữa+vữa kết cứng (HP 2)

# ── Wall-kick offsets (SRS đơn giản) ──────────────────────────────
WALL_KICKS = [(0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0), (0, -1)]

# ── Lock delay ────────────────────────────────────────────────────
LOCK_DELAY = 0.5    # giây chờ trước khi lock piece khi chạm đất

# ── Lines cần clear mỗi level (GDD) ──────────────────────────────
LINES_PER_LEVEL = {
    # Level 1-5: Giai đoạn Móng, 13 hàng
    1: 13, 2: 13, 3: 13, 4: 13, 5: 13,
    # Level 6-15: Giai đoạn Tường, 20 hàng
    6: 20, 7: 20, 8: 20, 9: 20, 10: 20,
    11: 20, 12: 20, 13: 20, 14: 20, 15: 20,
    # Level 16-20: Giai đoạn Mái, 25 hàng
    16: 25, 17: 25, 18: 25, 19: 25, 20: 25,
}
