# board.py — Trạng thái bảng, va chạm, xóa dòng, trọng lực

from constants import (
    BOARD_COLS, BOARD_ROWS,
    CELL_EMPTY, CELL_BRICK, CELL_MORTAR, CELL_LINKED, CELL_HARD,
    SCORE_BRICK, SCORE_LINKED, SCORE_HARD_PER_UNIT,
    WALL_KICKS,
)


class Cell:
    """Một ô trên board.
    
    Attributes:
        cell_type (str): CELL_EMPTY | CELL_BRICK | CELL_MORTAR | CELL_LINKED | CELL_HARD
        kind (str|None): loại piece gốc ('I','O','T','S','Z','J','L','M') hoặc None
        hp (int): số lần xóa cần thiết (1 = bình thường, 2 = cần 2 lần)
        cracked (bool): đã bị xóa lần 1 (vết nứt xuất hiện)
        mortar_units (int): số đơn vị vữa trong khối cứng (dùng tính điểm)
    """

    __slots__ = ('cell_type', 'kind', 'hp', 'cracked', 'mortar_units')

    def __init__(self):
        self.cell_type   = CELL_EMPTY
        self.kind        = None
        self.hp          = 1
        self.cracked     = False
        self.mortar_units = 0

    def is_empty(self):
        return self.cell_type == CELL_EMPTY

    def is_solid(self):
        """Ô chiếm chỗ (không rỗng)."""
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

    def set_linked(self, brick_kind):
        """Gạch + Vữa → HP = 2."""
        self.cell_type    = CELL_LINKED
        self.kind         = brick_kind
        self.hp           = 2
        self.cracked      = False
        self.mortar_units = 1

    def set_hard(self, units):
        """Vữa + Vữa → HP = 2, điểm = units."""
        self.cell_type    = CELL_HARD
        self.kind         = 'M'
        self.hp           = 2
        self.cracked      = False
        self.mortar_units = units

    def copy_from(self, other):
        self.cell_type    = other.cell_type
        self.kind         = other.kind
        self.hp           = other.hp
        self.cracked      = other.cracked
        self.mortar_units = other.mortar_units

    def clear(self):
        self.__init__()


