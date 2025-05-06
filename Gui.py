import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from tkcalendar import DateEntry
from abc import ABC, abstractmethod

# Note: Ensure the following dependencies are installed:
# - tkcalendar: pip install tkcalendar
# - matplotlib: pip install matplotlib
# - pandas: pip install pandas

class TransactionModel:
    """Base model class for managing transaction data"""
    def __init__(self, id, date, description, amount, category=None):
        self._id = int(id)  # Ensure ID is an integer
        try:
            # Validate and standardize date format
            self._date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            self._date = datetime.now().strftime("%Y-%m-%d")
        self._description = description if description else ""
        self._amount = float(amount) if amount else 0.0
        self._category = category if category else "Khác"
    
    @property
    def id(self):
        return self._id
        
    @property
    def date(self):
        return self._date
        
    @date.setter
    def date(self, value):
        try:
            self._date = datetime.strptime(value, "%Y-%m-%d").strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            self._date = datetime.now().strftime("%Y-%m-%d")
        
    @property
    def description(self):
        return self._description
        
    @description.setter
    def description(self, value):
        self._description = value if value else ""
        
    @property
    def amount(self):
        return self._amount
        
    @amount.setter
    def amount(self, value):
        self._amount = float(value) if value else 0.0
        
    @property
    def category(self):
        return self._category
        
    @category.setter
    def category(self, value):
        self._category = value if value else "Khác"
    
    @abstractmethod
    def get_type(self):
        """Return the transaction type"""
        pass
    
    def get_display_type(self):
        """Return display-friendly transaction type"""
        return "Thu nhập" if self.get_type() == "income" else "Chi tiêu"
    
    def to_dict(self):
        """Convert transaction to dictionary"""
        return {
            "id": self._id,
            "date": self._date,
            "description": self._description,
            "amount": self._amount,
            "type": self.get_type(),
            "category": self._category
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a transaction from dictionary"""
        try:
            if data.get("type") == "income":
                return IncomeTransaction(
                    data.get("id", 1), 
                    data.get("date", datetime.now().strftime("%Y-%m-%d")), 
                    data.get("description", ""), 
                    data.get("amount", 0.0), 
                    data.get("category", "Khác")
                )
            else:
                return ExpenseTransaction(
                    data.get("id", 1), 
                    data.get("date", datetime.now().strftime("%Y-%m-%d")), 
                    data.get("description", ""), 
                    data.get("amount", 0.0), 
                    data.get("category", "Khác")
                )
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo giao dịch từ dữ liệu: {str(e)}")
            return None

class IncomeTransaction(TransactionModel):
    """Model for income transactions"""
    def get_type(self):
        return "income"

class ExpenseTransaction(TransactionModel):
    """Model for expense transactions"""
    def get_type(self):
        return "expense"

class TransactionManager:
    """Manager class for handling transactions"""
    def __init__(self):
        self._transactions = []
        self._filename = "transactions.json"
        self._income_categories = ["Lương", "Thưởng", "Đầu tư", "Khác"]
        self._expense_categories = ["Ăn uống", "Đi lại", "Mua sắm", "Giải trí", "Hóa đơn", "Khác"]
        self.load_transactions()
    
    @property
    def transactions(self):
        return self._transactions
    
    @property
    def income_categories(self):
        return self._income_categories
    
    @property
    def expense_categories(self):
        return self._expense_categories
    
    def load_transactions(self):
        """Load transactions from file"""
        if os.path.exists(self._filename):
            try:
                with open(self._filename, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    self._transactions = [t for t in (TransactionModel.from_dict(d) for d in data) if t is not None]
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể đọc dữ liệu: {str(e)}")
                self._transactions = []
        else:
            self._transactions = []
    
    def save_transactions(self):
        """Save transactions to file"""
        try:
            with open(self._filename, "w", encoding="utf-8") as file:
                data = [t.to_dict() for t in self._transactions]
                json.dump(data, file, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu dữ liệu: {str(e)}")
            return False
    
    def add_transaction(self, transaction):
        """Add a new transaction"""
        if transaction:
            self._transactions.append(transaction)
            return self.save_transactions()
        return False
    
    def update_transaction(self, transaction):
        """Update an existing transaction"""
        if transaction:
            for i, t in enumerate(self._transactions):
                if t.id == transaction.id:
                    self._transactions[i] = transaction
                    return self.save_transactions()
        return False
    
    def delete_transaction(self, transaction_id):
        """Delete a transaction by ID"""
        initial_len = len(self._transactions)
        self._transactions = [t for t in self._transactions if t.id != transaction_id]
        if len(self._transactions) < initial_len:
            return self.save_transactions()
        return False
    
    def get_transaction_by_id(self, transaction_id):
        """Get a transaction by ID"""
        for t in self._transactions:
            if t.id == transaction_id:
                return t
        return None
    
    def get_next_id(self):
        """Get next available ID"""
        if not self._transactions:
            return 1
        try:
            max_id = max(t.id for t in self._transactions if isinstance(t.id, (int, float)))
            return int(max_id) + 1
        except (ValueError, TypeError):
            return 1
    
    def filter_transactions(self, start_date=None, end_date=None, transaction_type=None):
        """Filter transactions by date range and type"""
        filtered = self._transactions
        
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                end = datetime.strptime(end_date, "%Y-%m-%d").date()
                filtered = [t for t in filtered if start <= datetime.strptime(t.date, "%Y-%m-%d").date() <= end]
            except (ValueError, TypeError):
                messagebox.showwarning("Lỗi", "Định dạng ngày không hợp lệ")
        
        if transaction_type and transaction_type != "all":
            filtered = [t for t in filtered if t.get_type() == transaction_type]
            
        return filtered
    
    def get_summary(self, transactions=None):
        """Get summary of transactions"""
        if transactions is None:
            transactions = self._transactions
            
        income = sum(t.amount for t in transactions if t.get_type() == "income")
        expense = sum(t.amount for t in transactions if t.get_type() == "expense")
        balance = income - expense
        
        return {
            "income": income,
            "expense": expense,
            "balance": balance,
            "count": len(transactions)
        }
    
    def export_to_csv(self, filename):
        """Export transactions to CSV file"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'Ngày', 'Mô tả', 'Số tiền', 'Loại', 'Danh mục'])
                
                for t in self._transactions:
                    writer.writerow([
                        t.id, t.date, t.description, t.amount,
                        t.get_display_type(), t.category
                    ])
            return True
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi khi xuất CSV: {str(e)}")
            return False
    
    def export_to_json(self, filename):
        """Export transactions to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                data = [t.to_dict() for t in self._transactions]
                json.dump(data, file, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi khi xuất JSON: {str(e)}")
            return False

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

class TransactionInputView(BaseView):
    """View for transaction input"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self._controller = controller
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up UI components"""
        frame = ttk.LabelFrame(self._frame, text="Thêm giao dịch")
        frame.pack(padx=10, pady=5, fill="x")
        
        # Row 1: Date and Description
        input_row1 = ttk.Frame(frame)
        input_row1.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(input_row1, text="Ngày:").pack(side="left", padx=5)
        self._date_entry = DateEntry(input_row1, width=12, date_pattern='yyyy-mm-dd')
        self._date_entry.pack(side="left", padx=5)
        
        ttk.Label(input_row1, text="Mô tả:").pack(side="left", padx=5)
        self._desc_entry = ttk.Entry(input_row1, width=30)
        self._desc_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Row 2: Amount and Type
        input_row2 = ttk.Frame(frame)
        input_row2.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(input_row2, text="Số tiền (VND):").pack(side="left", padx=5)
        self._amount_entry = ttk.Entry(input_row2, width=15)
        self._amount_entry.pack(side="left", padx=5)
        
        self._type_var = tk.StringVar(value="expense")
        ttk.Radiobutton(input_row2, text="Chi tiêu", value="expense", 
                        variable=self._type_var, command=self._update_category_options).pack(side="left", padx=10)
        ttk.Radiobutton(input_row2, text="Thu nhập", value="income", 
                        variable=self._type_var, command=self._update_category_options).pack(side="left", padx=10)
        
        # Row 3: Category
        input_row3 = ttk.Frame(frame)
        input_row3.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(input_row3, text="Danh mục:").pack(side="left", padx=5)
        self._category_var = tk.StringVar()
        self._category_combobox = ttk.Combobox(input_row3, textvariable=self._category_var, width=20)
        self._category_combobox.pack(side="left", padx=5)
        
        # Add transaction button
        ttk.Button(frame, text="Thêm giao dịch", 
                   command=self._controller.handle_add_transaction).pack(pady=10)
        
        # Initialize combobox values
        self._update_category_options()
    
    def _update_category_options(self):
        """Update category options based on transaction type"""
        categories = (self._controller.transaction_manager.income_categories 
                      if self._type_var.get() == "income" 
                      else self._controller.transaction_manager.expense_categories)
        self._category_combobox["values"] = categories
        self._category_var.set(categories[0] if categories else "Khác")
    
    def get_input_data(self):
        """Get input data from form"""
        return {
            "date": self._date_entry.get(),
            "description": self._desc_entry.get().strip(),
            "amount": self._amount_entry.get().strip(),
            "type": self._type_var.get(),
            "category": self._category_var.get()
        }
    
    def clear_inputs(self):
        """Clear input fields"""
        self._desc_entry.delete(0, tk.END)
        self._amount_entry.delete(0, tk.END)
        
    def update_view(self, data=None):
        """This view doesn't need updating with data"""
        pass

class TransactionListView(BaseView):
    """View for transaction list"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self._controller = controller
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up UI components"""
        frame = ttk.LabelFrame(self._frame, text="Danh sách giao dịch")
        frame.pack(padx=10, pady=5, fill="both", expand=True)
        
        # Treeview with scrollbar
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill="both", expand=True)
        
        tree_scrollbar = ttk.Scrollbar(tree_frame)
        tree_scrollbar.pack(side="right", fill="y")
        
        self._tree = ttk.Treeview(tree_frame, 
                                 columns=("ID", "Date", "Desc", "Amount", "Type", "Category"), 
                                 show="headings", yscrollcommand=tree_scrollbar.set)
        
        self._tree.heading("ID", text="ID")
        self._tree.heading("Date", text="Ngày")
        self._tree.heading("Desc", text="Mô tả")
        self._tree.heading("Amount", text="Số tiền")
        self._tree.heading("Type", text="Loại")
        self._tree.heading("Category", text="Danh mục")
        
        # Adjust column widths
        self._tree.column("ID", width=40)
        self._tree.column("Date", width=100)
        self._tree.column("Desc", width=200)
        self._tree.column("Amount", width=120)
        self._tree.column("Type", width=100)
        self._tree.column("Category", width=120)
        
        self._tree.pack(side="left", fill="both", expand=True)
        tree_scrollbar.config(command=self._tree.yview)
        
        # Action buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill="x", pady=5)
        ttk.Button(button_frame, text="Xóa giao dịch", 
                   command=self._controller.handle_delete_transaction).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Sửa giao dịch", 
                   command=self._controller.handle_edit_transaction).pack(side="left", padx=5)
    
    def get_selected_id(self):
        """Get selected transaction ID"""
        selected = self._tree.selection()
        if not selected:
            return None
        try:
            return int(self._tree.item(selected)["values"][0])
        except (ValueError, IndexError):
            return None
    
    def update_view(self, transactions=None):
        """Update transaction list"""
        if transactions is None:
            transactions = self._controller.transaction_manager.transactions
            
        # Clear current items
        for item in self._tree.get_children():
            self._tree.delete(item)
            
        # Sort transactions by date (newest first)
        try:
            sorted_transactions = sorted(transactions, key=lambda t: datetime.strptime(t.date, "%Y-%m-%d"), reverse=True)
        except (ValueError, TypeError):
            sorted_transactions = transactions
            
        # Insert transactions
        for t in sorted_transactions:
            try:
                self._tree.insert("", tk.END, values=(
                    t.id,
                    t.date,
                    t.description,
                    f"{t.amount:,.0f} VND",
                    t.get_display_type(),
                    t.category
                ))
            except Exception:
                continue

