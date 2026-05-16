import pygame
import random
import sys

pygame.init()

# =====================================================================
#  CONSTANTS
# =====================================================================

# --- Kích thước lưới logic (KHÔNG thay đổi) ---
H = 15
W = 10
CELL_SIZE = 30          # ← SỬA để đổi kích thước ô (px). Giảm từ 40 xuống 30

# --- Kích thước map chơi thực tế (pixel) — GIỮ NGUYÊN ---
MAP_W = W * CELL_SIZE   # 10 * 30 = 300
MAP_H = H * CELL_SIZE   # 15 * 30 = 450

# --- Kích thước màn hình ---
# THAY ĐỔI: background trải full màn hình, không chia panel trái/phải nữa.
# Map chơi được căn giữa màn hình. UI các widget nổi lên trên background.
# ← SỬA hai giá trị này nếu muốn đổi kích thước cửa sổ
SCREEN_WIDTH  = 1000
SCREEN_HEIGHT = 600

# --- Tọa độ góc trên-trái của map chơi (căn giữa màn hình) ---
# THAY ĐỔI: map chơi nằm chính giữa màn hình cả ngang lẫn dọc.
MAP_ORIGIN_X = (SCREEN_WIDTH  - MAP_W) // 2   # = 350
MAP_ORIGIN_Y = (SCREEN_HEIGHT - MAP_H) // 2   # = 50

# --- Khoảng cách từ mép map đến các widget UI overlay ---
# ← SỬA để đẩy widget gần/xa map hơn
UI_GAP = 20

FPS = 60

# =====================================================================
#  COLORS
# =====================================================================
BLACK     = (0,   0,   0)
WHITE     = (255, 255, 255)
GRAY      = (128, 128, 128)
DARK_GRAY = (80,  80,  80)
MAP_EMPTY = (15,  15,  25)      # màu nền map nếu không có ảnh bg

# --- Màu lưới trong vùng chơi ---
GRID_COLOR     = (50, 50, 75)   # ← ĐỔI màu lưới (R,G,B)
GRID_THICKNESS = 1              # ← ĐỔI độ dày lưới (px)

# --- Màu fill bán trong suốt bên trong map chơi ---
# THÊM MỚI: map chơi phủ một lớp màu nhạt lên trên background
# ← SỬA MAP_FILL_COLOR và MAP_FILL_ALPHA để đổi màu/độ trong suốt
MAP_FILL_COLOR = (100, 140, 200)  # màu fill (R,G,B)
MAP_FILL_ALPHA = 60               # 0=trong suốt hoàn toàn, 255=đục hoàn toàn

# --- Viền tường map: đường line (không dùng rect border nữa) ---
# THAY ĐỔI: mỗi cạnh là một đường line riêng để dễ tuỳ chỉnh màu/kiểu
# ← SỬA WALL_COLOR, WALL_THICKNESS để đổi kiểu viền
WALL_COLOR     = (160, 200, 255)
WALL_THICKNESS = 2

# --- Widget UI overlay ---
WIDGET_BG_COLOR = (15, 15, 40)
WIDGET_ALPHA    = 200
WIDGET_BORDER   = (80, 80, 140)

# =====================================================================
#  DISPLAY SETUP
# =====================================================================
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris - Gach & Vua v2.1")
clock  = pygame.time.Clock()

# Font
font_large  = pygame.font.SysFont('Arial', 28, bold=True)
font_medium = pygame.font.SysFont('Arial', 22)
font_small  = pygame.font.SysFont('Arial', 16)

# =====================================================================
#  TEXTURE LOADING (GIỮ NGUYÊN logic gốc)
# =====================================================================
def load_tile(filename):
    try:
        img = pygame.image.load(f"My Tetris/assets/{filename}").convert_alpha()
        return pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
    except Exception as e:
        print(f"❌ Failed {filename}: {e}")
        surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
        surf.fill(GRAY)
        return surf

textures = {
    'B': load_tile("Gach01.png"),
    'G': load_tile("Gach02.png"),
    'R': load_tile("Gach03.png"),
    'M': load_tile("Vuamem.png"),
    'V': load_tile("Vuacung.png"),
    'S': load_tile("Gachcung.png"),
    'X': load_tile("Vuafill.png"),
}