class Board:
    """Bảng game 10 cột × 20 hàng.
    
    grid[row][col] — row 0 = đỉnh, row 19 = đáy.
    """

    def __init__(self):
        self.cols = BOARD_COLS
        self.rows = BOARD_ROWS
        self.grid = [[Cell() for _ in range(self.cols)] for _ in range(self.rows)]

    # ── Truy cập ──────────────────────────────────────────────────

    def cell(self, row, col):
        return self.grid[row][col]

    def in_bounds(self, row, col):
        return 0 <= col < self.cols and row < self.rows

    def is_empty(self, row, col):
        if not self.in_bounds(row, col):
            return False
        if row < 0:
            return True  # trên đỉnh board = hợp lệ khi spawn
        return self.grid[row][col].is_empty()

    # ── Va chạm ───────────────────────────────────────────────────

    def can_place(self, piece, dr=0, dc=0):
        """Kiểm tra piece (dịch thêm dr hàng, dc cột) có hợp lệ không."""
        for r, c in piece.get_cells():
            nr, nc = r + dr, c + dc
            if nc < 0 or nc >= self.cols:
                return False
            if nr >= self.rows:
                return False
            if nr >= 0 and self.grid[nr][nc].is_solid():
                return False
        return True

    def can_rotate(self, piece):
        """Thử xoay CW với wall-kick, trả về (True, dc_offset) hoặc (False, 0)."""
        new_matrix, new_rot = piece.rotated_matrix()
        # Lưu tạm để kiểm tra
        old_matrix   = piece.matrix
        old_rotation = piece.rotation
        piece.matrix   = new_matrix
        piece.rotation = new_rot

        for dc, dr in WALL_KICKS:
            if self.can_place(piece, dr, dc):
                # Khôi phục
                piece.matrix   = old_matrix
                piece.rotation = old_rotation
                return True, dc, dr

        piece.matrix   = old_matrix
        piece.rotation = old_rotation
        return False, 0, 0

    # ── Đặt piece xuống board ─────────────────────────────────────

    def lock_piece(self, piece):
        """Đặt piece cố định vào board."""
        for r, c in piece.get_cells():
            if 0 <= r < self.rows and 0 <= c < self.cols:
                cell = self.grid[r][c]
                if piece.is_mortar:
                    cell.set_mortar()
                else:
                    cell.set_brick(piece.kind)

    # ── Xóa dòng & tính điểm ──────────────────────────────────────

    def _is_full_line(self, row):
        return all(self.grid[row][c].is_solid() for c in range(self.cols))

    def _score_for_line(self, row):
        """Tính điểm cho 1 dòng đầy (chưa xóa).
        
        - Ô gạch thường (hp=1): +1
        - Ô liên kết/khối cứng (hp=2, cracked=False): đây là lần xóa đầu → không tính điểm,
          chỉ giảm hp → hp=1, cracked=True. Ô không bị xóa.
        - Ô liên kết/khối cứng (hp=1, cracked=True): lần xóa thứ 2 → tính điểm rồi xóa.
        
        Trả về: (score_gained, cleared_cols_set, needs_second_clear_cols_set)
        """
        score = 0
        cleared   = set()
        second    = set()

        for c in range(self.cols):
            cell = self.grid[row][c]
            if cell.hp == 1 and not cell.cracked:
                # Bình thường → xóa ngay
                if cell.cell_type == CELL_BRICK:
                    score += SCORE_BRICK
                elif cell.cell_type == CELL_MORTAR:
                    score += SCORE_HARD_PER_UNIT * cell.mortar_units
                cleared.add(c)
            elif cell.hp == 2:
                # Lần xóa 1 → giảm hp, đánh dấu nứt, KHÔNG xóa
                cell.hp = 1
                cell.cracked = True
                second.add(c)
            elif cell.hp == 1 and cell.cracked:
                # Lần xóa 2 → tính điểm và xóa
                if cell.cell_type == CELL_LINKED:
                    score += SCORE_LINKED
                elif cell.cell_type == CELL_HARD:
                    score += SCORE_HARD_PER_UNIT * cell.mortar_units
                cleared.add(c)

        return score, cleared, second

    def clear_lines(self):
        """Quét toàn bộ board, xóa các dòng đầy.
        
        Logic 2-lần cho khối liên kết / cứng:
        - Dòng đủ điều kiện xóa (tất cả ô đều is_solid) được xử lý.
        - Ô hp=2 → chỉ crack (hp→1), ô không bị remove.
        - Nếu sau khi crack, dòng vẫn "đầy" (tất cả ô solid) → tính tiếp.
        - Thực ra: dòng bị "xóa" chỉ khi không còn ô hp=2 nào còn sót.
        
        Trả về: tổng điểm cộng vào.
        """
        total_score = 0
        row = self.rows - 1

        while row >= 0:
            if not self._is_full_line(row):
                row -= 1
                continue

            score, cleared_cols, second_cols = self._score_for_line(row)
            total_score += score

            if len(second_cols) == 0:
                # Xóa hoàn toàn dòng này, shift tất cả hàng trên xuống
                self._remove_row(row)
                # Không giảm row vì hàng mới vừa dịch xuống cần kiểm tra lại
            else:
                # Dòng chưa xóa được (còn ô cracked), tiếp tục scan lên
                row -= 1

        return total_score

    def _remove_row(self, remove_row):
        """Xóa hàng `remove_row`, dịch tất cả hàng trên xuống 1."""
        for r in range(remove_row, 0, -1):
            for c in range(self.cols):
                self.grid[r][c].copy_from(self.grid[r - 1][c])
        # Hàng đỉnh → trống
        for c in range(self.cols):
            self.grid[0][c].clear()

    # ── Mortar coat (lớp phủ vữa lên gạch bên dưới) ───────────────

    def apply_mortar_coat(self, mortar_row, mortar_col):
        """Khi vữa tại (mortar_row, mortar_col) hóa lỏng, tìm ô đầu tiên
        phía dưới và tạo liên kết hoặc khối cứng.
        
        Trả về: True nếu thành công.
        """
        if mortar_row < 0 or mortar_row >= self.rows:
            return False
        if mortar_col < 0 or mortar_col >= self.cols:
            return False

        mortar_cell = self.grid[mortar_row][mortar_col]
        if mortar_cell.cell_type != CELL_MORTAR:
            return False

        # Tìm ô đầu tiên phía dưới (ngay kế tiếp)
        target_row = mortar_row + 1
        if target_row >= self.rows:
            # Đáy board — vữa không chảy được, giữ nguyên
            return False

        target_cell = self.grid[target_row][mortar_col]

        if target_cell.is_empty():
            # Không có gì phía dưới → vữa rơi xuống ô trống (như trọng lực)
            target_cell.set_mortar()
            mortar_cell.clear()
            return True

        if target_cell.cell_type == CELL_BRICK:
            # Gạch + Vữa → LINKED (hp=2)
            brick_kind = target_cell.kind
            target_cell.set_linked(brick_kind)
            mortar_cell.clear()
            return True

        if target_cell.cell_type in (CELL_MORTAR, CELL_HARD):
            # Vữa + Vữa → HARD (hp=2, mortar_units tăng)
            units = target_cell.mortar_units + mortar_cell.mortar_units
            target_cell.set_hard(units)
            mortar_cell.clear()
            return True

        # Các trường hợp còn lại (LINKED, HARD đã đầy, v.v.) → không chảy
        return False

    # ── Ghost piece (bóng thả) ─────────────────────────────────────

    def ghost_row(self, piece):
        """Trả về row của ghost piece (vị trí thấp nhất piece có thể đặt)."""
        dr = 0
        while self.can_place(piece, dr + 1, 0):
            dr += 1
        return piece.row + dr

    # ── Kiểm tra game over ─────────────────────────────────────────

    def is_game_over(self):
        """Game kết thúc khi có ô ở hàng 0 bị chiếm."""
        return any(self.grid[0][c].is_solid() for c in range(self.cols))