class SummaryView(BaseView):
    """View for financial summary"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self._controller = controller
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up UI components"""
        frame = ttk.LabelFrame(self._frame, text="Tổng quan")
        frame.pack(padx=10, pady=5, fill="x")
        
        self._balance_label = ttk.Label(frame, text="Số dư: 0 VND", font=("Arial", 12, "bold"))
        self._balance_label.pack(anchor="w", padx=5, pady=2)
        
        self._income_label = ttk.Label(frame, text="Thu nhập: 0 VND", font=("Arial", 11))
        self._income_label.pack(anchor="w", padx=5, pady=2)
        
        self._expense_label = ttk.Label(frame, text="Chi tiêu: 0 VND", font=("Arial", 11))
        self._expense_label.pack(anchor="w", padx=5, pady=2)
        
        # Export buttons
        export_frame = ttk.Frame(frame)
        export_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(export_frame, text="Xuất CSV", 
                   command=self._controller.handle_export_csv).pack(side="left", padx=5)
        ttk.Button(export_frame, text="Xuất JSON", 
                   command=self._controller.handle_export_json).pack(side="left", padx=5)
        
        # Logout button
        ttk.Button(export_frame, text="Đăng xuất", 
                   command=self._controller.logout).pack(side="left", padx=5)
    
    def update_view(self, summary=None):
        """Update summary view"""
        if summary is None:
            summary = self._controller.transaction_manager.get_summary()
            
        try:
            self._balance_label.config(text=f"Số dư: {summary['balance']:,.0f} VND")
            self._income_label.config(text=f"Thu nhập: {summary['income']:,.0f} VND")
            self._expense_label.config(text=f"Chi tiêu: {summary['expense']:,.0f} VND")
        except (KeyError, TypeError):
            self._balance_label.config(text="Số dư: 0 VND")
            self._income_label.config(text="Thu nhập: 0 VND")
            self._expense_label.config(text="Chi tiêu: 0 VND")

