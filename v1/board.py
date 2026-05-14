# board.py — Board state, va chạm, xóa dòng 2-lần, trọng lực combo
#
# Quy tắc GDD:
# - Gạch thường (BRICK, hp=1): 1 lần clear → +1 điểm/ô
# - Khối liên kết (LINKED = Gạch+Vữa, hp=2):
#     Lần 1 clear: vữa biến mất, gạch nứt (cracked) → hp giảm về 1
#     Lần 2 clear: gạch vỡ hoàn toàn → +2 điểm/ô
# - Khối cứng (HARD = Vữa+Vữa, hp=2):
#     Lần 1 clear: nứt → hp giảm về 1
#     Lần 2 clear: vỡ → +N điểm (N = số vữa tạo thành)
# - Trọng lực: sau clear, khối trên rơi xuống lấp trống → kiểm tra combo
# - Combo: nhịp 1 x1, nhịp 2 x2, nhịp 3 x4, ...

from constants import (
    BOARD_COLS, BOARD_ROWS,
    CELL_EMPTY, CELL_BRICK, CELL_MORTAR, CELL_LINKED, CELL_HARD,
    SCORE_BRICK, SCORE_LINKED_PER_CELL, SCORE_HARD_PER_UNIT,
    COMBO_BASE_MULTIPLIER, WALL_KICKS,
)


class Cell:
    """Một ô trên board."""
    __slots__ = ('cell_type', 'kind', 'hp', 'cracked', 'mortar_units')

    def __init__(self):
        self.clear()

    def clear(self):
        self.cell_type   = CELL_EMPTY
        self.kind        = None
        self.hp          = 0
        self.cracked     = False
        self.mortar_units = 0

    def is_empty(self):
        return self.cell_type == CELL_EMPTY

    def is_solid(self):
        return self.cell_type != CELL_EMPTY

    def set_brick(self, kind):
        self.cell_type    = CELL_BRICK
        self.kind         = kind
        self.hp           = 1
        self.cracked      = False
        self.mortar_units = 0

    def set_mortar(self):
        self.cell_type    = CELL_MORTAR
        self.kind         = 'M'
        self.hp           = 1
        self.cracked      = False
        self.mortar_units = 1

    def make_linked(self):
        """Gạch + Vữa → LINKED (hp=2).
        Gọi trên ô BRICK khi vữa chảy xuống phủ lên."""
        old_kind = self.kind
        self.cell_type    = CELL_LINKED
        self.kind         = old_kind  # giữ loại gạch gốc để hiển thị màu
        self.hp           = 2
        self.cracked      = False
        self.mortar_units = 1

    def make_hard(self, extra_units=1):
        """Vữa + Vữa → HARD (hp=2).
        Gọi trên ô MORTAR/HARD khi vữa chảy xuống chồng lên."""
        self.mortar_units += extra_units
        self.cell_type    = CELL_HARD
        self.kind         = 'M'
        self.hp           = 2
        self.cracked      = False

    def copy_from(self, other):
        self.cell_type    = other.cell_type
        self.kind         = other.kind
        self.hp           = other.hp
        self.cracked      = other.cracked
        self.mortar_units = other.mortar_units


