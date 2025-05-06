import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import csv
from datetime import datetime
from tkcalendar import DateEntry
from abc import ABC, abstractmethod

class BaseView(ABC):
    """Abstract base class for all views"""
    def __init__(self, parent):
        self._parent = parent
        self._frame = ttk.Frame(parent)
    
    def get_frame(self):
        return self._frame
    
    def pack(self, **kwargs):
        self._frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        self._frame.grid(**kwargs)
    
    @abstractmethod
    def update_view(self, data=None):
        """Update the view with new data"""
        pass

class UserInfoView(BaseView):
    """View for managing user information"""
    def __init__(self, parent, controller, username):
        super().__init__(parent)
        self.controller = controller
        self.username = username
        self.users_file = "users.json"
        self.users = self.load_users()
        
        # Các trường thông tin
        self.name_var = tk.StringVar()
        self.dob_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.role_var = tk.StringVar()
        
        # Danh sách đối tượng
        self.roles = ["Học sinh", "Sinh viên", "Gia đình", "Freelance", "Tổ chức phi lợi nhuận"]
        
        # Thiết lập giao diện
        self.setup_ui()
        
        # Load thông tin người dùng
        self.update_view()

    def load_users(self):
        """Tải dữ liệu người dùng từ file users.json"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, "r", encoding="utf-8") as file:
                    return json.load(file)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể đọc dữ liệu người dùng: {str(e)}")
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

    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        frame = ttk.LabelFrame(self._frame, text="Thông Tin Cá Nhân")
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Tên
        ttk.Label(frame, text="Tên:").pack(anchor="w", padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.name_var, width=30).pack(fill="x", padx=5)

        # Ngày tháng năm sinh
        ttk.Label(frame, text="Ngày sinh (YYYY-MM-DD):").pack(anchor="w", padx=5, pady=5)
        self.dob_entry = DateEntry(frame, width=12, date_pattern='yyyy-mm-dd', textvariable=self.dob_var)
        self.dob_entry.pack(fill="x", padx=5)

        # Email
        ttk.Label(frame, text="Email:").pack(anchor="w", padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.email_var, width=30).pack(fill="x", padx=5)

        # Số điện thoại
        ttk.Label(frame, text="Số điện thoại:").pack(anchor="w", padx=5, pady=5)
        ttk.Entry(frame, textvariable=self.phone_var, width=30).pack(fill="x", padx=5)

        # Đối tượng
        ttk.Label(frame, text="Đối tượng:").pack(anchor="w", padx=5, pady=5)
        ttk.Combobox(frame, textvariable=self.role_var, values=self.roles, state="readonly").pack(fill="x", padx=5)

        # Nút điều khiển
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill="x", pady=20)

        ttk.Button(button_frame, text="Lưu thay đổi", command=self.save_changes).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Xuất CSV", command=self.export_csv).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Xuất JSON", command=self.export_json).pack(side="left", padx=5)

    def update_view(self, data=None):
        """Cập nhật thông tin người dùng lên giao diện"""
        user_data = self.users.get(self.username, {})
        self.name_var.set(user_data.get("name", ""))
        self.dob_var.set(user_data.get("dob", datetime.now().strftime("%Y-%m-%d")))
        self.email_var.set(user_data.get("email", ""))
        self.phone_var.set(user_data.get("phone", ""))
        self.role_var.set(user_data.get("role", self.roles[0]))

    def save_changes(self):
        """Lưu thay đổi thông tin người dùng"""
        try:
            # Validate input
            name = self.name_var.get().strip()
            if not name:
                raise ValueError("Tên không được để trống")
            
            dob = self.dob_var.get()
            try:
                datetime.strptime(dob, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Ngày sinh không đúng định dạng (YYYY-MM-DD)")

            email = self.email_var.get().strip()
            if not email or "@" not in email:
                raise ValueError("Email không hợp lệ")

            phone = self.phone_var.get().strip()
            if not phone or not phone.isdigit():
                raise ValueError("Số điện thoại không hợp lệ")

            role = self.role_var.get()
            if role not in self.roles:
                raise ValueError("Đối tượng không hợp lệ")

            # Cập nhật thông tin người dùng
            self.users[self.username] = {
                "password": self.users.get(self.username, {}).get("password", ""),
                "name": name,
                "dob": dob,
                "email": email,
                "phone": phone,
                "role": role
            }

            # Lưu vào file
            if self.save_users():
                messagebox.showinfo("Thành công", "Thông tin đã được cập nhật!")
                self.update_view()
            else:
                messagebox.showerror("Lỗi", "Không thể lưu thông tin")
        except ValueError as e:
            messagebox.showwarning("Lỗi", str(e))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")

    def export_csv(self):
        """Xuất thông tin người dùng ra file CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")],
                title="Xuất thông tin sang CSV"
            )
            if not filename:
                return

            user_data = self.users.get(self.username, {})
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Tên đăng nhập", "Tên", "Ngày sinh", "Email", "Số điện thoại", "Đối tượng"])
                writer.writerow([
                    self.username,
                    user_data.get("name", ""),
                    user_data.get("dob", ""),
                    user_data.get("email", ""),
                    user_data.get("phone", ""),
                    user_data.get("role", "")
                ])
            messagebox.showinfo("Thành công", "Thông tin đã được xuất sang CSV!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi khi xuất CSV: {str(e)}")

    def export_json(self):
        """Xuất thông tin người dùng ra file JSON"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json")],
                title="Xuất thông tin sang JSON"
            )
            if not filename:
                return

            user_data = self.users.get(self.username, {})
            export_data = {
                "username": self.username,
                "name": user_data.get("name", ""),
                "dob": user_data.get("dob", ""),
                "email": user_data.get("email", ""),
                "phone": user_data.get("phone", ""),
                "role": user_data.get("role", "")
            }
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(export_data, file, indent=4, ensure_ascii=False)
            messagebox.showinfo("Thành công", "Thông tin đã được xuất sang JSON!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi khi xuất JSON: {str(e)}")