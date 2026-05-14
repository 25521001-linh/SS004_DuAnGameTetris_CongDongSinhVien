# main.py — Game loop chính: Tetris Building V1

import sys
import random
import pygame

from constants import (
    BOARD_COLS, BOARD_ROWS, CELL_SIZE,
    SCREEN_W, SCREEN_H, PANEL_W, FPS,
    BLACK, WHITE, GRAY, DARK_GRAY, BORDER_COL,
    PIECE_COLORS, MORTAR_SOLID_COLOR, MORTAR_LIQUID_COLOR,
    MORTAR_COAT_COLOR, CRACK_COLOR,
    FALL_SPEEDS, DEFAULT_FALL_SPEED, SOFT_DROP_MULTIPLIER,
    MORTAR_RATIO, MORTAR_MELT_TIME,
    CELL_EMPTY, CELL_BRICK, CELL_MORTAR, CELL_LINKED, CELL_HARD,
    BRICK_TYPES,
)
from pieces import Piece, BRICK_TYPES as BT, MORTAR_TYPES
from board import Board
from mortar import MortarManager

# ── Warna tambahan ────────────────────────────────────────────────
BOARD_BG      = (15, 15, 25)
PANEL_BG      = (20, 20, 35)
GRID_LINE_COL = (30, 30, 50)
GHOST_COLOR   = (60, 60, 80)
TEXT_COLOR    = (220, 220, 220)
ACCENT_COLOR  = (247, 211, 8)
DANGER_COLOR  = (239, 32, 41)

BOARD_ORIGIN_X = 0   # pixel x bắt đầu của board
BOARD_ORIGIN_Y = 0


# ── Helper: chọn piece ngẫu nhiên ─────────────────────────────────

