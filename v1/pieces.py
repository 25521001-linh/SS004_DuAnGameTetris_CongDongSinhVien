# pieces.py — 7 Tetromino + khối Vữa (M) + hàm xoay

PIECES = {
    'I': [
        [0,0,0,0],
        [1,1,1,1],
        [0,0,0,0],
        [0,0,0,0],
    ],
    'O': [
        [0,1,1,0],
        [0,1,1,0],
        [0,0,0,0],
        [0,0,0,0],
    ],
    'T': [
        [0,1,0,0],
        [1,1,1,0],
        [0,0,0,0],
        [0,0,0,0],
    ],
    'S': [
        [0,1,1,0],
        [1,1,0,0],
        [0,0,0,0],
        [0,0,0,0],
    ],
    'Z': [
        [1,1,0,0],
        [0,1,1,0],
        [0,0,0,0],
        [0,0,0,0],
    ],
    'J': [
        [1,0,0,0],
        [1,1,1,0],
        [0,0,0,0],
        [0,0,0,0],
    ],
    'L': [
        [0,0,1,0],
        [1,1,1,0],
        [0,0,0,0],
        [0,0,0,0],
    ],
    # Vữa — dùng hình T (theo GDD, vữa cũng có hình dạng tetromino)
    'M': [
        [0,1,0,0],
        [1,1,1,0],
        [0,0,0,0],
        [0,0,0,0],
    ],
}

BRICK_TYPES  = ['I', 'O', 'T', 'S', 'Z', 'J', 'L']
MORTAR_TYPES = ['M']


def rotate_cw(matrix):
    """Xoay ma trận 4×4 theo chiều kim đồng hồ 90°."""
    n = len(matrix)
    rotated = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            rotated[j][n - 1 - i] = matrix[i][j]
    return rotated


def _build_rotations(base):
    """Xây 4 trạng thái xoay."""
    rots = [base]
    cur = base
    for _ in range(3):
        cur = rotate_cw(cur)
        rots.append(cur)
    return rots


def get_filled_cells(matrix):
    """Trả về list (row, col) của các ô != 0."""
    cells = []
    for r, row in enumerate(matrix):
        for c, val in enumerate(row):
            if val:
                cells.append((r, c))
    return cells


class Piece:
    """Tetromino đang rơi.

    Attributes:
        kind: str — 'I','O','T','S','Z','J','L','M'
        row, col: vị trí bounding box trên board (row có thể âm khi spawn)
        rotation: 0-3
        is_mortar: True nếu kind == 'M'
    """

    def __init__(self, kind, start_col=3, start_row=0):
        self.kind = kind
        self.rotation = 0
        self._rotations = _build_rotations(PIECES[kind])
        self.matrix = self._rotations[0]
        self.col = start_col
        self.row = start_row
        self.is_mortar = (kind == 'M')

    def get_cells(self):
        """Trả về list (board_row, board_col) của mỗi ô filled."""
        return [(self.row + r, self.col + c)
                for r, c in get_filled_cells(self.matrix)]

    def rotated_matrix(self):
        """Trả về (new_matrix, new_rotation_index) cho CW."""
        nr = (self.rotation + 1) % 4
        return self._rotations[nr], nr

    def apply_rotation(self, new_matrix, new_rot):
        """Áp dụng xoay (gọi sau khi đã kiểm tra hợp lệ)."""
        self.rotation = new_rot
        self.matrix = new_matrix

    def clone(self):
        """Bản sao nông cho preview/next piece."""
        p = Piece(self.kind, self.col, self.row)
        p.rotation = self.rotation
        p.matrix = self._rotations[self.rotation]
        return p
