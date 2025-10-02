"""
Sales Summary UI component for displaying sales reports and analytics.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import datetime
import os
from ui.base import BaseUIComponent
from database.stock_data import load_log
from utils.file_utils import get_log_file_path
from config.colors import *


class SalesSummaryUI(BaseUIComponent):
    """Sales Summary interface component."""
    
    def __init__(self, parent, stock_app_ref):
        super().__init__(parent, stock_app_ref)
        self.frame = self.create_frame()
        self.sales_chart_canvas = None
        self.sales_pie_canvas = None
        self.create_widgets()
    
    def create_widgets(self):
        """Create sales summary widgets."""
        # Title
        ttk.Label(self.frame, text="Sales Summary & Profit Analysis", style='SubHeader.TLabel').pack(pady=(0, 18))
        
        # Overall summary frame
        summary_frame = ttk.LabelFrame(self.frame, text="Business Performance Overview", padding="10")
        summary_frame.pack(fill='x', padx=5, pady=(0, 10))
        
        # Create summary labels
        summary_left = ttk.Frame(summary_frame)
        summary_left.pack(side='left', fill='x', expand=True)
        summary_right = ttk.Frame(summary_frame)
        summary_right.pack(side='right', fill='x', expand=True)
        
        self.total_sales_label = ttk.Label(summary_left, text="Total Sales: ₹0.00", font=('Segoe UI', 12, 'bold'))
        self.total_sales_label.pack(anchor='w')
        self.total_purchase_label = ttk.Label(summary_left, text="Total Purchase: ₹0.00", font=('Segoe UI', 12))
        self.total_purchase_label.pack(anchor='w')
        
        self.total_profit_label = ttk.Label(summary_right, text="Total Profit: ₹0.00", font=('Segoe UI', 12, 'bold'))
        self.total_profit_label.pack(anchor='w')
        self.profit_margin_label = ttk.Label(summary_right, text="Profit Margin: 0.0%", font=('Segoe UI', 12))
        self.profit_margin_label.pack(anchor='w')
        
        # Sales summary table with profit/loss columns
        self.sales_summary_tree = ttk.Treeview(self.frame, 
            columns=("Month", "Product ID", "Product Name", "Units Sold", "Sales Value (₹)", "Purchase Value (₹)", "Profit/Loss (₹)", "Profit Margin (%)"), 
            show='headings', height=10)
        
        # Configure columns
        for col, width in zip(("Month", "Product ID", "Product Name", "Units Sold", "Sales Value (₹)", "Purchase Value (₹)", "Profit/Loss (₹)", "Profit Margin (%)"), 
                             [80, 100, 180, 80, 120, 120, 120, 100]):
            self.sales_summary_tree.heading(col, text=col)
            self.sales_summary_tree.column(col, width=width, anchor='center')
        
        self.sales_summary_tree.pack(expand=True, fill='both', pady=10)
        
        # Buttons
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Refresh", command=self.update_sales_summary).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Clear Sales Summary", command=self.clear_sales_summary).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Export to PDF", command=self.export_sales_summary_pdf).pack(side='left', padx=5)
        
        # Initial data load
        self.update_sales_summary()
    
    def update_sales_summary(self):
        """Update the sales summary display."""
        # Clear existing data
        for item in self.sales_summary_tree.get_children():
            self.sales_summary_tree.delete(item)
        
        try:
            # Load sales log
            sales_log_file = get_log_file_path(self.stock_app.selected_json_file, 'sales')
            sales_log = load_log(sales_log_file)
            
            if not sales_log:
                messagebox.showinfo('Info', 'No sales data found.')
                return
            
            # Group sales by month and product
            monthly_sales = {}
            
            for entry in sales_log:
                if entry.get('type') == 'sale':
                    date_str = entry.get('date', '')
                    if date_str:
                        month = date_str[:7]  # Extract YYYY-MM
                        product_id = entry.get('product_id', '')
                        product_name = entry.get('product_name', '')
                        quantity = entry.get('quantity', 0)
                        sales_value = entry.get('sales_value', 0)
                        purchase_value = entry.get('purchase_value', 0)
                        
                        key = (month, product_id, product_name)
                        if key in monthly_sales:
                            monthly_sales[key]['quantity'] += quantity
                            monthly_sales[key]['sales_value'] += sales_value
                            monthly_sales[key]['purchase_value'] += purchase_value
                        else:
                            monthly_sales[key] = {
                                'quantity': quantity,
                                'sales_value': sales_value,
                                'purchase_value': purchase_value
                            }
            
            # Insert data into tree with profit/loss calculations
            for (month, product_id, product_name), data in sorted(monthly_sales.items()):
                sales_value = data['sales_value']
                purchase_value = data['purchase_value']
                profit_loss = sales_value - purchase_value
                
                # Calculate profit margin percentage
                if purchase_value > 0:
                    profit_margin = (profit_loss / purchase_value) * 100
                else:
                    profit_margin = 0
                
                # Color coding for profit/loss
                profit_loss_display = f"₹{profit_loss:.2f}"
                margin_display = f"{profit_margin:.1f}%"
                
                item = self.sales_summary_tree.insert('', 'end', values=(
                    month,
                    product_id,
                    product_name,
                    data['quantity'],
                    f"₹{sales_value:.2f}",
                    f"₹{purchase_value:.2f}",
                    profit_loss_display,
                    margin_display
                ))
                
                # Color coding for profit/loss (green for profit, red for loss)
                if profit_loss > 0:
                    self.sales_summary_tree.set(item, "Profit/Loss (₹)", f"🟢 {profit_loss_display}")
                elif profit_loss < 0:
                    self.sales_summary_tree.set(item, "Profit/Loss (₹)", f"🔴 {profit_loss_display}")
                else:
                    self.sales_summary_tree.set(item, "Profit/Loss (₹)", f"⚪ {profit_loss_display}")
            
            # Update summary totals
            self.update_summary_totals(monthly_sales)
            
            messagebox.showinfo('Success', 'Sales summary updated successfully.')
            
        except Exception as e:
            messagebox.showerror('Error', f'Error updating sales summary: {str(e)}')
    
    def update_summary_totals(self, monthly_sales):
        """Update the summary totals display."""
        total_sales = sum(data['sales_value'] for data in monthly_sales.values())
        total_purchase = sum(data['purchase_value'] for data in monthly_sales.values())
        total_profit = total_sales - total_purchase
        profit_margin = (total_profit / total_purchase * 100) if total_purchase > 0 else 0
        
        # Update labels
        self.total_sales_label.config(text=f"Total Sales: ₹{total_sales:,.2f}")
        self.total_purchase_label.config(text=f"Total Purchase: ₹{total_purchase:,.2f}")
        
        # Color coding for profit/loss
        if total_profit > 0:
            self.total_profit_label.config(text=f"Total Profit: 🟢 ₹{total_profit:,.2f}", foreground="#059669")
            self.profit_margin_label.config(text=f"Profit Margin: {profit_margin:.1f}%", foreground="#059669")
        elif total_profit < 0:
            self.total_profit_label.config(text=f"Total Loss: 🔴 ₹{abs(total_profit):,.2f}", foreground="#dc2626")
            self.profit_margin_label.config(text=f"Loss Margin: {abs(profit_margin):.1f}%", foreground="#dc2626")
        else:
            self.total_profit_label.config(text=f"Break-even: ⚪ ₹{total_profit:,.2f}", foreground="#6b7280")
            self.profit_margin_label.config(text=f"Margin: {profit_margin:.1f}%", foreground="#6b7280")
    
    def clear_sales_summary(self):
        """Clear the sales summary data."""
        if not messagebox.askyesno("Confirm Clear", "Are you sure you want to CLEAR the entire sales summary? This cannot be undone."):
            return
        
        try:
            sales_log_file = get_log_file_path(self.stock_app.selected_json_file, 'sales')
            with open(sales_log_file, 'w') as f:
                json.dump([], f)
            self.update_sales_summary()
            messagebox.showinfo('Success', 'Sales summary cleared.')
        except Exception as e:
            messagebox.showerror('Error', f'Error clearing sales summary: {str(e)}')
    
    def export_sales_summary_pdf(self):
        """Export sales summary to PDF."""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.lib import colors
        except ImportError:
            messagebox.showerror('Error', 'reportlab is not installed. Please install it with "pip install reportlab".')
            return
        
        # Get file path to save PDF
        file_path = filedialog.asksaveasfilename(
            defaultextension='.pdf', 
            filetypes=[('PDF files', '*.pdf')], 
            title='Export Sales Summary PDF'
        )
        if not file_path:
            return
        
        try:
            # Gather table data from the treeview
            table_data = [("Month", "Product ID", "Product Name", "Units Sold", "Sales Value (₹)", "Purchase Value (₹)", "Profit/Loss (₹)", "Profit Margin (%)")]
            for row in self.sales_summary_tree.get_children():
                table_data.append(self.sales_summary_tree.item(row)['values'])
            
            # Create PDF
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            y = height - 40
            
            # Title
            c.setFont("Helvetica-Bold", 18)
            c.drawString(40, y, f"Stock Mitra - Sales Summary Report")
            
            # Company and date info
            c.setFont("Helvetica", 12)
            y -= 25
            c.drawString(40, y, f"Company: {self.stock_app.selected_company}")
            c.drawString(350, y, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
            # Table title
            y -= 30
            c.setFont("Helvetica-Bold", 14)
            c.drawString(40, y, "Monthly Sales Summary Table:")
            y -= 20
            
            # Draw table
            col_widths = [60, 80, 120, 60, 80, 80, 80, 70]
            for i, row in enumerate(table_data):
                for j, val in enumerate(row):
                    c.setFont("Helvetica-Bold" if i == 0 else "Helvetica", 8)
                    c.setFillColor(colors.black if i == 0 else colors.darkblue)
                    c.drawString(40 + sum(col_widths[:j]), y, str(val))
                y -= 18
                if y < 120:  # Start new page if running out of space
                    c.showPage()
                    y = height - 40
            
            # Add summary statistics
            y -= 30
            c.setFont("Helvetica-Bold", 14)
            c.drawString(40, y, "Summary Statistics:")
            y -= 20
            
            # Calculate totals
            total_units = 0
            total_sales = 0.0
            total_purchase = 0.0
            total_profit = 0.0
            for row in self.sales_summary_tree.get_children():
                values = self.sales_summary_tree.item(row)['values']
                total_units += int(values[3])
                # Remove ₹ symbol and convert to float
                sales_str = str(values[4]).replace('₹', '').replace(',', '')
                purchase_str = str(values[5]).replace('₹', '').replace(',', '')
                profit_str = str(values[6]).replace('₹', '').replace(',', '')
                total_sales += float(sales_str)
                total_purchase += float(purchase_str)
                total_profit += float(profit_str)
            
            # Calculate overall profit margin
            overall_margin = (total_profit / total_purchase * 100) if total_purchase > 0 else 0
            
            c.setFont("Helvetica", 12)
            c.drawString(40, y, f"Total Units Sold: {total_units}")
            y -= 20
            c.drawString(40, y, f"Total Sales Value: ₹{total_sales:,.2f}")
            y -= 20
            c.drawString(40, y, f"Total Purchase Value: ₹{total_purchase:,.2f}")
            y -= 20
            c.drawString(40, y, f"Total Profit/Loss: ₹{total_profit:,.2f}")
            y -= 20
            c.drawString(40, y, f"Overall Profit Margin: {overall_margin:.1f}%")
            y -= 20
            c.drawString(40, y, f"Total Products: {len(table_data) - 1}")  # -1 for header
            
            c.save()
            messagebox.showinfo('Success', f'Sales summary exported to {file_path}')
            
        except Exception as e:
            messagebox.showerror('Error', f'Error exporting PDF: {str(e)}')