def random_piece():
    """Trả về Piece ngẫu nhiên — 25% là Mortar (M), 75% là gạch."""
    if random.random() < MORTAR_RATIO:
        kind = 'M'
    else:
        kind = random.choice(BT)
    return Piece(kind, start_col=BOARD_COLS // 2 - 2)


# ── Màu của ô board ───────────────────────────────────────────────

def cell_color(cell, mortar_positions=None, row=None, col=None):
    """Trả về màu RGB cho ô cell."""
    if cell.is_empty():
        return None   # không vẽ

    t = cell.cell_type

    if t == CELL_BRICK:
        base = PIECE_COLORS.get(cell.kind, GRAY)
        if cell.cracked:
            # Trộn màu nứt lên
            return _blend(base, CRACK_COLOR, 0.4)
        return base

    if t == CELL_MORTAR:
        # Kiểm tra timer còn bao nhiêu → gradient màu
        if mortar_positions and (row, col) in mortar_positions:
            return MORTAR_SOLID_COLOR   # đang đếm ngược
        return MORTAR_LIQUID_COLOR      # đã hóa lỏng (hiếm, xảy ra ngay trước coat)

    if t == CELL_LINKED:
        base = PIECE_COLORS.get(cell.kind, GRAY)
        if cell.cracked:
            return _blend(base, CRACK_COLOR, 0.5)
        return _blend(base, MORTAR_COAT_COLOR, 0.35)

    if t == CELL_HARD:
        if cell.cracked:
            return _blend(MORTAR_SOLID_COLOR, CRACK_COLOR, 0.5)
        return MORTAR_SOLID_COLOR

    return GRAY


def _blend(c1, c2, t):
    """Trộn c1 và c2 theo tỉ lệ t (0=c1, 1=c2)."""
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


# ── Renderer ──────────────────────────────────────────────────────

def draw_board(surface, board, mortar_mgr):
    """Vẽ board game."""
    board_surf = pygame.Surface((BOARD_COLS * CELL_SIZE, BOARD_ROWS * CELL_SIZE))
    board_surf.fill(BOARD_BG)

    # Grid lines
    for r in range(BOARD_ROWS + 1):
        pygame.draw.line(board_surf, GRID_LINE_COL,
                         (0, r * CELL_SIZE),
                         (BOARD_COLS * CELL_SIZE, r * CELL_SIZE))
    for c in range(BOARD_COLS + 1):
        pygame.draw.line(board_surf, GRID_LINE_COL,
                         (c * CELL_SIZE, 0),
                         (c * CELL_SIZE, BOARD_ROWS * CELL_SIZE))

    mpos = mortar_mgr.get_liquid_positions()

    for r in range(BOARD_ROWS):
        for c in range(BOARD_COLS):
            cell = board.cell(r, c)
            color = cell_color(cell, mpos, r, c)
            if color:
                rect = pygame.Rect(c * CELL_SIZE + 1, r * CELL_SIZE + 1,
                                   CELL_SIZE - 2, CELL_SIZE - 2)
                pygame.draw.rect(board_surf, color, rect, border_radius=3)

                # Vết nứt — vạch chéo
                if cell.cracked:
                    x0 = c * CELL_SIZE + 4
                    y0 = r * CELL_SIZE + 4
                    x1 = (c + 1) * CELL_SIZE - 4
                    y1 = (r + 1) * CELL_SIZE - 4
                    pygame.draw.line(board_surf, CRACK_COLOR, (x0, y0), (x1, y1), 2)
                    pygame.draw.line(board_surf, CRACK_COLOR, (x1, y0), (x0, y1), 2)

                # Timer bar cho vữa
                if cell.cell_type == CELL_MORTAR:
                    t = mortar_mgr.get_timer(r, c)
                    if t is not None:
                        ratio = max(0.0, t / MORTAR_MELT_TIME)
                        bar_w = int((CELL_SIZE - 4) * ratio)
                        bar_rect = pygame.Rect(c * CELL_SIZE + 2,
                                               (r + 1) * CELL_SIZE - 5,
                                               bar_w, 3)
                        pygame.draw.rect(board_surf, MORTAR_LIQUID_COLOR, bar_rect)

    surface.blit(board_surf, (BOARD_ORIGIN_X, BOARD_ORIGIN_Y))


def draw_piece(surface, piece, board, color_override=None, alpha=255):
    """Vẽ piece đang rơi."""
    kind = piece.kind
    base_color = color_override or (
        MORTAR_SOLID_COLOR if piece.is_mortar else PIECE_COLORS.get(kind, GRAY)
    )

    for r, c in piece.get_cells():
        if r < 0:
            continue
        px = BOARD_ORIGIN_X + c * CELL_SIZE + 1
        py = BOARD_ORIGIN_Y + r * CELL_SIZE + 1
        rect = pygame.Rect(px, py, CELL_SIZE - 2, CELL_SIZE - 2)
        pygame.draw.rect(surface, base_color, rect, border_radius=3)


def draw_ghost(surface, piece, board):
    """Vẽ ghost piece (bóng mờ ở vị trí thấp nhất)."""
    ghost_row = board.ghost_row(piece)
    dr = ghost_row - piece.row

    for r, c in piece.get_cells():
        gr = r + dr
        if gr < 0 or gr >= BOARD_ROWS:
            continue
        px = BOARD_ORIGIN_X + c * CELL_SIZE + 1
        py = BOARD_ORIGIN_Y + gr * CELL_SIZE + 1
        rect = pygame.Rect(px, py, CELL_SIZE - 2, CELL_SIZE - 2)
        pygame.draw.rect(surface, GHOST_COLOR, rect, border_radius=3)
        pygame.draw.rect(surface, GRAY, rect, 1, border_radius=3)


def draw_panel(surface, font_large, font_small, score, level, next_piece, lines_cleared):
    """Vẽ panel bên phải."""
    px = BOARD_COLS * CELL_SIZE
    panel_rect = pygame.Rect(px, 0, PANEL_W, SCREEN_H)
    pygame.draw.rect(surface, PANEL_BG, panel_rect)
    pygame.draw.line(surface, BORDER_COL, (px, 0), (px, SCREEN_H), 2)

    margin = 12

    # ─ Score
    _label(surface, font_small, "SCORE", px + margin, 20, GRAY)
    _label(surface, font_large, str(score), px + margin, 40, ACCENT_COLOR)

    # ─ Level
    _label(surface, font_small, "LEVEL", px + margin, 90, GRAY)
    _label(surface, font_large, str(level), px + margin, 110, WHITE)

    # ─ Lines
    _label(surface, font_small, "LINES", px + margin, 160, GRAY)
    _label(surface, font_large, str(lines_cleared), px + margin, 180, WHITE)

    # ─ Next piece
    _label(surface, font_small, "NEXT", px + margin, 240, GRAY)
    _draw_mini_piece(surface, next_piece, px + margin, 265)

    # ─ Controls hint
    hints = [
        "← → : Move",
        "W/↑  : Rotate",
        "S/↓  : Soft Drop",
        "SPC  : Hard Drop",
        "ESC  : Pause",
    ]
    y = SCREEN_H - len(hints) * 18 - 10
    for h in hints:
        _label(surface, font_small, h, px + margin, y, GRAY)
        y += 18


def _label(surface, font, text, x, y, color):
    surf = font.render(text, True, color)
    surface.blit(surf, (x, y))


def _draw_mini_piece(surface, piece, ox, oy):
    """Vẽ piece thu nhỏ trong panel."""
    mini = 22
    kind = piece.kind
    base_color = MORTAR_SOLID_COLOR if piece.is_mortar else PIECE_COLORS.get(kind, GRAY)
    for r, c in piece.get_cells():
        rect = pygame.Rect(ox + c * mini, oy + r * mini, mini - 2, mini - 2)
        pygame.draw.rect(surface, base_color, rect, border_radius=2)


def draw_danger(surface, board):
    """Nhấp nháy cảnh báo khi gạch gần đỉnh."""
    danger_threshold = 4  # hàng từ đỉnh
    for r in range(danger_threshold):
        if any(board.grid[r][c].is_solid() for c in range(BOARD_COLS)):
            alpha = 80 + int(60 * abs(pygame.time.get_ticks() % 1000 / 500 - 1))
            warn = pygame.Surface((BOARD_COLS * CELL_SIZE, CELL_SIZE * danger_threshold),
                                  pygame.SRCALPHA)
            warn.fill((239, 32, 41, alpha))
            surface.blit(warn, (BOARD_ORIGIN_X, BOARD_ORIGIN_Y))
            break


# ── Pause screen ──────────────────────────────────────────────────

def draw_pause(surface, font_large):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))
    text = font_large.render("PAUSED", True, WHITE)
    surface.blit(text, text.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2)))


