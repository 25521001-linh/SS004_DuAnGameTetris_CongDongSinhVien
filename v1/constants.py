# constants.py — Hằng số cho game Tetris Building V1

# ── Kích thước board ──────────────────────────────────────────────
BOARD_COLS = 10
BOARD_ROWS = 20
CELL_SIZE  = 32          # pixels mỗi ô

# ── Kích thước cửa sổ ─────────────────────────────────────────────
PANEL_W    = 160         # panel bên phải (Next, Score, Level)
SCREEN_W   = BOARD_COLS * CELL_SIZE + PANEL_W   # 320 + 160 = 480
SCREEN_H   = BOARD_ROWS * CELL_SIZE             # 640

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

# Màu ghost piece (bóng hướng dẫn)
GHOST_ALPHA = 60        # độ trong suốt (dùng Surface với SRCALPHA)

# ── Tốc độ rơi (giây mỗi bước/hàng) ──────────────────────────────
# fall_speed[level] → giây để rơi 1 hàng
FALL_SPEEDS = {
    1:  1.00,
    2:  0.85,
    3:  0.72,
    4:  0.60,
    5:  0.50,
    6:  0.42,
    7:  0.35,
    8:  0.28,
    9:  0.22,
    10: 0.17,
}
DEFAULT_FALL_SPEED = 0.05   # khi level > 10

SOFT_DROP_MULTIPLIER = 10   # S nhấn → rơi nhanh gấp 10

# ── Vữa (Mortar) ──────────────────────────────────────────────────
MORTAR_MELT_TIME   = 2.5    # giây trước khi vữa hóa lỏng
MORTAR_RATIO       = 0.25   # 25% khả năng spawn mortar thay vì brick

# ── Điểm số ───────────────────────────────────────────────────────
# Điểm cho từng loại ô khi clear:
#   ô gạch thường:       +1
#   ô liên kết (G+V):    +2
#   ô cứng (V+V):        +N  (N = số vữa tạo thành khối cứng, tính riêng)
SCORE_BRICK          = 1
SCORE_LINKED         = 2
SCORE_HARD_PER_UNIT  = 1    # mỗi đơn vị vữa trong khối cứng

# ── Loại ô (cell type) ────────────────────────────────────────────
CELL_EMPTY   = 'empty'
CELL_BRICK   = 'brick'       # gạch thường (HP 1)
CELL_MORTAR  = 'mortar'      # vữa (HP có thể thay đổi)
CELL_LINKED  = 'linked'      # gạch đã bị vữa phủ (HP 2)
CELL_HARD    = 'hard'        # vữa+vữa kết cứng (HP 2)

# ── Wall-kick offsets (SRS đơn giản) ──────────────────────────────
# Thử dịch chuyển khi xoay bị chặn: (dx, dy)
WALL_KICKS = [(0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0), (0, -1)]
