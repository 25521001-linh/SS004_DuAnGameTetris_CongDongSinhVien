# mortar.py — Quản lý timer vữa: SOLID → LIQUID → chảy xuống
#
# GDD:
# - Thời gian vữa chảy = cố định theo hệ thống (2.5s), KHÔNG thay đổi theo level
# - Vữa dù bị đè hay không, vẫn chảy theo logic vật lý
# - Vữa chảy xuống khối ĐẦU TIÊN chạm vào, không tuột xuống đáy map

from constants import MORTAR_MELT_TIME, CELL_MORTAR


class MortarEntry:
    """Theo dõi 1 ô vữa đang đếm thời gian hóa lỏng."""
    __slots__ = ('row', 'col', 'timer')

    def __init__(self, row, col):
        self.row   = row
        self.col   = col
        self.timer = MORTAR_MELT_TIME


class MortarManager:
    """Quản lý tất cả ô vữa đang chờ hóa lỏng.

    Khi timer về 0 → gọi board.apply_mortar_coat() để
    chảy xuống khối đầu tiên bên dưới.
    """

    def __init__(self):
        self._entries = {}  # (row, col) → MortarEntry

    def register(self, row, col):
        """Đăng ký ô vữa mới."""
        key = (row, col)
        if key not in self._entries:
            self._entries[key] = MortarEntry(row, col)

    def register_piece(self, piece):
        """Đăng ký tất cả ô vữa của piece vừa lock."""
        if not piece.is_mortar:
            return
        for r, c in piece.get_cells():
            if r >= 0:
                self.register(r, c)

    def update(self, dt, board):
        """Cập nhật timer. Khi hết → vữa hóa lỏng và chảy.

        GDD: Vữa dù bị đè hay không vẫn chảy.
        GDD: Thời gian = cố định, không phụ thuộc level.

        dt: delta time (giây).
        board: Board object.
        Trả về: list (row, col) các ô vừa chảy thành công.
        """
        melted = []
        expired = []

        for key, entry in list(self._entries.items()):
            entry.timer -= dt
            if entry.timer <= 0:
                expired.append(key)

        for key in expired:
            entry = self._entries.pop(key)
            r, c = entry.row, entry.col

            if 0 <= r < board.rows and 0 <= c < board.cols:
                cell = board.grid[r][c]
                if cell.cell_type == CELL_MORTAR:
                    # GDD: chảy xuống khối đầu tiên chạm vào
                    success = board.apply_mortar_coat(r, c)
                    if success:
                        melted.append((r, c))
                    # Nếu không chảy được (đáy map) → vữa giữ nguyên vị trí

        return melted

    def remove(self, row, col):
        """Xóa entry khi ô vữa bị clear."""
        self._entries.pop((row, col), None)

    def adjust_after_row_removal(self, cleared_row):
        """Khi 1 hàng bị xóa, dịch entry phía trên xuống 1."""
        new_entries = {}
        for (r, c), entry in self._entries.items():
            if r == cleared_row:
                continue
            if r < cleared_row:
                new_r = r + 1
                entry.row = new_r
                new_entries[(new_r, c)] = entry
            else:
                new_entries[(r, c)] = entry
        self._entries = new_entries

    def clear_all(self):
        self._entries.clear()

    def get_active_positions(self):
        """Set (row, col) các ô vữa đang đếm ngược (để render)."""
        return set(self._entries.keys())

    def get_timer(self, row, col):
        """Thời gian còn lại, None nếu không tracking."""
        entry = self._entries.get((row, col))
        return entry.timer if entry else None