# =====================================================================
#  BACKGROUND IMAGE
#  ↓ ĐÂY LÀ PHẦN DỄ THAY ĐỔI SAU NÀY
#  Chỉ cần sửa đường dẫn ở BG_PATH để đổi ảnh nền
# =====================================================================
BG_PATH = "My Tetris/assets/city bg.png"   # ← SỬA ĐƯỜNG DẪN ẢNH NỀN

# =====================================================================
#  ẢNH KHUNG WIDGET (SCORE CARD & NEXT BLOCK)
#  THÊM MỚI: Mỗi widget dùng một ảnh khung riêng.
#  Ảnh sẽ được blit NGUYÊN SIZE (không scale) tại tọa độ bạn chỉ định.
#  Để None nếu không dùng ảnh — widget sẽ fallback về hộp màu đặc.
# =====================================================================
SCORE_FRAME_PATH = None   # ← SỬA: vd "My Tetris/assets/score_frame.png"
NEXT_FRAME_PATH  = None   # ← SỴA: vd "My Tetris/assets/next_frame.png"
LEVEL_FRAME_PATH = None   # ← SỬA: vd "My Tetris/assets/level_frame.png"

# =====================================================================
#  ẢNH NỀN (BACKGROUND)
#  background trải full SCREEN_WIDTH x SCREEN_HEIGHT
# =====================================================================

