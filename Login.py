import random
import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng đăng nhập")
        self.root.geometry("400x400")
        self.users_file = "users.json"
        self.users = self.load_users()
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.email = tk.StringVar()
        self.phone = tk.StringVar()
        self.otp_code = ""
        self.init_login_ui()

    def load_users(self):
        """Tải dữ liệu người dùng từ file users.json"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, "r", encoding="utf-8") as file:
                    return json.load(file)
            except Exception:
                return {}
        return {}

    def save_users(self):
        """Lưu dữ liệu người dùng vào file users.json"""
        try:
            with open(self.users_file, "w", encoding="utf-8") as file:
                json.dump(self.users, file, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu dữ liệu người dùng: {str(e)}")
            return False

    def send_otp_via_email(self, email_to):
        """Giả lập gửi OTP qua email (hiển thị qua messagebox)"""
        otp = str(random.randint(100000, 999999))
        messagebox.showinfo("Mã OTP đã gửi", f"OTP gửi tới email {email_to}: {otp}")
        return otp

    def send_otp_via_sms(self, phone_to):
        """Giả lập gửi OTP qua số điện thoại (hiển thị qua messagebox)"""
        otp = str(random.randint(100000, 999999))
        messagebox.showinfo("Mã OTP đã gửi", f"OTP gửi tới số {phone_to}: {otp}")
        return otp

    def clear_widgets(self):
        """Xóa tất cả widget trên giao diện"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def styled_label(self, text):
        """Tạo label với định dạng thống nhất"""
        return tk.Label(self.root, text=text, font=("Arial", 12), anchor="w", padx=10)

    def styled_entry(self, text_var, show=None):
        """Tạo entry với định dạng thống nhất"""
        return tk.Entry(self.root, textvariable=text_var, show=show, font=("Arial", 12), width=30)

    def init_login_ui(self):
        """Khởi tạo giao diện đăng nhập"""
        self.clear_widgets()
        tk.Label(self.root, text="Đăng Nhập", font=("Arial", 16, "bold")).pack(pady=15)

        self.styled_label("Tên đăng nhập").pack()
        self.styled_entry(self.username).pack(pady=5)

        self.styled_label("Mật khẩu").pack()
        self.styled_entry(self.password, show="*").pack(pady=5)

        tk.Button(self.root, text="Đăng nhập", font=("Arial", 11), command=self.login).pack(pady=10)
        tk.Button(self.root, text="Đăng ký tài khoản", font=("Arial", 11), command=self.init_register_ui).pack()
        tk.Button(self.root, text="Quên mật khẩu", font=("Arial", 11), command=self.init_forgot_ui).pack(pady=5)

    def init_register_ui(self):
        """Khởi tạo giao diện đăng ký"""
        self.clear_widgets()
        tk.Label(self.root, text="Đăng Ký", font=("Arial", 16, "bold")).pack(pady=15)

        self.styled_label("Tên đăng nhập").pack()
        self.styled_entry(self.username).pack(pady=5)

        self.styled_label("Mật khẩu").pack()
        self.styled_entry(self.password, show="*").pack(pady=5)

        self.styled_label("Email").pack()
        self.styled_entry(self.email).pack(pady=5)

        self.styled_label("Số điện thoại").pack()
        self.styled_entry(self.phone).pack(pady=5)

        tk.Button(self.root, text="Xác nhận đăng ký", font=("Arial", 11), command=self.register).pack(pady=10)
        tk.Button(self.root, text="Quay lại", font=("Arial", 11), command=self.init_login_ui).pack()

    def init_forgot_ui(self):
        """Khởi tạo giao diện quên mật khẩu"""
        self.clear_widgets()
        tk.Label(self.root, text="Quên Mật Khẩu", font=("Arial", 16, "bold")).pack(pady=15)

        self.styled_label("Chọn phương thức nhận OTP:").pack()
        self.method_var = tk.StringVar(value="email")
        tk.Radiobutton(self.root, text="Email", variable=self.method_var, value="email", font=("Arial", 12)).pack()
        tk.Radiobutton(self.root, text="Số điện thoại", variable=self.method_var, value="phone", font=("Arial", 12)).pack()

        self.styled_label("Nhập email hoặc số điện thoại đã đăng ký:").pack()
        self.contact_entry = self.styled_entry(self.email if self.method_var.get() == "email" else self.phone)
        self.contact_entry.pack(pady=5)

        # Cập nhật entry khi method_var thay đổi
        def update_contact_entry(*args):
            self.contact_entry.config(textvariable=self.email if self.method_var.get() == "email" else self.phone)
        self.method_var.trace("w", update_contact_entry)

        tk.Button(self.root, text="Gửi mã OTP", font=("Arial", 12), command=self.verify_contact).pack(pady=10)
        tk.Button(self.root, text="Quay lại", font=("Arial", 11), command=self.init_login_ui).pack()

    def verify_contact(self):
        """Xác minh email/số điện thoại và gửi OTP"""
        method = self.method_var.get()
        contact = self.email.get() if method == "email" else self.phone.get()
        if not contact:
            messagebox.showerror("Lỗi", f"Vui lòng nhập {method}!")
            return

        found_user = None
        if method == "email":
            for user, data in self.users.items():
                if data.get("email") == contact:
                    found_user = user
                    break
        elif method == "phone":
            for user, data in self.users.items():
                if data.get("phone") == contact:
                    found_user = user
                    break

        if not found_user:
            messagebox.showerror("Lỗi", f"Không tìm thấy {method} đã đăng ký.")
            return

        self.username.set(found_user)

        if method == "email":
            self.otp_code = self.send_otp_via_email(contact)
        else:
            self.otp_code = self.send_otp_via_sms(contact)

        if self.otp_code:
            self.init_reset_password_ui()

    def init_reset_password_ui(self):
        """Khởi tạo giao diện đặt lại mật khẩu"""
        self.clear_widgets()
        tk.Label(self.root, text="Đặt Lại Mật Khẩu", font=("Arial", 16, "bold")).pack(pady=15)

        self.styled_label("Nhập mã OTP").pack()
        otp_var = tk.StringVar()
        otp_entry = self.styled_entry(otp_var)
        otp_entry.pack(pady=5)

        self.styled_label("Mật khẩu mới").pack()
        self.styled_entry(self.password, show="*").pack(pady=5)

        def reset_password():
            if not otp_var.get() or not self.password.get():
                messagebox.showerror("Lỗi", "Vui lòng nhập mã OTP và mật khẩu mới!")
                return
            if otp_var.get() != self.otp_code:
                messagebox.showerror("Lỗi", "Mã OTP không chính xác.")
                return
            self.users[self.username.get()]["password"] = self.password.get()
            if self.save_users():
                messagebox.showinfo("Thành công", "Mật khẩu đã được cập nhật.")
                self.init_login_ui()
            else:
                messagebox.showerror("Lỗi", "Không thể cập nhật mật khẩu.")

        tk.Button(self.root, text="Xác nhận", font=("Arial", 12), command=reset_password).pack(pady=10)

    def login(self):
        """Xử lý đăng nhập"""
        uname = self.username.get()
        pword = self.password.get()
        if not uname or not pword:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên đăng nhập và mật khẩu!")
            return
        if uname in self.users and self.users[uname]["password"] == pword:
            messagebox.showinfo("Thành công", "Đăng nhập thành công!")
            self.root.destroy()
            try:
                import Gui
                root = tk.Tk()
                app = Gui.Controller(root, uname)
                root.mainloop()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể mở ứng dụng: {str(e)}")
        else:
            messagebox.showerror("Lỗi", "Tên đăng nhập hoặc mật khẩu sai.")

    def register(self):
        """Xử lý đăng ký"""
        uname = self.username.get()
        pword = self.password.get()
        email = self.email.get()
        phone = self.phone.get()
        if not all([uname, pword, email, phone]):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return
        if uname in self.users:
            messagebox.showerror("Lỗi", "Tên người dùng đã tồn tại!")
            return
        if "@" not in email:
            messagebox.showerror("Lỗi", "Email không hợp lệ!")
            return
        if not phone.isdigit():
            messagebox.showerror("Lỗi", "Số điện thoại không hợp lệ!")
            return
        self.users[uname] = {
            "password": pword,
            "name": "",
            "dob": datetime.now().strftime("%Y-%m-%d"),
            "email": email,
            "phone": phone,
            "role": "Sinh viên"
        }
        if self.save_users():
            messagebox.showinfo("Thành công", "Đăng ký thành công!")
            self.init_login_ui()
        else:
            messagebox.showerror("Lỗi", "Không thể đăng ký.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()