class StatsView(BaseView):
    """View for statistics and charts"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self._controller = controller
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up UI components"""
        frame = ttk.LabelFrame(self._frame, text="Thống kê chi tiêu và thu nhập")
        frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Date filter frame
        date_filter_frame = ttk.Frame(frame)
        date_filter_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(date_filter_frame, text="Từ ngày:").pack(side="left", padx=5)
        self._from_date = DateEntry(date_filter_frame, width=12, date_pattern='yyyy-mm-dd')
        self._from_date.pack(side="left", padx=5)
        
        ttk.Label(date_filter_frame, text="Đến ngày:").pack(side="left", padx=5)
        self._to_date = DateEntry(date_filter_frame, width=12, date_pattern='yyyy-mm-dd')
        self._to_date.pack(side="left", padx=5)
        
        ttk.Button(date_filter_frame, text="Cập nhật biểu đồ", 
                   command=self._controller.handle_update_charts).pack(side="left", padx=20)
        
        # Charts frame
        charts_frame = ttk.Frame(frame)
        charts_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create matplotlib figure
        self._fig = plt.Figure(figsize=(10, 6), dpi=100)
        self._pie1 = self._fig.add_subplot(121)  # Expenses by category
        self._pie2 = self._fig.add_subplot(122)  # Income vs Expense
        
        # Create Tkinter canvas
        self._canvas = FigureCanvasTkAgg(self._fig, charts_frame)
        self._canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def get_date_range(self):
        """Get selected date range"""
        try:
            return {
                "from_date": self._from_date.get_date().strftime("%Y-%m-%d"),
                "to_date": self._to_date.get_date().strftime("%Y-%m-%d")
            }
        except Exception:
            return {
                "from_date": datetime.now().strftime("%Y-%m-%d"),
                "to_date": datetime.now().strftime("%Y-%m-%d")
            }
    
    def update_view(self, data=None):
        """Update charts with data"""
        if data is None:
            return
            
        # Clear old charts
        self._pie1.clear()
        self._pie2.clear()
        
        # Extract data
        expense_by_category = data.get("expense_by_category", {})
        total_income = data.get("total_income", 0)
        total_expense = data.get("total_expense", 0)
        
        # Chart 1: Expenses by category
        if expense_by_category:
            labels = list(expense_by_category.keys())
            sizes = list(expense_by_category.values())
            
            # Create automatic colors
            colors = plt.cm.tab10(range(len(labels)))
            
            self._pie1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
            self._pie1.axis('equal')
            self._pie1.set_title('Chi tiêu theo danh mục')
        else:
            self._pie1.text(0.5, 0.5, 'Không có dữ liệu chi tiêu', ha='center', va='center')
            self._pie1.axis('off')
        
        # Chart 2: Income vs Expense
        if total_income > 0 or total_expense > 0:
            labels = ['Thu nhập', 'Chi tiêu']
            sizes = [total_income, total_expense]
            colors = ['#55a868', '#c44e52']  # Green for income, red for expense
            
            self._pie2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
            self._pie2.axis('equal')
            self._pie2.set_title('Tỷ lệ thu nhập - chi tiêu')
        else:
            self._pie2.text(0.5, 0.5, 'Không có dữ liệu', ha='center', va='center')
            self._pie2.axis('off')
        
        # Update canvas
        try:
            self._fig.tight_layout()
            self._canvas.draw()
        except Exception:
            pass

