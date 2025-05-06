# 11_Quan_Ly_Thu_Nhap_Chi_Tieu_Ca_Nhan

## Giới thiệu đề tài

Đây là một ứng dụng quản lý tài chính cá nhân, cho phép người dùng:
- Đăng nhập tài khoản.
- Thêm, chỉnh sửa, xóa các khoản thu nhập và chi tiêu.
- Xem thông tin cá nhân và các giao dịch.
- Lưu trữ dữ liệu cục bộ bằng file `.json`.

Ứng dụng giúp sinh viên hoặc người đi làm có thể theo dõi dòng tiền hàng ngày dễ dàng hơn.

## Nhóm thực hiện

- **Tên nhóm**: Nhóm 11
- **Thành viên**:
Nguyễn Duy Trường     _ 24110276
Trần Thu Phương       _ 24110261
Nguyễn Đức Anh        _ 24110334
Phạm Ngọc Minh Anh    _ 24110353

## 🛠 Công nghệ sử dụng

- Ngôn ngữ: Python
- Thư viện GUI: `tkinter`
- Lưu trữ dữ liệu: `json`
- Các module tự viết: `Login.py`, `UserInfo.py`, `Gui.py`

## Cấu trúc thư mục

├──_pycache              #thư viện```
├── Gui.py               # Giao diện chính của chương trình
├── Login.py             # Xử lý đăng nhập người dùng
├── UserInfo.py          # Quản lý thông tin người dùng
├── users.json           # Dữ liệu người dùng
├── transactions.json    # Dữ liệu thu nhập/chi tiêu
├── README.md            # Tệp mô tả (file này)
└── LICENSE              # Giấy phép sử dụng (nếu có)
```

## Cách chạy ứng dụng

### 1. Cài Python (nếu chưa có):
- Tải tại: https://www.python.org/downloads/

### 2. Clone project về máy:

```bash
git clone https://github.com/TranPhuong126/Group11_Quan_Ly_Thu_Nhap_Chi_Tieu_Ca_Nhan.git
cd Group11_Quan_Ly_Thu_Nhap_Chi_Tieu_Ca_Nhan

### 3. Run chương trình:
```-Tải cả file xuống, sau đó run code tại file "Login.py" để chạy chương trình

### 3. Chạy ứng dụng:

```bash
python Gui.py
```

> Lưu ý: Đảm bảo file `users.json` và `transactions.json` tồn tại trong thư mục gốc.

## Tính năng chính

- Đăng nhập tài khoản
- Quản lý thông tin cá nhân
- Thêm/sửa/xóa các khoản thu nhập hoặc chi tiêu.
- Xuất dữ liệu sang định dạng CSV

## Ghi chú

- Đây là sản phẩm thuộc môn học LẬP TRÌNH HƯỚNG ĐỐI TƯỢNG.

## Giấy phép

MIT License – tự do sử dụng và chỉnh sửa cho mục đích học tập.