def draw_game_over(surface, font_large, font_small, score):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    t1 = font_large.render("GAME OVER", True, DANGER_COLOR)
    t2 = font_small.render(f"Score: {score}", True, WHITE)
    t3 = font_small.render("Press R to restart", True, GRAY)
    cx, cy = SCREEN_W // 2, SCREEN_H // 2
    surface.blit(t1, t1.get_rect(center=(cx, cy - 40)))
    surface.blit(t2, t2.get_rect(center=(cx, cy + 10)))
    surface.blit(t3, t3.get_rect(center=(cx, cy + 40)))


# ── Game state ────────────────────────────────────────────────────

class GameState:
    def __init__(self):
        self.board        = Board()
        self.mortar_mgr   = MortarManager()
        self.current      = random_piece()
        self.next         = random_piece()
        self.score        = 0
        self.level        = 1
        self.lines_total  = 0
        self.fall_timer   = 0.0   # giây đã trôi qua từ lần rơi cuối
        self.paused       = False
        self.game_over    = False
        self.lock_delay   = 0.0   # thời gian chờ lock sau khi chạm đất
        self.lock_delay_max = 0.5

    def fall_speed(self):
        return FALL_SPEEDS.get(self.level, DEFAULT_FALL_SPEED)

    def _spawn_next(self):
        self.current = self.next
        self.next    = random_piece()
        self.fall_timer = 0.0
        self.lock_delay = 0.0
        if not self.board.can_place(self.current):
            self.game_over = True

    def _lock_current(self):
        """Đặt piece xuống board, xử lý vữa, xóa dòng."""
        self.board.lock_piece(self.current)
        # Đăng ký ô vữa
        if self.current.is_mortar:
            self.mortar_mgr.register_piece(self.current)
        # Xóa dòng
        gained = self.board.clear_lines()
        self.score += gained
        # Tính lines cleared (ước lượng từ điểm — đơn giản hóa cho V1)
        self._update_level()
        self._spawn_next()

    def _update_level(self):
        # Level up mỗi 10 dòng (tính xấp xỉ qua score)
        self.level = max(1, self.score // 10 + 1)

    # ── Input ─────────────────────────────────────────────────────

    def move(self, dc):
        if self.board.can_place(self.current, 0, dc):
            self.current.col += dc
            self.lock_delay = 0.0   # reset lock delay khi di chuyển

    def rotate(self):
        ok, dc, dr = self.board.can_rotate(self.current)
        if ok:
            self.current.apply_rotation()
            self.current.col += dc
            self.current.row += dr
            self.lock_delay = 0.0

    def soft_drop(self):
        if self.board.can_place(self.current, 1, 0):
            self.current.row += 1
            self.fall_timer = 0.0
            self.score += 1   # soft drop bonus
        # Nếu không thể → lock ngay
        else:
            self._lock_current()

    def hard_drop(self):
        dr = 0
        while self.board.can_place(self.current, dr + 1, 0):
            dr += 1
        self.score += dr * 2   # hard drop bonus
        self.current.row += dr
        self._lock_current()

    # ── Update ────────────────────────────────────────────────────

    def update(self, dt):
        if self.paused or self.game_over:
            return

        # Cập nhật vữa
        self.mortar_mgr.update(dt, self.board)

        # Fall timer
        self.fall_timer += dt
        speed = self.fall_speed()

        if self.fall_timer >= speed:
            self.fall_timer -= speed
            if self.board.can_place(self.current, 1, 0):
                self.current.row += 1
                self.lock_delay = 0.0
            else:
                # Chạm đất → bắt đầu lock delay
                self.lock_delay += dt
                if self.lock_delay >= self.lock_delay_max:
                    self._lock_current()


# ── Main ──────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Tetris Building — V1")
    clock  = pygame.time.Clock()

    try:
        font_large = pygame.font.SysFont("consolas", 26, bold=True)
        font_small = pygame.font.SysFont("consolas", 14)
    except Exception:
        font_large = pygame.font.Font(None, 30)
        font_small = pygame.font.Font(None, 18)

    state = GameState()

    # DAS (Delayed Auto Shift) — giữ phím trái/phải
    das_key      = None
    das_timer    = 0.0
    das_delay    = 0.17   # giây trước khi ARR bắt đầu
    das_arr      = 0.05   # giây mỗi lần lặp

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0   # giây

        # ── Events ────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                k = event.key

                if state.game_over:
                    if k == pygame.K_r:
                        state = GameState()
                    continue

                if k == pygame.K_ESCAPE:
                    state.paused = not state.paused

                if state.paused:
                    continue

                # Xoay
                if k in (pygame.K_w, pygame.K_UP):
                    state.rotate()

                # Hard drop
                if k == pygame.K_SPACE:
                    state.hard_drop()

                # Soft drop
                if k in (pygame.K_s, pygame.K_DOWN):
                    state.soft_drop()

                # Di chuyển (khởi động DAS)
                if k in (pygame.K_a, pygame.K_LEFT):
                    state.move(-1)
                    das_key   = -1
                    das_timer = 0.0
                if k in (pygame.K_d, pygame.K_RIGHT):
                    state.move(1)
                    das_key   = 1
                    das_timer = 0.0

            elif event.type == pygame.KEYUP:
                k = event.key
                if k in (pygame.K_a, pygame.K_LEFT) and das_key == -1:
                    das_key = None
                if k in (pygame.K_d, pygame.K_RIGHT) and das_key == 1:
                    das_key = None

        # ── DAS logic ─────────────────────────────────────────────
        if das_key and not state.paused and not state.game_over:
            das_timer += dt
            if das_timer >= das_delay:
                arr_timer = das_timer - das_delay
                steps = int(arr_timer / das_arr)
                for _ in range(steps):
                    state.move(das_key)
                das_timer = das_delay + (arr_timer % das_arr)

        # ── Update logic ──────────────────────────────────────────
        state.update(dt)

        # ── Render ────────────────────────────────────────────────
        screen.fill(BLACK)

        draw_board(screen, state.board, state.mortar_mgr)

        if not state.game_over:
            draw_ghost(screen, state.current, state.board)
            draw_piece(screen, state.current, state.board)

        draw_danger(screen, state.board)

        draw_panel(screen, font_large, font_small,
                   state.score, state.level, state.next, state.lines_total)

        if state.paused:
            draw_pause(screen, font_large)

        if state.game_over:
            draw_game_over(screen, font_large, font_small, state.score)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
