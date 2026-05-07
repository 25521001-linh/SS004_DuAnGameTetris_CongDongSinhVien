# Tetris-game
- Môn học: Kỹ năng nghề nghiệp SS004
- Giáo viên: Ths Nguyễn Văn Toàn
- Nhóm thực hiện: Cộng đồng sinh viên
- Thành viên:  
    Nguyễn Ngọc Linh - trưởng nhóm   
    Võ Trọng Kiên   
    Nguyễn Phan Kiều My  
    La Duy Khải  
    Nguyễn Minh Khuê  

# 🧱 Tetris Building

**Tetris Building** là một game xếp hình lấy cảm hứng từ Tetris cổ điển, được tái thiết kế với chủ đề **công trường xây dựng** theo phong cách **Pixel Art 2D**.

## 🎮 Gameplay

Người chơi điều khiển các khối **gạch** và **vữa** trong khung hình kích thước **10×20 ô**, có thể xoay và sắp xếp các khối để lấp đầy các hàng ngang. Điểm đặc biệt so với Tetris gốc:

- **Vữa có vật lý riêng** — sau vài giây, vữa hóa lỏng và chảy xuống bám vào khối bên dưới, tạo liên kết.
- **Khối liên kết (Gạch + Vữa)** và **Khối cứng (Vữa + Vữa)** cần **2 lần xóa hàng** mới bị phá.
- **Hệ thống Combo** — khi phá khối phía dưới, các khối bên trên rơi xuống theo trọng lực, tạo chuỗi combo dây chuyền với hệ số nhân điểm tăng theo mỗi nhịp nổ.

## ⌨️ Điều khiển

| Phím | Hành động |
|------|-----------|
| `A` / `←` | Di chuyển sang trái |
| `D` / `→` | Di chuyển sang phải |
| `S` / `↓` | Tăng tốc rơi |
| `W` / `↑` | Xoay khối |
| `Esc` | Tạm dừng |

## 📊 Hệ thống điểm

| Loại khối | Điểm |
|-----------|------|
| Gạch thường | +1 |
| Khối liên kết (mỗi ô) | +2 |
| Khối cứng (N vữa) | +N |

## 🏗️ Cấu trúc Level

Game gồm **20 level** chia 3 giai đoạn theo tiến trình xây dựng:

| Giai đoạn | Level | Mô tả |
|-----------|-------|-------|
| Móng | 1–5 | Tốc độ chậm, làm quen cơ chế |
| Tường | 6–15 | Tốc độ tăng dần, áp lực xuất hiện |
| Mái | 16–20 | Tốc độ tăng mạnh, Dark Mode kích hoạt |

## 🛠️ Công nghệ

- **Ngôn ngữ:** Python
- **Thư viện:** Pygame
- **Độ phân giải:** 800×600