class Board:
    """Board 10×20. grid[row][col], row 0 = đỉnh."""

    def __init__(self):
        self.cols = BOARD_COLS
        self.rows = BOARD_ROWS
        self.grid = [[Cell() for _ in range(self.cols)] for _ in range(self.rows)]

    def cell(self, r, c):
        return self.grid[r][c]

    def in_bounds(self, r, c):
        return 0 <= c < self.cols and r < self.rows

    def is_empty(self, r, c):
        if not self.in_bounds(r, c):
            return False
        if r < 0:
            return True  # trên đỉnh board = OK khi spawn
        return self.grid[r][c].is_empty()

    # ── Va chạm ───────────────────────────────────────────────────

    def can_place(self, piece, dr=0, dc=0):
        """Kiểm tra piece (dịch thêm dr hàng, dc cột) có hợp lệ."""
        for r, c in piece.get_cells():
            nr, nc = r + dr, c + dc
            if nc < 0 or nc >= self.cols or nr >= self.rows:
                return False
            if nr >= 0 and self.grid[nr][nc].is_solid():
                return False
        return True

    def try_rotate(self, piece):
        """Thử xoay CW với wall-kick.
        Trả về (success, new_matrix, new_rot, kick_dc, kick_dr)."""
        new_matrix, new_rot = piece.rotated_matrix()
        old_m, old_r = piece.matrix, piece.rotation
        piece.matrix, piece.rotation = new_matrix, new_rot

        for dc, dr in WALL_KICKS:
            if self.can_place(piece, dr, dc):
                piece.matrix, piece.rotation = old_m, old_r
                return True, new_matrix, new_rot, dc, dr

        piece.matrix, piece.rotation = old_m, old_r
        return False, None, None, 0, 0

    # ── Lock piece ────────────────────────────────────────────────

    def lock_piece(self, piece):
        """Đặt piece cố định vào board.
        Nếu vữa, kiểm tra ngay chồng vữa → HARD."""
        for r, c in piece.get_cells():
            if 0 <= r < self.rows and 0 <= c < self.cols:
                cell = self.grid[r][c]
                if piece.is_mortar:
                    cell.set_mortar()
                else:
                    cell.set_brick(piece.kind)

        # GDD: Vữa chồng lên vữa → tự động kết cứng ngay khi lock
        if piece.is_mortar:
            self._check_mortar_stack_on_lock(piece)

    def _check_mortar_stack_on_lock(self, piece):
        """Khi vừa lock piece vữa, kiểm tra xem có ô nào của piece
        nằm ngay trên một ô MORTAR/HARD khác → tạo HARD ngay."""
        for r, c in piece.get_cells():
            if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
                continue
            # Kiểm tra ô ngay bên dưới
            below_r = r + 1
            if below_r < self.rows:
                below = self.grid[below_r][c]
                me = self.grid[r][c]
                if me.cell_type == CELL_MORTAR and below.cell_type in (CELL_MORTAR, CELL_HARD):
                    units = me.mortar_units
                    below.make_hard(units)
                    me.clear()

    # ── Vữa hóa lỏng: chảy xuống khối đầu tiên bên dưới ─────────

    def apply_mortar_coat(self, mortar_r, mortar_c):
        """Khi vữa tại (mortar_r, mortar_c) hóa lỏng:
        - Chảy xuống khối đầu tiên nó chạm vào (GDD: không tuột xuống đáy)
        - Gạch bên dưới → LINKED
        - Vữa/Hard bên dưới → HARD (gộp units)
        - Ô trống bên dưới → vữa rơi xuống 1 ô
        Trả về True nếu thành công."""
        if not (0 <= mortar_r < self.rows and 0 <= mortar_c < self.cols):
            return False
        me = self.grid[mortar_r][mortar_c]
        if me.cell_type != CELL_MORTAR:
            return False

        # Tìm ô ngay bên dưới (chỉ 1 ô — GDD: khối đầu tiên chạm vào)
        target_r = mortar_r + 1
        if target_r >= self.rows:
            return False  # đáy map, vữa giữ nguyên

        target = self.grid[target_r][mortar_c]
        units = me.mortar_units

        if target.is_empty():
            # Ô trống → vữa rơi xuống 1 ô (GDD: chảy xuống khối đầu tiên)
            target.set_mortar()
            target.mortar_units = units
            me.clear()
            return True

        if target.cell_type == CELL_BRICK:
            # Gạch + Vữa → LINKED
            target.make_linked()
            me.clear()
            return True

        if target.cell_type in (CELL_MORTAR, CELL_HARD):
            # Vữa + Vữa/Hard → HARD
            target.make_hard(units)
            me.clear()
            return True

        if target.cell_type == CELL_LINKED:
            # Vữa chảy lên khối đã liên kết → gộp thêm mortar_units
            target.mortar_units += units
            me.clear()
            return True

        return False

    # ── Xóa dòng + trọng lực combo ───────────────────────────────

    def clear_lines_with_combo(self):
        """Xóa dòng theo quy tắc GDD, bao gồm trọng lực + combo.

        Trả về: (total_score, total_lines_cleared)

        Logic:
        1. Quét tìm dòng đầy
        2. Xử lý từng dòng: ô hp=1 → xóa; ô hp=2 → crack (hp→1), không xóa
        3. Nếu toàn bộ ô trong dòng đều bị xóa → remove_row + gravity
        4. Sau gravity → quét lại (combo loop)
        5. Hệ số combo nhân đôi mỗi nhịp: x1, x2, x4, x8...
        """
        total_score = 0
        total_lines = 0
        combo_multiplier = COMBO_BASE_MULTIPLIER

        while True:
            # Tìm tất cả dòng đầy
            full_rows = [r for r in range(self.rows) if self._is_full_line(r)]
            if not full_rows:
                break  # không còn dòng đầy → kết thúc

            round_score = 0
            rows_removed = []

            for row in sorted(full_rows, reverse=True):
                line_score, fully_cleared = self._process_full_line(row)
                round_score += line_score
                if fully_cleared:
                    rows_removed.append(row)

            # Xóa các hàng đã cleared hoàn toàn (từ dưới lên)
            for row in sorted(rows_removed, reverse=True):
                self._remove_row(row)
                total_lines += 1

            # Áp dụng combo multiplier
            total_score += round_score * combo_multiplier
            combo_multiplier *= 2  # GDD: nhân đôi mỗi nhịp

            if not rows_removed:
                break  # không xóa được hàng nào hoàn toàn → kết thúc

            # GDD: Trọng lực — khối trên rơi xuống lấp trống
            # _remove_row đã dịch xuống, nên loop lại kiểm tra combo

        return total_score, total_lines

    def _is_full_line(self, row):
        return all(self.grid[row][c].is_solid() for c in range(self.cols))

    def _process_full_line(self, row):
        """Xử lý 1 dòng đầy. Trả về (score, fully_cleared).

        - Ô BRICK (hp=1, not cracked): xóa → +1 điểm
        - Ô MORTAR (hp=1): xóa → +mortar_units điểm
        - Ô LINKED (hp=2, not cracked): crack → hp=1, cracked=True, KHÔNG xóa
        - Ô LINKED (hp=1, cracked): xóa → +2 điểm
        - Ô HARD (hp=2, not cracked): crack → hp=1, cracked=True, KHÔNG xóa
        - Ô HARD (hp=1, cracked): xóa → +N điểm
        """
        score = 0
        all_cleared = True

        for c in range(self.cols):
            cell = self.grid[row][c]

            if cell.cell_type == CELL_BRICK:
                score += SCORE_BRICK
                # Sẽ bị xóa khi remove_row

            elif cell.cell_type == CELL_MORTAR:
                score += SCORE_HARD_PER_UNIT * cell.mortar_units
                # Sẽ bị xóa

            elif cell.cell_type == CELL_LINKED:
                if cell.hp == 2 and not cell.cracked:
                    # Lần 1: vữa biến mất, gạch nứt
                    cell.hp = 1
                    cell.cracked = True
                    all_cleared = False  # ô này không bị xóa
                elif cell.hp == 1 and cell.cracked:
                    # Lần 2: gạch vỡ hoàn toàn
                    score += SCORE_LINKED_PER_CELL
                else:
                    # hp=1 nhưng chưa cracked (edge case)
                    score += SCORE_LINKED_PER_CELL

            elif cell.cell_type == CELL_HARD:
                if cell.hp == 2 and not cell.cracked:
                    # Lần 1: nứt
                    cell.hp = 1
                    cell.cracked = True
                    all_cleared = False
                elif cell.hp == 1 and cell.cracked:
                    # Lần 2: vỡ
                    score += SCORE_HARD_PER_UNIT * cell.mortar_units
                else:
                    score += SCORE_HARD_PER_UNIT * cell.mortar_units

        return score, all_cleared

    def _remove_row(self, remove_row):
        """Xóa hàng, dịch tất cả hàng trên xuống 1."""
        for r in range(remove_row, 0, -1):
            for c in range(self.cols):
                self.grid[r][c].copy_from(self.grid[r - 1][c])
        for c in range(self.cols):
            self.grid[0][c].clear()

    # ── Ghost piece ───────────────────────────────────────────────

    def ghost_row(self, piece):
        """Vị trí thấp nhất piece có thể đặt."""
        dr = 0
        while self.can_place(piece, dr + 1, 0):
            dr += 1
        return piece.row + dr

    # ── Game over ─────────────────────────────────────────────────

    def is_topped_out(self):
        """Game kết thúc khi hàng 0 hoặc 1 có ô solid."""
        for r in range(2):
            if any(self.grid[r][c].is_solid() for c in range(self.cols)):
                return True
        return False