def load_background(path, target_w, target_h):
    """
    Load ảnh nền và scale vừa khít target_w x target_h (giữ tỉ lệ, căn giữa).
    Trả về Surface hoặc None nếu load thất bại.
    """
    try:
        img    = pygame.image.load(path).convert()
        scale  = min(target_w / img.get_width(), target_h / img.get_height())
        new_w  = int(img.get_width()  * scale)
        new_h  = int(img.get_height() * scale)
        scaled = pygame.transform.scale(img, (new_w, new_h))

        surface = pygame.Surface((target_w, target_h))
        surface.fill(MAP_EMPTY)
        surface.blit(scaled, ((target_w - new_w) // 2, (target_h - new_h) // 2))

        print(f"✅ Background loaded: {path}")
        return surface
    except Exception as e:
        print(f"❌ Background failed ({path}): {e}")
        return None

# Load ảnh nền full màn hình
bg_image = load_background(BG_PATH, SCREEN_WIDTH, SCREEN_HEIGHT)

# =====================================================================
#  LOAD ẢNH KHUNG WIDGET — NGUYÊN SIZE, KHÔNG SCALE
#  THÊM MỚI: hàm riêng, chỉ load và convert, không resize.
#  Kích thước ảnh bạn chuẩn bị = kích thước khung hiển thị thực tế.
# =====================================================================
def load_image(path):
    """
    Load ảnh nguyên kích thước gốc (không scale).
    Trả về Surface hoặc None nếu load thất bại.
    Hỗ trợ ảnh có alpha (PNG trong suốt).
    """
    if path is None:
        return None
    try:
        img = pygame.image.load(path).convert_alpha()
        print(f"✅ Image loaded: {path}  size={img.get_size()}")
        return img
    except Exception as e:
        print(f"❌ Image failed ({path}): {e}")
        return None

score_frame_img = load_image(SCORE_FRAME_PATH)
next_frame_img  = load_image(NEXT_FRAME_PATH)
level_frame_img = load_image(LEVEL_FRAME_PATH)

# =====================================================================
#  BOARD STATE  (GIỮ NGUYÊN hoàn toàn từ code gốc)
# =====================================================================
board                = [[' '] * W for _ in range(H)]
mortar_placed_time   = [[0]   * W for _ in range(H)]
block_durability     = [[1]   * W for _ in range(H)]

brick_templates = [
    [['B','B','B','B']],
    [[' ','G','G'],['G','G',' ']],
    [[' ','B',' '],['B','B','B']],
    [[' ','B','B'],['B','B',' ']],
    [['B','B',' '],[' ','B','B']],
    [['B',' ',' '],['B',' ',' '],['B','B',' ']],
    [[' ',' ','B'],[' ',' ','B'],['B','B',' ']]
]

mortar_templates = [
    [['M','M','M','M']],
    [[' ','V','V'],['V','V',' ']],
    [[' ','M',' '],['M','M','M']],
    [[' ','M','M'],['M','M',' ']],
    [['M','M',' '],[' ','M','M']],
    [['M',' ',' '],['M',' ',' '],['M','M',' ']],
    [[' ',' ','M'],[' ',' ','M'],['M','M',' ']]
]

class Block:
    def __init__(self, is_brick=True):
        self.is_brick  = is_brick
        self.templates = brick_templates if is_brick else mortar_templates
        self.shape     = random.choice(self.templates)
        self.x         = W // 2 - 2
        self.y         = 0
        self.brick_type = random.choice(['B','G','R']) if is_brick else 'M'

    def rotate(self):
        rotated    = list(zip(*self.shape[::-1]))
        self.shape = [list(row) for row in rotated]

# =====================================================================
#  LOGIC FUNCTIONS  (GIỮ NGUYÊN hoàn toàn từ code gốc)
# =====================================================================
def init_board():
    for i in range(H):
        for j in range(W):
            if i == H-1 or j == 0 or j == W-1:
                board[i][j] = '#'
            else:
                board[i][j] = ' '

def can_move(block, dx, dy):
    for i, row in enumerate(block.shape):
        for j, cell in enumerate(row):
            if cell != ' ':
                tx = block.x + j + dx
                ty = block.y + i + dy
                if tx < 1 or tx >= W-1 or ty >= H-1 or ty < 0:
                    return False
                if board[ty][tx] != ' ':
                    return False
    return True

def place_block(block):
    for i, row in enumerate(block.shape):
        for j, cell in enumerate(row):
            if cell != ' ':
                x_pos = block.x + j
                y_pos = block.y + i
                if 0 <= y_pos < H and 0 <= x_pos < W:
                    current_time = pygame.time.get_ticks()
                    if not block.is_brick:
                        board[y_pos][x_pos] = 'M'
                        mortar_placed_time[y_pos][x_pos] = current_time
                    else:
                        board[y_pos][x_pos] = block.brick_type
                        if y_pos+1 < H and board[y_pos+1][x_pos] == 'M':
                            board[y_pos+1][x_pos] = 'X'
                            block_durability[y_pos+1][x_pos] = 2

def find_falling_brick_above(i, j):
    for above_i in range(i-1, -1, -1):
        if board[above_i][j] in ['B','G','R','S']:
            return above_i
    return None

def fill_random_hole(i, j):
    if board[i][j] == ' ' and random.random() < 0.6:
        board[i][j] = 'R'

def handle_mortar_flow():
    current_time = pygame.time.get_ticks()
    for i in range(H-2, 0, -1):
        for j in range(1, W-1):
            if board[i][j] == 'M' and current_time - mortar_placed_time[i][j] > 3500:
                below_i, below_j = i+1, j
                if board[below_i][below_j] == ' ':
                    brick_above = find_falling_brick_above(i, j)
                    if brick_above is not None:
                        brick_type = board[brick_above][j]
                        board[brick_above][j] = ' '
                        board[brick_above+1][j] = brick_type
                    board[below_i][below_j] = 'M'
                    mortar_placed_time[below_i][below_j] = current_time
                    board[i][j] = ' '
                    mortar_placed_time[i][j] = 0
                    fill_random_hole(i, j)
                elif board[below_i][below_j] in ['B','G','R']:
                    board[below_i][below_j] = 'X'
                    block_durability[below_i][below_j] = 2
                    board[i][j] = ' '
                elif board[below_i][below_j] == 'M':
                    board[below_i][below_j] = 'V'
                    block_durability[below_i][below_j] = 1
                    board[i][j] = ' '

def check_glue_reaction():
    for i in range(H):
        for j in range(1, W-1):
            if board[i][j] in ['B','G','R']:
                for di in [-1,0,1]:
                    for dj in [-1,0,1]:
                        ni, nj = i+di, j+dj
                        if 0 <= ni < H and 0 <= nj < W and board[ni][nj] == 'X':
                            board[i][j] = 'S'
                            block_durability[i][j] = 2
                            return

def remove_lines():
    lines_removed = 0
    i = H-2
    while i > 0:
        full_line = all(board[i][j] != ' ' and board[i][j] != '#' for j in range(1, W-1))
        if full_line:
            for j in range(1, W-1):
                if block_durability[i][j] > 1:
                    block_durability[i][j] -= 1
                    if block_durability[i][j] == 1:
                        if board[i][j] in ['S','X']:
                            board[i][j] = 'B'
                else:
                    board[i][j] = ' '
            for ii in range(i, 1, -1):
                for j in range(1, W-1):
                    board[ii][j]              = board[ii-1][j]
                    block_durability[ii][j]   = block_durability[ii-1][j]
                    mortar_placed_time[ii][j] = mortar_placed_time[ii-1][j]
            lines_removed += 1
        else:
            i -= 1
    return lines_removed

# =====================================================================
#  DRAW HELPERS
# =====================================================================

def _cell_rect(col, row):
    """
    Trả về pygame.Rect của ô (col, row) trong lưới logic,
    đã offset đúng vào vị trí map chơi trên màn hình.

    THAY ĐỔI CHÍNH: tất cả tọa độ vẽ đều cộng MAP_ORIGIN_X / MAP_ORIGIN_Y
    thay vì dùng LEFT_OFFSET cứng như code cũ.
    """
    return pygame.Rect(
        MAP_ORIGIN_X + col * CELL_SIZE,
        MAP_ORIGIN_Y + row * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE
    )

# =====================================================================
#  DRAW FUNCTIONS
# =====================================================================

def draw_background_screen():
    """
    Vẽ theo thứ tự lớp:
      1. Background full màn hình
      2. Lớp fill màu nhạt bán trong suốt bên trong map chơi
      3. Viền line 4 cạnh riêng quanh map
    """
    # 1. Background full màn hình
    if bg_image:
        screen.blit(bg_image, (0, 0))
    else:
        screen.fill(MAP_EMPTY)

    # 2. Fill màu nhạt bán trong suốt lên vùng map
    # THÊM MỚI: dùng Surface SRCALPHA để giữ background nhìn xuyên qua
    # ← Chỉnh MAP_FILL_COLOR và MAP_FILL_ALPHA ở đầu file
    map_fill = pygame.Surface((MAP_W, MAP_H), pygame.SRCALPHA)
    map_fill.fill((*MAP_FILL_COLOR, MAP_FILL_ALPHA))
    screen.blit(map_fill, (MAP_ORIGIN_X, MAP_ORIGIN_Y))

    # 3. Viền line 4 cạnh riêng (top, bottom, left, right)
    # THAY ĐỔI: dùng 4 đường line thay vì rect stroke — linh hoạt hơn
    # ← Chỉnh WALL_COLOR, WALL_THICKNESS ở đầu file
    x0, y0 = MAP_ORIGIN_X, MAP_ORIGIN_Y
    x1, y1 = MAP_ORIGIN_X + MAP_W, MAP_ORIGIN_Y + MAP_H
    pygame.draw.line(screen, WALL_COLOR, (x0, y0), (x1, y0), WALL_THICKNESS)  # top
    pygame.draw.line(screen, WALL_COLOR, (x0, y1), (x1, y1), WALL_THICKNESS)  # bottom
    pygame.draw.line(screen, WALL_COLOR, (x0, y0), (x0, y1), WALL_THICKNESS)  # left
    pygame.draw.line(screen, WALL_COLOR, (x1, y0), (x1, y1), WALL_THICKNESS)  # right


def draw_widget_frame(frame_img, frame_x, frame_y,
                      fallback_w=160, fallback_h=80, fallback_radius=10):
    """
    THÊM MỚI: Vẽ khung widget tại (frame_x, frame_y).

    Nếu frame_img không None  → blit ảnh nguyên size tại đúng tọa độ đó.
    Nếu frame_img là None     → vẽ hộp màu fallback (WIDGET_BG_COLOR + alpha).

    Tham số:
      frame_img      : Surface ảnh đã load bằng load_image(), hoặc None
      frame_x/y      : ← ĐÂY LÀ CHỖ BẠN ĐIỀU CHỈNH VỊ TRÍ KHUNG
      fallback_w/h   : kích thước hộp màu khi không có ảnh
      fallback_radius: bo góc hộp màu

    Trả về (frame_x, frame_y, actual_w, actual_h) để caller biết vùng vẽ chữ.
    """
    if frame_img is not None:
        screen.blit(frame_img, (frame_x, frame_y))
        return frame_x, frame_y, frame_img.get_width(), frame_img.get_height()
    else:
        # Fallback: hộp màu bán trong suốt
        box = pygame.Surface((fallback_w, fallback_h), pygame.SRCALPHA)
        pygame.draw.rect(box, (*WIDGET_BG_COLOR, WIDGET_ALPHA),
                         (0, 0, fallback_w, fallback_h), border_radius=fallback_radius)
        pygame.draw.rect(box, (*WIDGET_BORDER, 220),
                         (0, 0, fallback_w, fallback_h), 2, border_radius=fallback_radius)
        screen.blit(box, (frame_x, frame_y))
        return frame_x, frame_y, fallback_w, fallback_h


def draw_grid():
    """
    Vẽ lưới mờ bên trong vùng map chơi.
    Màu/độ dày chỉnh qua GRID_COLOR, GRID_THICKNESS ở đầu file.
    """
    for col in range(W + 1):
        x = MAP_ORIGIN_X + col * CELL_SIZE
        pygame.draw.line(screen, GRID_COLOR,
                         (x, MAP_ORIGIN_Y),
                         (x, MAP_ORIGIN_Y + MAP_H), GRID_THICKNESS)
    for row in range(H + 1):
        y = MAP_ORIGIN_Y + row * CELL_SIZE
        pygame.draw.line(screen, GRID_COLOR,
                         (MAP_ORIGIN_X, y),
                         (MAP_ORIGIN_X + MAP_W, y), GRID_THICKNESS)


def draw_board():
    """Vẽ các ô đã đặt trên board."""
    for i in range(H):
        for j in range(W):
            cell = board[i][j]
            rect = _cell_rect(j, i)
            if cell in textures:
                screen.blit(textures[cell], rect)
            elif cell == '#':
                pygame.draw.rect(screen, DARK_GRAY, rect)


def draw_block(block):
    """Vẽ khối đang rơi (không có viền trắng)."""
    for i, row in enumerate(block.shape):
        for j, char in enumerate(row):
            if char != ' ':
                rect      = _cell_rect(block.x + j, block.y + i)
                cell_type = block.brick_type if block.is_brick else 'M'
                if cell_type in textures:
                    screen.blit(textures[cell_type], rect)
                else:
                    pygame.draw.rect(screen, (200, 50, 50), rect)


# =====================================================================
#  LEFT SIDE UI — Level badge + Score card
# =====================================================================

# -----------------------------------------------------------------------
#  VỊ TRÍ CÁC WIDGET BÊN TRÁI — CHỈNH TẠI ĐÂY
#  Mỗi cặp (x, y) là góc trên-trái của khung ảnh / hộp màu.
#  Tọa độ chữ (text offset) tính tương đối so với góc trên-trái khung.
# -----------------------------------------------------------------------
LEVEL_FRAME_X,  LEVEL_FRAME_Y  = 16, 16        # ← vị trí khung LEVEL
LEVEL_TEXT_OX,  LEVEL_TEXT_OY  = 14, 8         # ← offset chữ trong khung LEVEL
LEVEL_FBK_W,    LEVEL_FBK_H    = 160, 38       # ← kích thước fallback (không có ảnh)

SCORE_FRAME_X,  SCORE_FRAME_Y  = None, None    # ← None = tự tính (căn trái map)
SCORE_TEXT_OX,  SCORE_TEXT_OY  = 12, 10        # ← offset dòng ★ score
SCORE_BIG_OY    = 52                           # ← offset số điểm to (từ top khung)
SCORE_FBK_W,    SCORE_FBK_H    = 140, 120      # ← kích thước fallback


def draw_left_panel(score, lines, level):
    """
    Vẽ hai widget nổi bên trái map:
      • Khung LEVEL  — góc trên-trái màn hình
      • Khung SCORE  — giữa chiều cao map, bên trái map

    ĐỂ CHỈNH VỊ TRÍ: sửa LEVEL_FRAME_X/Y và SCORE_FRAME_X/Y ở trên.
    ĐỂ CHỈNH CHỮ:    sửa các *_TEXT_OX/OY offset.
    ĐỂ CHÈN ẢNH:     gán LEVEL_FRAME_PATH / SCORE_FRAME_PATH ở đầu file.
    """

    # ------------------------------------------------------------------
    # 1. KHUNG LEVEL
    # ------------------------------------------------------------------
    fx, fy, fw, fh = draw_widget_frame(
        level_frame_img,
        LEVEL_FRAME_X, LEVEL_FRAME_Y,
        fallback_w=LEVEL_FBK_W, fallback_h=LEVEL_FBK_H, fallback_radius=19
    )
    # Chữ đè lên khung — offset tính từ góc trên-trái khung
    lv_surf = font_medium.render(f"LEVEL:  {level}", True, WHITE)
    screen.blit(lv_surf, (fx + LEVEL_TEXT_OX, fy + LEVEL_TEXT_OY))

    # ------------------------------------------------------------------
    # 2. KHUNG SCORE
    # Nếu SCORE_FRAME_X/Y là None → tự tính sát mép trái map
    # ------------------------------------------------------------------
    fbk_w = SCORE_FBK_W
    fbk_h = SCORE_FBK_H
    sx = SCORE_FRAME_X if SCORE_FRAME_X is not None \
         else MAP_ORIGIN_X - UI_GAP - fbk_w
    sy = SCORE_FRAME_Y if SCORE_FRAME_Y is not None \
         else MAP_ORIGIN_Y + (MAP_H - fbk_h) // 2

    fx, fy, fw, fh = draw_widget_frame(
        score_frame_img, sx, sy,
        fallback_w=fbk_w, fallback_h=fbk_h, fallback_radius=10
    )
    # Dòng ★ + điểm nhỏ
    star_surf = font_medium.render("★", True, (255, 210, 0))
    sc_surf   = font_medium.render(f"  {score}", True, WHITE)
    screen.blit(star_surf, (fx + SCORE_TEXT_OX, fy + SCORE_TEXT_OY))
    screen.blit(sc_surf,   (fx + SCORE_TEXT_OX + 4, fy + SCORE_TEXT_OY))

    # Đường kẻ phân cách
    sep_y = fy + SCORE_TEXT_OY + 28
    pygame.draw.line(screen, WIDGET_BORDER, (fx + 6, sep_y), (fx + fw - 6, sep_y), 1)

    # Số điểm to — căn giữa khung theo chiều ngang
    big_surf = font_large.render(str(score), True, WHITE)
    bx = fx + (fw - big_surf.get_width()) // 2
    screen.blit(big_surf, (bx, fy + SCORE_BIG_OY))


# =====================================================================
#  RIGHT SIDE UI — Nút Pause/Settings (trên-phải) + Next block (giữa-phải)
#  THAY ĐỔI HOÀN TOÀN: không còn cột panel — widget nổi riêng
# =====================================================================

def draw_right_panel(next_block):
    """
    Vẽ hai widget nổi ở bên phải map chơi (khớp layout ảnh tham khảo):
      • Nút Pause + Settings: góc trên-phải màn hình
      • Khung Next block: giữa chiều cao, bên phải map
    """
    pad = 12

    # ------------------------------------------------------------------
    # 1. NÚT PAUSE + SETTINGS — góc trên-phải màn hình
    # THAY ĐỔI: vị trí cố định, x tính từ mép phải màn hình
    # ------------------------------------------------------------------
    btn_w, btn_h = 110, 44
    btn_x = SCREEN_WIDTH - btn_w - 16
    btn_y = 16
    _draw_widget_box(btn_x, btn_y, btn_w, btn_h, radius=10)
    pause_surf   = font_large.render("II", True, WHITE)
    setting_surf = font_large.render("⚙", True, (255, 80, 80))
    screen.blit(pause_surf,   (btn_x + 14,  btn_y + 8))
    screen.blit(setting_surf, (btn_x + 62,  btn_y + 8))

    # ------------------------------------------------------------------
    # 2. KHUNG NEXT BLOCK — bên phải map, căn giữa chiều cao map
    # THAY ĐỔI: x = mép phải map + UI_GAP
    # ------------------------------------------------------------------
    next_w  = SCREEN_WIDTH - (MAP_ORIGIN_X + MAP_W) - UI_GAP * 2
    next_w  = max(next_w, 130)
    next_h  = 140
    next_x  = MAP_ORIGIN_X + MAP_W + UI_GAP
    next_y  = MAP_ORIGIN_Y + (MAP_H - next_h) // 2   # căn giữa theo chiều cao map
    _draw_widget_box(next_x, next_y, next_w, next_h, radius=10)

    # Label "NEXT"
    lbl = font_small.render("NEXT", True, (180, 180, 220))
    screen.blit(lbl, (next_x + pad, next_y + pad))

    if next_block is None:
        return

    # Vẽ khối preview căn giữa trong khung
    preview_cell = CELL_SIZE - 8
    rows  = len(next_block.shape)
    cols  = max(len(r) for r in next_block.shape)
    blk_w = cols * preview_cell
    blk_h = rows * preview_cell
    off_x = next_x + (next_w - blk_w) // 2
    off_y = next_y + pad + 24 + (next_h - pad - 24 - blk_h) // 2

    cell_type = next_block.brick_type if next_block.is_brick else 'M'
    for i, row in enumerate(next_block.shape):
        for j, char in enumerate(row):
            if char != ' ':
                r = pygame.Rect(
                    off_x + j * preview_cell,
                    off_y + i * preview_cell,
                    preview_cell - 2,
                    preview_cell - 2
                )
                if cell_type in textures:
                    t = pygame.transform.scale(
                            textures[cell_type], (preview_cell-2, preview_cell-2))
                    screen.blit(t, r)
                else:
                    pygame.draw.rect(screen, (200, 50, 50), r)


# =====================================================================
#  MAIN LOOP
# =====================================================================

def main():
    init_board()

    score      = 0
    lines_done = 0
    level      = 1
    fall_time  = 0
    fall_speed = 500

    # Spawn khối đầu tiên
    is_brick      = random.choices([True, True, True, False], weights=[1,1,1,0.33])[0]
    current_block = Block(is_brick)

    # Chuẩn bị khối tiếp theo (THÊM MỚI: next_block để hiện trong right panel)
    is_brick_next = random.choices([True, True, True, False], weights=[1,1,1,0.33])[0]
    next_block    = Block(is_brick_next)

    running = True
    while running:
        screen.fill(BLACK)
        current_time = pygame.time.get_ticks()

        # --- Logic không thay đổi ---
        handle_mortar_flow()
        check_glue_reaction()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                if event.key in (pygame.K_LEFT, pygame.K_a) and can_move(current_block, -1, 0):
                    current_block.x -= 1
                elif event.key in (pygame.K_RIGHT, pygame.K_d) and can_move(current_block, 1, 0):
                    current_block.x += 1
                elif event.key in (pygame.K_UP, pygame.K_w):
                    current_block.rotate()
                    if not can_move(current_block, 0, 0):
                        for _ in range(3):
                            current_block.rotate()
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    fall_speed = 50

        if current_time - fall_time > fall_speed:
            if can_move(current_block, 0, 1):
                current_block.y += 1
            else:
                place_block(current_block)
                removed     = remove_lines()
                lines_done += removed
                score      += removed * 100 * level
                level       = lines_done // 10 + 1   # THÊM: tăng level mỗi 10 hàng
                fall_speed  = max(100, 500 - (level - 1) * 40)  # THÊM: tăng tốc theo level

                # Dùng next_block làm current, tạo next mới
                current_block = next_block
                is_brick_next = random.choices([True, True, True, False], weights=[1,1,1,0.33])[0]
                next_block    = Block(is_brick_next)
                fall_speed    = max(100, 500 - (level - 1) * 40)

                if not can_move(current_block, 0, 0):
                    running = False

            fall_time = current_time

        # --- Vẽ ---
        draw_background_screen()   # 1. Background full màn hình + viền tường map
        draw_grid()                # 2. Lưới mờ bên trong map
        draw_board()               # 3. Các ô đã đặt
        draw_block(current_block)  # 4. Khối đang rơi
        draw_left_panel(score, lines_done, level)   # 5. Widget trái (Level badge + Score card)
        draw_right_panel(next_block)                # 6. Widget phải (Pause btn + Next block)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()