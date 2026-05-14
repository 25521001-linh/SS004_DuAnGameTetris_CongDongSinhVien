# mortar.py — Quản lý timer vữa: SOLID → LIQUID → chảy xuống

from constants import MORTAR_MELT_TIME, CELL_MORTAR


class MortarEntry:
    """Theo dõi 1 ô vữa đang đếm thời gian."""
    __slots__ = ('row', 'col', 'timer')

    def __init__(self, row, col):
        self.row   = row
        self.col   = col
        self.timer = MORTAR_MELT_TIME   # giây còn lại


class MortarManager:
    """Quản lý danh sách tất cả ô vữa đang chờ hóa lỏng.
    
    Khi timer của 1 ô về 0, gọi board.apply_mortar_coat() để
    tạo liên kết với ô bên dưới.
    """

    def __init__(self):
        # dict (row, col) → MortarEntry để tránh trùng lặp
        self._entries = {}

    def register(self, row, col):
        """Đăng ký ô vữa mới vừa được đặt xuống board."""
        key = (row, col)
        if key not in self._entries:
            self._entries[key] = MortarEntry(row, col)

    def register_piece(self, piece):
        """Đăng ký tất cả ô vữa của một piece vừa lock."""
        if not piece.is_mortar:
            return
        for r, c in piece.get_cells():
            self.register(r, c)

    def update(self, dt, board):
        """Cập nhật timer tất cả ô vữa.
        
        dt: delta time tính bằng giây.
        board: Board object để apply coat.
        
        Trả về: danh sách (row, col) các ô vừa hóa lỏng + chảy.
        """
        melted = []
        expired_keys = []

        for key, entry in list(self._entries.items()):
            entry.timer -= dt
            if entry.timer <= 0:
                expired_keys.append(key)

        for key in expired_keys:
            entry = self._entries.pop(key)
            # Kiểm tra ô vẫn còn là mortar trên board
            r, c = entry.row, entry.col
            if 0 <= r < board.rows and 0 <= c < board.cols:
                cell = board.grid[r][c]
                if cell.cell_type == CELL_MORTAR:
                    success = board.apply_mortar_coat(r, c)
                    if success:
                        melted.append((r, c))
                    else:
                        # Không chảy được (đáy board, hoặc ô dưới bị LINKED/HARD)
                        # Vữa ở lại như gạch thường (hp=1)
                        pass

        return melted

    def remove(self, row, col):
        """Xóa entry khi ô vữa bị clear khỏi board."""
        self._entries.pop((row, col), None)

    def remove_row(self, cleared_row):
        """Khi một hàng bị xóa, dịch tất cả entry phía trên xuống 1."""
        new_entries = {}
        for (r, c), entry in self._entries.items():
            if r == cleared_row:
                continue          # ô này đã bị xóa
            if r < cleared_row:
                new_r = r + 1     # dịch xuống 1 hàng
                entry.row = new_r
                new_entries[(new_r, c)] = entry
            else:
                new_entries[(r, c)] = entry
        self._entries = new_entries

    def clear(self):
        self._entries.clear()

    def get_liquid_positions(self):
        """Trả về set (row, col) các ô vữa đang đếm ngược (để render màu khác nhau)."""
        return set(self._entries.keys())

    def get_timer(self, row, col):
        """Trả về thời gian còn lại của ô vữa, hoặc None nếu không có."""
        entry = self._entries.get((row, col))
        return entry.timer if entry else None
