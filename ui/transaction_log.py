"""
Transaction Log UI component for displaying purchase and sales transaction history.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from ui.base import BaseUIComponent
from database.stock_data import load_log
from utils.file_utils import get_log_file_path
from config.colors import *


class TransactionLogUI(BaseUIComponent):
    """Transaction Log interface component."""
    
    def __init__(self, parent, stock_app_ref):
        super().__init__(parent, stock_app_ref)
        self.frame = self.create_frame()
        self.create_widgets()
    
    def create_widgets(self):
        """Create transaction log widgets."""
        # Title
        ttk.Label(self.frame, text="Transaction Log", style='SubHeader.TLabel').pack(pady=(0, 18))
        
        # Transaction log table with detailed pricing
        self.transaction_tree = ttk.Treeview(self.frame, 
            columns=("Date", "Type", "Product ID", "Product Name", "Carton ID", "Quantity", "Purchase Price", "Sales Price", "MRP", "Purchase Value (₹)", "Sales Value (₹)", "Profit/Loss (₹)"), 
            show='headings', height=15)
        
        # Configure columns with optimized widths to fit screen
        for col, width in zip(("Date", "Type", "Product ID", "Product Name", "Carton ID", "Quantity", "Purchase Price", "Sales Price", "MRP", "Purchase Value (₹)", "Sales Value (₹)", "Profit/Loss (₹)"), 
                             [90, 70, 80, 120, 80, 60, 80, 80, 70, 100, 100, 100]):
            self.transaction_tree.heading(col, text=col)
            self.transaction_tree.column(col, width=width, anchor='center')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.transaction_tree.yview)
        self.transaction_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbars with proper frame
        tree_frame = ttk.Frame(self.frame)
        tree_frame.pack(expand=True, fill='both', pady=10)
        
        # Add horizontal scrollbar for wide table
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.transaction_tree.xview)
        self.transaction_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Pack layout for scrollbars and tree
        h_scrollbar.pack(side='bottom', fill='x')
        scrollbar.pack(side='right', fill='y')
        self.transaction_tree.pack(side='left', expand=True, fill='both')
        
        # Buttons
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Refresh", command=self.update_transaction_log).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Export to CSV", command=self.export_transaction_log_csv).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Clear Logs", command=self.clear_transaction_logs).pack(side='left', padx=5)
        
        # Initial data load
        self.update_transaction_log()
    
    def update_transaction_log(self):
        """Update the transaction log display."""
        # Clear existing data
        for item in self.transaction_tree.get_children():
            self.transaction_tree.delete(item)
        
        try:
            # Load both purchase and sales logs
            purchase_log_file = get_log_file_path(self.stock_app.selected_json_file, 'purchase')
            sales_log_file = get_log_file_path(self.stock_app.selected_json_file, 'sales')
            
            purchase_log = load_log(purchase_log_file)
            sales_log = load_log(sales_log_file)
            
            # Combine and sort all transactions by date
            all_transactions = []
            
            # Add purchase transactions
            for entry in purchase_log:
                all_transactions.append({
                    'date': entry.get('date', ''),
                    'type': 'Purchase',
                    'product_id': entry.get('product_id', ''),
                    'product_name': entry.get('product_name', ''),
                    'carton_id': entry.get('carton_id', ''),
                    'quantity': entry.get('quantity', 0),
                    'purchase_price': entry.get('purchase_price', 0),
                    'sales_price': entry.get('sales_price', 0),
                    'mrp': entry.get('mrp', 0),
                    'purchase_value': entry.get('purchase_value', 0),
                    'sales_value': entry.get('sales_value', 0),
                    'profit_loss': 0  # No profit/loss for purchases
                })
            
            # Add sales transactions
            for entry in sales_log:
                purchase_value = entry.get('purchase_value', 0)
                sales_value = entry.get('sales_value', 0)
                profit_loss = sales_value - purchase_value
                all_transactions.append({
                    'date': entry.get('date', ''),
                    'type': 'Sale',
                    'product_id': entry.get('product_id', ''),
                    'product_name': entry.get('product_name', ''),
                    'carton_id': entry.get('carton_id', ''),
                    'quantity': entry.get('quantity', 0),
                    'purchase_price': entry.get('purchase_price', 0),
                    'sales_price': entry.get('sales_price', 0),
                    'mrp': entry.get('mrp', 0),
                    'purchase_value': purchase_value,
                    'sales_value': sales_value,
                    'profit_loss': profit_loss
                })
            
            # Sort by date (newest first)
            all_transactions.sort(key=lambda x: x['date'], reverse=True)
            
            # Insert data into tree
            for trans in all_transactions:
                purchase_display = f"₹{trans['purchase_value']:.2f}" if trans['purchase_value'] > 0 else "N/A"
                sales_display = f"₹{trans['sales_value']:.2f}" if trans['sales_value'] > 0 else "N/A"
                
                if trans['type'] == 'Purchase':
                    profit_display = "N/A"  # No profit/loss for purchases
                else:
                    profit_loss = trans['profit_loss']
                    if profit_loss > 0:
                        profit_display = f"🟢 ₹{profit_loss:.2f}"
                    elif profit_loss < 0:
                        profit_display = f"🔴 ₹{abs(profit_loss):.2f}"
                    else:
                        profit_display = f"⚪ ₹{profit_loss:.2f}"
                
                self.transaction_tree.insert('', 'end', values=(
                    trans['date'],
                    trans['type'],
                    trans['product_id'],
                    trans['product_name'],
                    trans['carton_id'],
                    trans['quantity'],
                    f"₹{trans.get('purchase_price', 0):.2f}",
                    f"₹{trans.get('sales_price', 0):.2f}",
                    f"₹{trans.get('mrp', 0):.2f}" if trans.get('mrp', 0) > 0 else 'N/A',
                    purchase_display,
                    sales_display,
                    profit_display
                ))
            
            total_transactions = len(all_transactions)
            messagebox.showinfo('Success', f'Transaction log updated. Total transactions: {total_transactions}')
            
        except Exception as e:
            messagebox.showerror('Error', f'Error updating transaction log: {str(e)}')
    
    def export_transaction_log_csv(self):
        """Export transaction log to CSV file."""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Export Transaction Log",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")]
            )
            
            if not file_path:
                return
            
            # Get data from tree
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(["Date", "Type", "Product ID", "Product Name", "Carton ID", "Quantity", "Purchase Price", "Sales Price", "MRP", "Purchase Value (₹)", "Sales Value (₹)", "Profit/Loss (₹)"])
                
                # Write data
                for item in self.transaction_tree.get_children():
                    values = self.transaction_tree.item(item)['values']
                    writer.writerow(values)
            
            messagebox.showinfo('Success', f'Transaction log exported to {file_path}')
            
        except Exception as e:
            messagebox.showerror('Error', f'Error exporting transaction log: {str(e)}')
    
    def clear_transaction_logs(self):
        """Clear all transaction logs."""
        if not messagebox.askyesno("Confirm Clear", "Are you sure you want to CLEAR all transaction logs? This cannot be undone."):
            return
        
        try:
            # Clear both purchase and sales logs
            import json
            purchase_log_file = get_log_file_path(self.stock_app.selected_json_file, 'purchase')
            sales_log_file = get_log_file_path(self.stock_app.selected_json_file, 'sales')
            
            with open(purchase_log_file, 'w') as f:
                json.dump([], f)
            with open(sales_log_file, 'w') as f:
                json.dump([], f)
            
            self.update_transaction_log()
            messagebox.showinfo('Success', 'All transaction logs cleared.')
            
        except Exception as e:
            messagebox.showerror('Error', f'Error clearing transaction logs: {str(e)}')