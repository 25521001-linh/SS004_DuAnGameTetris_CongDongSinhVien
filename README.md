# 🧱 Tetris Building

Môn học: Kỹ năng nghề nghiệp – SS004
Giáo viên: ThS. Nguyễn Văn Toàn
Nhóm thực hiện: Cộng đồng sinh viên

Thành viên:
- 25521001: Nguyễn Ngọc Linh – Trưởng nhóm
- 23520808: Võ Trọng Kiên
- 24521095: Võ Phan Kiều My
- 25520767: La Duy Khải
- 25520924: Nguyễn Minh Khuê

## Giới thiệu

Tetris Building là game xếp hình 2D phong cách Pixel Art, nơi người chơi điều khiển các khối gạch và vữa trên lưới 10×20 ô. Trò chơi kế thừa cơ chế Tetris cổ điển và bổ sung thêm hệ thống vật lý vữa, cơ chế kết dính khối, và combo dây chuyền độc đáo.

## Điểm nổi bật

- **Vữa có vật lý riêng** — sau vài giây, vữa hóa lỏng và chảy xuống bám vào khối bên dưới
- **Khối liên kết** (Gạch + Vữa) cần 2 lần xóa hàng mới bị phá

## Điều khiển

| Phím | Hành động |
|---|---|
| `A` / `←` | Di chuyển sang trái |
| `D` / `→` | Di chuyển sang phải |
| `S` / `↓` | Tăng tốc rơi |
| `W` / `↑` | Xoay khối |
| `Esc` | Tạm dừng |

## Hệ thống điểm

| Loại khối | Điểm |
|---|---|
| Gạch thường | +1 |
| Khối liên kết (mỗi ô) | +2 |

## Công nghệ

Ngôn ngữ: Python
Thư viện: Pygame
Độ phân giải: 800 × 600 px
Kích thước lưới: 10 × 20 ô (CELL_SIZE = 28px)