class SearchView(BaseView):
    """View for transaction search"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self._controller = controller
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up UI components"""
        # Search criteria frame
        search_frame = ttk.LabelFrame(self._frame, text="Tìm kiếm giao dịch theo thời gian")
        search_frame.pack(padx=10, pady=10, fill="x")
        
        # Row 1: Date range
        date_range_frame = ttk.Frame(search_frame)
        date_range_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(date_range_frame, text="Từ ngày:").pack(side="left", padx=5)
        self._from_date = DateEntry(date_range_frame, width=12, date_pattern='yyyy-mm-dd')
        self._from_date.pack(side="left", padx=5)
        
        ttk.Label(date_range_frame, text="Đến ngày:").pack(side="left", padx=5)
        self._to_date = DateEntry(date_range_frame, width=12, date_pattern='yyyy-mm-dd')
        self._to_date.pack(side="left", padx=5)
        
        # Row 2: Transaction type and search button
        filter_frame = ttk.Frame(search_frame)
        filter_frame.pack(fill="x", padx=5, pady=5)
        
        self._search_type_var = tk.StringVar(value="all")
        ttk.Radiobutton(filter_frame, text="Tất cả", value="all", 
                        variable=self._search_type_var).pack(side="left", padx=5)
        ttk.Radiobutton(filter_frame, text="Chi tiêu", value="expense", 
                        variable=self._search_type_var).pack(side="left", padx=5)
        ttk.Radiobutton(filter_frame, text="Thu nhập", value="income", 
                        variable=self._search_type_var).pack(side="left", padx=5)
        
        ttk.Button(filter_frame, text="Tìm kiếm", 
                   command=self._controller.handle_search).pack(side="left", padx=20)
        
        # Results frame
        result_frame = ttk.LabelFrame(self._frame, text="Kết quả tìm kiếm")
        result_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Treeview with scrollbar
        tree_frame = ttk.Frame(result_frame)
        tree_frame.pack(fill="both", expand=True)
        
        search_scrollbar = ttk.Scrollbar(tree_frame)
        search_scrollbar.pack(side="right", fill="y")
        
        self._search_tree = ttk.Treeview(tree_frame, 
                                        columns=("ID", "Date", "Desc", "Amount", "Type", "Category"), 
                                        show="headings", yscrollcommand=search_scrollbar.set)
        
        self._search_tree.heading("ID", text="ID")
        self._search_tree.heading("Date", text="Ngày")
        self._search_tree.heading("Desc", text="Mô tả")
        self._search_tree.heading("Amount", text="Số tiền")
        self._search_tree.heading("Type", text="Loại")
        self._search_tree.heading("Category", text="Danh mục")
        
        # Adjust column widths
        self._search_tree.column("ID", width=40)
        self._search_tree.column("Date", width=100)
        self._search_tree.column("Desc", width=200)
        self._search_tree.column("Amount", width=120)
        self._search_tree.column("Type", width=100)
        self._search_tree.column("Category", width=120)
        
        self._search_tree.pack(side="left", fill="both", expand=True)
        search_scrollbar.config(command=self._search_tree.yview)
        
        # Summary section
        summary_frame = ttk.Frame(result_frame)
        summary_frame.pack(fill="x", pady=5)
        
        self._total_label = ttk.Label(summary_frame, text="Tổng kết: 0 giao dịch")
        self._total_label.pack(side="left", padx=5)
        
        self._income_label = ttk.Label(summary_frame, text="Thu nhập: 0 VND")
        self._income_label.pack(side="left", padx=20)
        
        self._expense_label = ttk.Label(summary_frame, text="Chi tiêu: 0 VND")
        self._expense_label.pack(side="left", padx=20)
        
        self._balance_label = ttk.Label(summary_frame, text="Chênh lệch: 0 VND")
        self._balance_label.pack(side="left", padx=20)
    
    def get_search_criteria(self):
        """Get search criteria"""
        try:
            return {
                "from_date": self._from_date.get_date().strftime("%Y-%m-%d"),
                "to_date": self._to_date.get_date().strftime("%Y-%m-%d"),
                "type": self._search_type_var.get()
            }
        except Exception:
            return {
                "from_date": datetime.now().strftime("%Y-%m-%d"),
                "to_date": datetime.now().strftime("%Y-%m-%d"),
                "type": "all"
            }
    
    def update_view(self, data=None):
        """Update search results"""
        if data is None:
            return
            
        transactions = data.get("transactions", [])
        summary = data.get("summary", {})
        
        # Clear current items
        for item in self._search_tree.get_children():
            self._search_tree.delete(item)
        
        # Display new results
        for t in sorted(transactions, key=lambda t: t.date, reverse=True):
            try:
                self._search_tree.insert("", tk.END, values=(
                    t.id,
                    t.date,
                    t.description,
                    f"{t.amount:,.0f} VND",
                    t.get_display_type(),
                    t.category
                ))
            except Exception:
                continue
        
        # Update summary
        try:
            self._total_label.config(text=f"Tổng kết: {summary['count']} giao dịch")
            self._income_label.config(text=f"Thu nhập: {summary['income']:,.0f} VND")
            self._expense_label.config(text=f"Chi tiêu: {summary['expense']:,.0f} VND")
            self._balance_label.config(text=f"Chênh lệch: {summary['balance']:,.0f} VND")
        except (KeyError, TypeError):
            self._total_label.config(text="Tổng kết: 0 giao dịch")
            self._income_label.config(text="Thu nhập: 0 VND")
            self._expense_label.config(text="Chi tiêu: 0 VND")
            self._balance_label.config(text="Chênh lệch: 0 VND")

