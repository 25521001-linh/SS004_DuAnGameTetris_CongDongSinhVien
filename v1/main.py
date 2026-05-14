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
    FALL_SPEEDS, DEFAULT_FALL_SPEED, LOCK_DELAY,
    MORTAR_MELT_TIME,
    CELL_EMPTY, CELL_BRICK, CELL_MORTAR, CELL_LINKED, CELL_HARD,
    MORTAR_RATIO, LINES_PER_LEVEL,
)
from pieces import Piece, BRICK_TYPES
from board import Board
from mortar import MortarManager

# ── Màu phụ trợ ──────────────────────────────────────────────────
BOARD_BG      = (15, 15, 25)
PANEL_BG      = (20, 20, 35)
GRID_LINE_COL = (30, 30, 50)
GHOST_COLOR   = (60, 60, 80)
TEXT_COL      = (220, 220, 220)
ACCENT_COL    = (247, 211, 8)
DANGER_COL    = (239, 32, 41)


def random_piece():
    if random.random() < MORTAR_RATIO:
        kind = 'M'
    else:
        kind = random.choice(BRICK_TYPES)
    return Piece(kind, start_col=BOARD_COLS // 2 - 2)


def _blend(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def cell_color(cell, mortar_positions, r, c):
    if cell.is_empty():
        return None
    t = cell.cell_type
    if t == CELL_BRICK:
        base = PIECE_COLORS.get(cell.kind, GRAY)
        return _blend(base, CRACK_COLOR, 0.4) if cell.cracked else base
    if t == CELL_MORTAR:
        return MORTAR_SOLID_COLOR if (r, c) in mortar_positions else MORTAR_LIQUID_COLOR
    if t == CELL_LINKED:
        base = PIECE_COLORS.get(cell.kind, GRAY)
        if cell.cracked:
            return _blend(base, CRACK_COLOR, 0.5)
        return _blend(base, MORTAR_COAT_COLOR, 0.35)
    if t == CELL_HARD:
        return _blend(MORTAR_SOLID_COLOR, CRACK_COLOR, 0.5) if cell.cracked else MORTAR_SOLID_COLOR
    return GRAY


# ── Rendering ─────────────────────────────────────────────────────

def draw_board(surf, board, mortar_mgr):
    bs = pygame.Surface((BOARD_COLS * CELL_SIZE, BOARD_ROWS * CELL_SIZE))
    bs.fill(BOARD_BG)
    for r in range(BOARD_ROWS + 1):
        pygame.draw.line(bs, GRID_LINE_COL, (0, r * CELL_SIZE), (BOARD_COLS * CELL_SIZE, r * CELL_SIZE))
    for c in range(BOARD_COLS + 1):
        pygame.draw.line(bs, GRID_LINE_COL, (c * CELL_SIZE, 0), (c * CELL_SIZE, BOARD_ROWS * CELL_SIZE))

    mpos = mortar_mgr.get_active_positions()
    for r in range(BOARD_ROWS):
        for c in range(BOARD_COLS):
            cell = board.cell(r, c)
            color = cell_color(cell, mpos, r, c)
            if color:
                rect = pygame.Rect(c * CELL_SIZE + 1, r * CELL_SIZE + 1, CELL_SIZE - 2, CELL_SIZE - 2)
                pygame.draw.rect(bs, color, rect, border_radius=3)
                if cell.cracked:
                    x0, y0 = c * CELL_SIZE + 5, r * CELL_SIZE + 5
                    x1, y1 = (c + 1) * CELL_SIZE - 5, (r + 1) * CELL_SIZE - 5
                    pygame.draw.line(bs, CRACK_COLOR, (x0, y0), (x1, y1), 2)
                    pygame.draw.line(bs, CRACK_COLOR, (x1, y0), (x0, y1), 2)
                if cell.cell_type == CELL_MORTAR:
                    t = mortar_mgr.get_timer(r, c)
                    if t is not None:
                        ratio = max(0.0, t / MORTAR_MELT_TIME)
                        bw = int((CELL_SIZE - 4) * ratio)
                        pygame.draw.rect(bs, MORTAR_LIQUID_COLOR,
                                         (c * CELL_SIZE + 2, (r + 1) * CELL_SIZE - 5, bw, 3))
    surf.blit(bs, (0, 0))


def draw_piece(surf, piece):
    color = MORTAR_SOLID_COLOR if piece.is_mortar else PIECE_COLORS.get(piece.kind, GRAY)
    for r, c in piece.get_cells():
        if r < 0:
            continue
        rect = pygame.Rect(c * CELL_SIZE + 1, r * CELL_SIZE + 1, CELL_SIZE - 2, CELL_SIZE - 2)
        pygame.draw.rect(surf, color, rect, border_radius=3)


def draw_ghost(surf, piece, board):
    gr = board.ghost_row(piece)
    dr = gr - piece.row
    for r, c in piece.get_cells():
        nr = r + dr
        if nr < 0 or nr >= BOARD_ROWS:
            continue
        rect = pygame.Rect(c * CELL_SIZE + 1, nr * CELL_SIZE + 1, CELL_SIZE - 2, CELL_SIZE - 2)
        pygame.draw.rect(surf, GHOST_COLOR, rect, border_radius=3)
        pygame.draw.rect(surf, GRAY, rect, 1, border_radius=3)


def draw_panel(surf, fl, fs, score, level, lines, next_p, phase):
    px = BOARD_COLS * CELL_SIZE
    pygame.draw.rect(surf, PANEL_BG, (px, 0, PANEL_W, SCREEN_H))
    pygame.draw.line(surf, BORDER_COL, (px, 0), (px, SCREEN_H), 2)
    m = 12

    _txt(surf, fs, "SCORE", px + m, 20, GRAY)
    _txt(surf, fl, str(score), px + m, 40, ACCENT_COL)
    _txt(surf, fs, "LEVEL", px + m, 90, GRAY)
    _txt(surf, fl, str(level), px + m, 110, WHITE)
    _txt(surf, fs, "LINES", px + m, 155, GRAY)
    _txt(surf, fl, str(lines), px + m, 175, WHITE)
    _txt(surf, fs, f"Phase: {phase}", px + m, 215, ACCENT_COL)
    _txt(surf, fs, "NEXT", px + m, 255, GRAY)
    _mini(surf, next_p, px + m, 278)

    hints = ["A/← : Left", "D/→ : Right", "W/↑ : Rotate",
             "S/↓ : Soft Drop", "SPC : Hard Drop", "ESC : Pause"]
    y = SCREEN_H - len(hints) * 18 - 10
    for h in hints:
        _txt(surf, fs, h, px + m, y, GRAY)
        y += 18


def _txt(surf, font, text, x, y, col):
    surf.blit(font.render(text, True, col), (x, y))


def _mini(surf, piece, ox, oy):
    sz = 20
    color = MORTAR_SOLID_COLOR if piece.is_mortar else PIECE_COLORS.get(piece.kind, GRAY)
    for r, c in piece.get_cells():
        pygame.draw.rect(surf, color, (ox + c * sz, oy + r * sz, sz - 2, sz - 2), border_radius=2)


def draw_danger(surf, board):
    for r in range(4):
        if any(board.grid[r][c].is_solid() for c in range(BOARD_COLS)):
            alpha = 80 + int(60 * abs(pygame.time.get_ticks() % 1000 / 500 - 1))
            w = pygame.Surface((BOARD_COLS * CELL_SIZE, CELL_SIZE * 4), pygame.SRCALPHA)
            w.fill((239, 32, 41, alpha))
            surf.blit(w, (0, 0))
            break


def draw_pause(surf, fl):
    ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 160))
    surf.blit(ov, (0, 0))
    t = fl.render("PAUSED", True, WHITE)
    surf.blit(t, t.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2)))


