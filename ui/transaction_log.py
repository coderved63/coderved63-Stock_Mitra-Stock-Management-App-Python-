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
        
        # Transaction log table
        self.transaction_tree = ttk.Treeview(self.frame, 
            columns=("Date", "Type", "Product ID", "Product Name", "Carton ID", "Quantity", "Value (₹)"), 
            show='headings', height=15)
        
        # Configure columns
        for col, width in zip(("Date", "Type", "Product ID", "Product Name", "Carton ID", "Quantity", "Value (₹)"), 
                             [120, 80, 100, 180, 100, 80, 120]):
            self.transaction_tree.heading(col, text=col)
            self.transaction_tree.column(col, width=width, anchor='center')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.transaction_tree.yview)
        self.transaction_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        tree_frame = ttk.Frame(self.frame)
        tree_frame.pack(expand=True, fill='both', pady=10)
        self.transaction_tree.pack(side='left', expand=True, fill='both')
        scrollbar.pack(side='right', fill='y')
        
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
                    'value': entry.get('purchase_value', entry.get('sales_value', 0))
                })
            
            # Add sales transactions
            for entry in sales_log:
                all_transactions.append({
                    'date': entry.get('date', ''),
                    'type': 'Sale',
                    'product_id': entry.get('product_id', ''),
                    'product_name': entry.get('product_name', ''),
                    'carton_id': entry.get('carton_id', ''),
                    'quantity': entry.get('quantity', 0),
                    'value': entry.get('sales_value', 0)
                })
            
            # Sort by date (newest first)
            all_transactions.sort(key=lambda x: x['date'], reverse=True)
            
            # Insert data into tree
            for trans in all_transactions:
                self.transaction_tree.insert('', 'end', values=(
                    trans['date'],
                    trans['type'],
                    trans['product_id'],
                    trans['product_name'],
                    trans['carton_id'],
                    trans['quantity'],
                    f"₹{trans['value']:.2f}"
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
                writer.writerow(["Date", "Type", "Product ID", "Product Name", "Carton ID", "Quantity", "Value (₹)"])
                
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