class TransactionEditDialog:
    """Dialog for editing a transaction"""
    def __init__(self, parent, transaction, transaction_manager, callback):
        self._parent = parent
        self._transaction = transaction
        self._transaction_manager = transaction_manager
        self._callback = callback
        self._create_dialog()
    
    def _create_dialog(self):
        """Create the edit dialog UI"""
        self._dialog = tk.Toplevel(self._parent)
        self._dialog.title("Sửa giao dịch")
        self._dialog.geometry("400x300")
        self._dialog.transient(self._parent)
        self._dialog.grab_set()
        
        # Date
        ttk.Label(self._dialog, text="Ngày:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self._date_entry = DateEntry(self._dialog, width=12, date_pattern='yyyy-mm-dd')
        self._date_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        try:
            self._date_entry.set_date(datetime.strptime(self._transaction.date, "%Y-%m-%d"))
        except (ValueError, TypeError):
            self._date_entry.set_date(datetime.now())
        
        # Description
        ttk.Label(self._dialog, text="Mô tả:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self._desc_entry = ttk.Entry(self._dialog, width=30)
        self._desc_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self._desc_entry.insert(0, self._transaction.description)
        
        # Amount
        ttk.Label(self._dialog, text="Số tiền:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self._amount_entry = ttk.Entry(self._dialog, width=15)
        self._amount_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self._amount_entry.insert(0, str(self._transaction.amount))
        
        # Type
        ttk.Label(self._dialog, text="Loại:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self._type_var = tk.StringVar(value=self._transaction.get_type())
        type_frame = ttk.Frame(self._dialog)
        type_frame.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        ttk.Radiobutton(type_frame, text="Chi tiêu", value="expense", 
                        variable=self._type_var, command=self._update_categories).pack(side="left", padx=5)
        ttk.Radiobutton(type_frame, text="Thu nhập", value="income", 
                        variable=self._type_var, command=self._update_categories).pack(side="left", padx=5)
        
        # Category
        ttk.Label(self._dialog, text="Danh mục:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self._category_var = tk.StringVar(value=self._transaction.category)
        self._category_combobox = ttk.Combobox(self._dialog, textvariable=self._category_var)
        self._category_combobox.grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        self._update_categories()
        
        # Buttons
        button_frame = ttk.Frame(self._dialog)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="Lưu thay đổi", command=self._save_changes).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Hủy bỏ", command=self._dialog.destroy).pack(side="left", padx=10)
        
        # Center the dialog
        self._dialog.update_idletasks()
        width = self._dialog.winfo_width()
        height = self._dialog.winfo_height()
        x = (self._parent.winfo_screenwidth() // 2) - (width // 2)
        y = (self._parent.winfo_screenheight() // 2) - (height // 2)
        self._dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def _update_categories(self):
        """Update category options based on transaction type"""
        categories = (self._transaction_manager.income_categories 
                      if self._type_var.get() == "income" 
                      else self._transaction_manager.expense_categories)
        if self._transaction.category not in categories:
            categories = categories + [self._transaction.category]
        self._category_combobox["values"] = categories
        self._category_var.set(self._transaction.category)
    
    def _save_changes(self):
        """Save changes to the transaction"""
        try:
            amount = float(self._amount_entry.get().strip())
            if amount <= 0:
                raise ValueError("Số tiền phải lớn hơn 0")
                
            description = self._desc_entry.get().strip()
            if not description:
                raise ValueError("Mô tả không được để trống")
                
            transaction_data = {
                "id": self._transaction.id,
                "date": self._date_entry.get(),
                "description": description,
                "amount": amount,
                "category": self._category_var.get()
            }
            
            # Create new transaction object
            new_transaction = (IncomeTransaction(**transaction_data) 
                              if self._type_var.get() == "income" 
                              else ExpenseTransaction(**transaction_data))
            
            # Update transaction in manager
            if self._transaction_manager.update_transaction(new_transaction):
                self._callback()
                self._dialog.destroy()
            else:
                messagebox.showerror("Lỗi", "Không thể cập nhật giao dịch", parent=self._dialog)
                
        except ValueError as e:
            messagebox.showwarning("Lỗi", str(e), parent=self._dialog)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}", parent=self._dialog)

class Controller:
    """Controller to manage interactions between model and views"""
    def __init__(self, root, username):
        self.transaction_manager = TransactionManager()
        self.root = root
        self.username = username
        self.root.title("Quản Lý Chi Tiêu")
        self.root.geometry("900x700")
        
        # Setup notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create tabs
        self.main_tab = ttk.Frame(self.notebook)
        self.stats_tab = ttk.Frame(self.notebook)
        self.search_tab = ttk.Frame(self.notebook)
        self.user_info_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.main_tab, text="Tổng quan")
        self.notebook.add(self.stats_tab, text="Thống kê")
        self.notebook.add(self.search_tab, text="Tìm kiếm")
        self.notebook.add(self.user_info_tab, text="Thông Tin Người Dùng")
        
        # Initialize views
        self.input_view = TransactionInputView(self.main_tab, self)
        self.summary_view = SummaryView(self.main_tab, self)
        self.list_view = TransactionListView(self.main_tab, self)
        self.stats_view = StatsView(self.stats_tab, self)
        self.search_view = SearchView(self.search_tab, self)
        from UserInfo import UserInfoView
        self.user_info_view = UserInfoView(self.user_info_tab, self, self.username)
        
        # Layout views in main tab
        self.summary_view.pack(fill="x")
        self.input_view.pack(fill="x")
        self.list_view.pack(fill="both", expand=True)
        
        # Layout views in other tabs
        self.stats_view.pack(fill="both", expand=True)
        self.search_view.pack(fill="both", expand=True)
        self.user_info_view.pack(fill="both", expand=True)
        
        # Initial update
        self.update_all_views()
    
    def logout(self):
        """Đóng cửa sổ hiện tại và mở lại cửa sổ đăng nhập"""
        self.root.destroy()
        from Login import LoginApp
        root = tk.Tk()
        app = LoginApp(root)
        root.mainloop()
    
    def update_all_views(self):
        """Update all views with current data"""
        try:
            self.summary_view.update_view()
            self.list_view.update_view()
            self.stats_view.update_view(self._get_stats_data())
            self.search_view.update_view()
            self.user_info_view.update_view()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật giao diện: {str(e)}")
    
    def handle_add_transaction(self):
        """Handle adding a new transaction"""
        data = self.input_view.get_input_data()
        
        if not data["description"] or not data["amount"]:
            messagebox.showwarning("Lỗi", "Hãy nhập đầy đủ thông tin!")
            return
            
        try:
            amount = float(data["amount"])
            if amount <= 0:
                raise ValueError("Số tiền phải lớn hơn 0")
                
            datetime.strptime(data["date"], "%Y-%m-%d")  # Validate date
            
            transaction_data = {
                "id": self.transaction_manager.get_next_id(),
                "date": data["date"],
                "description": data["description"],
                "amount": amount,
                "category": data["category"]
            }
            
            transaction = (IncomeTransaction(**transaction_data) 
                          if data["type"] == "income" 
                          else ExpenseTransaction(**transaction_data))
            
            if self.transaction_manager.add_transaction(transaction):
                self.input_view.clear_inputs()
                self.update_all_views()
                messagebox.showinfo("Thành công", "Giao dịch đã được thêm!")
            else:
                messagebox.showerror("Lỗi", "Không thể thêm giao dịch")
                
        except ValueError as e:
            messagebox.showwarning("Lỗi", str(e))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
    
    def handle_delete_transaction(self):
        """Handle deleting a transaction"""
        transaction_id = self.list_view.get_selected_id()
        if not transaction_id:
            messagebox.showwarning("Lỗi", "Hãy chọn giao dịch để xóa!")
            return
            
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa giao dịch này?"):
            if self.transaction_manager.delete_transaction(transaction_id):
                self.update_all_views()
                messagebox.showinfo("Thành công", "Giao dịch đã được xóa!")
            else:
                messagebox.showerror("Lỗi", "Không thể xóa giao dịch")
    
    def handle_edit_transaction(self):
        """Handle editing a transaction"""
        transaction_id = self.list_view.get_selected_id()
        if not transaction_id:
            messagebox.showwarning("Lỗi", "Hãy chọn giao dịch để sửa!")
            return
            
        transaction = self.transaction_manager.get_transaction_by_id(transaction_id)
        if transaction:
            try:
                TransactionEditDialog(self.root, transaction, self.transaction_manager, self.update_all_views)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể mở cửa sổ chỉnh sửa: {str(e)}")
    
    def handle_search(self):
        """Handle transaction search"""
        try:
            criteria = self.search_view.get_search_criteria()
            transactions = self.transaction_manager.filter_transactions(
                criteria["from_date"],
                criteria["to_date"],
                criteria["type"]
            )
            summary = self.transaction_manager.get_summary(transactions)
            self.search_view.update_view({
                "transactions": transactions,
                "summary": summary
            })
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thực hiện tìm kiếm: {str(e)}")
    
    def handle_export_csv(self):
        """Handle exporting to CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")],
                title="Xuất dữ liệu sang CSV"
            )
            if filename and self.transaction_manager.export_to_csv(filename):
                messagebox.showinfo("Thành công", "Dữ liệu đã được xuất thành công!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi khi xuất CSV: {str(e)}")
    
    def handle_export_json(self):
        """Handle exporting to JSON"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json")],
                title="Xuất dữ liệu sang JSON"
            )
            if filename and self.transaction_manager.export_to_json(filename):
                messagebox.showinfo("Thành công", "Dữ liệu đã được xuất thành công!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi khi xuất JSON: {str(e)}")
    
    def handle_update_charts(self):
        """Handle updating statistics charts"""
        try:
            self.stats_view.update_view(self._get_stats_data())
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật biểu đồ: {str(e)}")
    
    def _get_stats_data(self):
        """Get data for statistics charts"""
        try:
            date_range = self.stats_view.get_date_range()
            transactions = self.transaction_manager.filter_transactions(
                date_range["from_date"],
                date_range["to_date"]
            )
            
            expense_by_category = {}
            for t in transactions:
                if t.get_type() == "expense":
                    expense_by_category[t.category] = expense_by_category.get(t.category, 0) + t.amount
            
            # Sort and limit to top 5 categories
            top_expenses = dict(sorted(expense_by_category.items(), key=lambda x: x[1], reverse=True)[:5])
            if len(expense_by_category) > 5:
                others_sum = sum(v for k, v in expense_by_category.items() if k not in top_expenses)
                if others_sum > 0:
                    top_expenses["Khác"] = others_sum
            
            total_income = sum(t.amount for t in transactions if t.get_type() == "income")
            total_expense = sum(t.amount for t in transactions if t.get_type() == "expense")
            
            return {
                "expense_by_category": top_expenses,
                "total_income": total_income,
                "total_expense": total_expense
            }
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo dữ liệu thống kê: {str(e)}")
            return {
                "expense_by_category": {},
                "total_income": 0,
                "total_expense": 0
            }

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = Controller(root, "test_user")
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Lỗi", f"Ứng dụng không thể khởi động: {str(e)}")