def draw_game_over(surf, fl, fs, score):
    ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 180))
    surf.blit(ov, (0, 0))
    cx, cy = SCREEN_W // 2, SCREEN_H // 2
    for txt, font, col, dy in [
        ("GAME OVER", fl, DANGER_COL, -40),
        (f"Score: {score}", fs, WHITE, 10),
        ("Press R to restart", fs, GRAY, 40),
    ]:
        t = font.render(txt, True, col)
        surf.blit(t, t.get_rect(center=(cx, cy + dy)))


# ── Game State ────────────────────────────────────────────────────

class GameState:
    def __init__(self):
        self.board       = Board()
        self.mortar_mgr  = MortarManager()
        self.current     = random_piece()
        self.next        = random_piece()
        self.score       = 0
        self.level       = 1
        self.lines_total = 0
        self.lines_level = 0      # dòng cleared trong level hiện tại
        self.fall_timer  = 0.0
        self.lock_timer  = 0.0
        self.paused      = False
        self.game_over   = False

    def fall_speed(self):
        return FALL_SPEEDS.get(self.level, DEFAULT_FALL_SPEED)

    @property
    def phase(self):
        if self.level <= 5:
            return "Móng"
        elif self.level <= 15:
            return "Tường"
        else:
            return "Mái"

    def _spawn_next(self):
        self.current = self.next
        self.next = random_piece()
        self.fall_timer = 0.0
        self.lock_timer = 0.0
        if not self.board.can_place(self.current):
            self.game_over = True

    def _lock_current(self):
        self.board.lock_piece(self.current)
        if self.current.is_mortar:
            self.mortar_mgr.register_piece(self.current)

        gained, lines = self.board.clear_lines_with_combo()
        self.score += gained
        self.lines_total += lines
        self.lines_level += lines
        self._check_level_up()
        self._spawn_next()

    def _check_level_up(self):
        needed = LINES_PER_LEVEL.get(self.level, 25)
        while self.lines_level >= needed and self.level < 20:
            self.lines_level -= needed
            self.level += 1
            needed = LINES_PER_LEVEL.get(self.level, 25)

    # ── Input ─────────────────────────────────────────────────────

    def move(self, dc):
        if self.board.can_place(self.current, 0, dc):
            self.current.col += dc
            self.lock_timer = 0.0

    def rotate(self):
        ok, nm, nr, dc, dr = self.board.try_rotate(self.current)
        if ok:
            self.current.apply_rotation(nm, nr)
            self.current.col += dc
            self.current.row += dr
            self.lock_timer = 0.0

    def soft_drop(self):
        if self.board.can_place(self.current, 1, 0):
            self.current.row += 1
            self.fall_timer = 0.0
            self.score += 1
        else:
            self._lock_current()

    def hard_drop(self):
        dr = 0
        while self.board.can_place(self.current, dr + 1, 0):
            dr += 1
        self.score += dr * 2
        self.current.row += dr
        self._lock_current()

    # ── Update ────────────────────────────────────────────────────

    def update(self, dt):
        if self.paused or self.game_over:
            return

        self.mortar_mgr.update(dt, self.board)

        self.fall_timer += dt
        speed = self.fall_speed()

        if self.fall_timer >= speed:
            self.fall_timer -= speed
            if self.board.can_place(self.current, 1, 0):
                self.current.row += 1
                self.lock_timer = 0.0
            else:
                self.lock_timer += speed

        # Lock delay
        if not self.board.can_place(self.current, 1, 0):
            self.lock_timer += dt
            if self.lock_timer >= LOCK_DELAY:
                self._lock_current()


