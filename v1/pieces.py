# pieces.py — Định nghĩa 7 tetromino chuẩn + hàm xoay

# Mỗi piece là list 4 hàng × 4 cột, ký tự ' ' = trống, chữ cái = ô có gạch.
# Chuẩn Tetris Guideline (SRS spawn orientation).

PIECES = {
    'I': [
        [' ',' ',' ',' '],
        ['I','I','I','I'],
        [' ',' ',' ',' '],
        [' ',' ',' ',' '],
    ],
    'O': [
        [' ','O','O',' '],
        [' ','O','O',' '],
        [' ',' ',' ',' '],
        [' ',' ',' ',' '],
    ],
    'T': [
        [' ','T',' ',' '],
        ['T','T','T',' '],
        [' ',' ',' ',' '],
        [' ',' ',' ',' '],
    ],
    'S': [
        [' ','S','S',' '],
        ['S','S',' ',' '],
        [' ',' ',' ',' '],
        [' ',' ',' ',' '],
    ],
    'Z': [
        ['Z','Z',' ',' '],
        [' ','Z','Z',' '],
        [' ',' ',' ',' '],
        [' ',' ',' ',' '],
    ],
    'J': [
        ['J',' ',' ',' '],
        ['J','J','J',' '],
        [' ',' ',' ',' '],
        [' ',' ',' ',' '],
    ],
    'L': [
        [' ',' ','L',' '],
        ['L','L','L',' '],
        [' ',' ',' ',' '],
        [' ',' ',' ',' '],
    ],
    # Mortar piece — hình dạng giống T (có thể random I/T/O)
    'M': [
        [' ','M',' ',' '],
        ['M','M','M',' '],
        [' ',' ',' ',' '],
        [' ',' ',' ',' '],
    ],
}

# Danh sách các loại piece gạch (không bao gồm Mortar)
BRICK_TYPES = ['I', 'O', 'T', 'S', 'Z', 'J', 'L']

# Danh sách các loại piece vữa
MORTAR_TYPES = ['M']


def rotate_cw(matrix):
    """Xoay ma trận 4×4 theo chiều kim đồng hồ 90°.
    
    rotated[j][3-i] = original[i][j]
    Trả về ma trận mới (không thay đổi bản gốc).
    """
    size = len(matrix)  # luôn là 4
    rotated = [[' '] * size for _ in range(size)]
    for i in range(size):
        for j in range(size):
            rotated[j][size - 1 - i] = matrix[i][j]
    return rotated


def get_cells(matrix):
    """Trả về danh sách (row, col) của các ô không rỗng trong ma trận."""
    cells = []
    for r, row in enumerate(matrix):
        for c, val in enumerate(row):
            if val != ' ':
                cells.append((r, c))
    return cells


class Piece:
    """Đại diện cho một tetromino đang rơi.
    
    Attributes:
        kind (str): loại piece ('I', 'O', ..., 'M')
        matrix (list): ma trận 4×4 hiện tại (sau khi xoay)
        col (int): cột bên trái của bounding box (0-indexed)
        row (int): hàng trên cùng của bounding box (0-indexed, có thể âm khi spawn)
        rotation (int): 0-3, góc xoay hiện tại
    """

    def __init__(self, kind, start_col=3):
        self.kind = kind
        self.rotation = 0
        self._rotations = _build_rotations(PIECES[kind])
        self.matrix = self._rotations[0]
        self.col = start_col
        self.row = 0  # spawn từ đỉnh

    def get_cells(self):
        """Trả về (board_row, board_col) của mỗi ô khối."""
        return [
            (self.row + r, self.col + c)
            for r, c in get_cells(self.matrix)
        ]

    def rotated_matrix(self):
        """Ma trận sau khi xoay CW 1 lần (chưa áp dụng vào piece)."""
        next_rot = (self.rotation + 1) % 4
        return self._rotations[next_rot], next_rot

    def apply_rotation(self):
        """Áp dụng xoay CW (gọi sau khi đã kiểm tra hợp lệ)."""
        self.rotation = (self.rotation + 1) % 4
        self.matrix = self._rotations[self.rotation]

    @property
    def is_mortar(self):
        return self.kind == 'M'


def _build_rotations(base_matrix):
    """Xây dựng 4 trạng thái xoay từ ma trận gốc."""
    rotations = [base_matrix]
    current = base_matrix
    for _ in range(3):
        current = rotate_cw(current)
        rotations.append(current)
    return rotations