# ── Main loop ─────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Tetris Building — V1")
    clock = pygame.time.Clock()

    try:
        fl = pygame.font.SysFont("consolas", 24, bold=True)
        fs = pygame.font.SysFont("consolas", 13)
    except Exception:
        fl = pygame.font.Font(None, 28)
        fs = pygame.font.Font(None, 16)

    state = GameState()

    das_key = None
    das_timer = 0.0
    DAS_DELAY = 0.17
    DAS_ARR   = 0.05

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

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
                if k in (pygame.K_w, pygame.K_UP):
                    state.rotate()
                if k == pygame.K_SPACE:
                    state.hard_drop()
                if k in (pygame.K_s, pygame.K_DOWN):
                    state.soft_drop()
                if k in (pygame.K_a, pygame.K_LEFT):
                    state.move(-1); das_key = -1; das_timer = 0.0
                if k in (pygame.K_d, pygame.K_RIGHT):
                    state.move(1); das_key = 1; das_timer = 0.0

            elif event.type == pygame.KEYUP:
                k = event.key
                if k in (pygame.K_a, pygame.K_LEFT) and das_key == -1:
                    das_key = None
                if k in (pygame.K_d, pygame.K_RIGHT) and das_key == 1:
                    das_key = None

        if das_key and not state.paused and not state.game_over:
            das_timer += dt
            if das_timer >= DAS_DELAY:
                arr_t = das_timer - DAS_DELAY
                for _ in range(int(arr_t / DAS_ARR)):
                    state.move(das_key)
                das_timer = DAS_DELAY + (arr_t % DAS_ARR)

        state.update(dt)

        screen.fill(BLACK)
        draw_board(screen, state.board, state.mortar_mgr)
        if not state.game_over:
            draw_ghost(screen, state.current, state.board)
            draw_piece(screen, state.current)
        draw_danger(screen, state.board)
        draw_panel(screen, fl, fs, state.score, state.level,
                   state.lines_total, state.next, state.phase)
        if state.paused:
            draw_pause(screen, fl)
        if state.game_over:
            draw_game_over(screen, fl, fs, state.score)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
