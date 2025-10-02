"""
Sell Stock UI component for processing stock sales.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from ui.base import BaseUIComponent
from services.stock_search import _get_product_for_action, get_product_summary_text
from database.stock_data import save_stock_data, append_log_entry
from utils.file_utils import get_log_file_path
from utils.date_utils import format_date
from config.colors import *


class SellStockUI(BaseUIComponent):
    """Sell Stock interface component."""
    
    def __init__(self, parent, stock_app_ref):
        super().__init__(parent, stock_app_ref)
        self.frame = self.create_frame()
        self.identified_product_id_for_sale = None
        self.sell_stock_suggestion_window = None
        self.sell_stock_suggestion_listbox = None
        self.create_widgets()
    
    def create_widgets(self):
        """Create sell stock widgets."""
        # Title
        ttk.Label(self.frame, text="Sell Stock", style='SubHeader.TLabel').pack(pady=10)
        
        # Product identification
        product_id_frame = ttk.Frame(self.frame)
        product_id_frame.pack(pady=5)
        ttk.Label(product_id_frame, text="Product ID or Name:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.sell_product_query_entry = ttk.Entry(product_id_frame, width=40)
        self.sell_product_query_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.sell_product_query_entry.bind("<Return>", lambda event: self.identify_product_for_sale())
        ttk.Button(product_id_frame, text="Find Product", command=self.identify_product_for_sale).grid(row=0, column=2, padx=5, pady=5)
        
        # Product summary
        self.sell_product_summary_text = tk.Text(self.frame, height=5, width=70, wrap=tk.WORD, 
                                               font=('Segoe UI', 10), bg=ACCENT_COLOR, fg=LABEL_FG, relief='flat')
        self.sell_product_summary_text.pack(pady=5, padx=5, fill='x')
        self.sell_product_summary_text.config(state=tk.DISABLED)
        
        # Quantities to sell
        self.sell_quantity_frame = ttk.LabelFrame(self.frame, text="Quantities to Sell", padding="10")
        self.sell_quantity_frame.pack(fill='x', padx=5, pady=10)
        
        ttk.Label(self.sell_quantity_frame, text="Full Cartons:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.sell_num_full_cartons_entry = ttk.Entry(self.sell_quantity_frame)
        self.sell_num_full_cartons_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.sell_num_full_cartons_entry.insert(0, "0")
        
        ttk.Label(self.sell_quantity_frame, text="Loose Pieces:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.sell_num_loose_pieces_entry = ttk.Entry(self.sell_quantity_frame)
        self.sell_num_loose_pieces_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        self.sell_num_loose_pieces_entry.insert(0, "0")
        
        self.sell_quantity_frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_sell_stock_form).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Process Sale", command=self.perform_sell_stock).grid(row=0, column=1, padx=5)
    
    def identify_product_for_sale(self):
        """Identify product for sale."""
        query = self.sell_product_query_entry.get().strip()
        if not query:
            messagebox.showerror('Error', 'Please enter a product ID or name to identify.')
            return
        
        all_stock_data_combined = self.stock_app.stock_data
        product_id, product_name, message = _get_product_for_action(query, all_stock_data_combined)
        
        if product_id:
            self.identified_product_id_for_sale = product_id
            summary_text = get_product_summary_text(product_id, all_stock_data_combined)
            self.sell_product_summary_text.config(state=tk.NORMAL)
            self.sell_product_summary_text.delete(1.0, tk.END)
            self.sell_product_summary_text.insert(tk.END, summary_text)
            self.sell_product_summary_text.config(state=tk.DISABLED)
            messagebox.showinfo('Info', f"Product identified: {product_name} ({product_id}). Ready to sell.")
        else:
            self.identified_product_id_for_sale = None
            self.sell_product_summary_text.config(state=tk.NORMAL)
            self.sell_product_summary_text.delete(1.0, tk.END)
            self.sell_product_summary_text.insert(tk.END, message)
            self.sell_product_summary_text.config(state=tk.DISABLED)
            messagebox.showerror('Error', message)
    
    def perform_sell_stock(self):
        """Process the stock sale."""
        if not self.identified_product_id_for_sale:
            messagebox.showerror('Error', 'Please identify a product first.')
            return
        
        try:
            full_cartons = int(self.sell_num_full_cartons_entry.get())
            loose_pieces = int(self.sell_num_loose_pieces_entry.get())
            if full_cartons < 0 or loose_pieces < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror('Error', 'Please enter valid non-negative numbers for quantities.')
            return
        
        if full_cartons == 0 and loose_pieces == 0:
            messagebox.showerror('Error', 'Please enter a quantity to sell.')
            return
        
        # Find available cartons for this product (FIFO/FEFO logic)
        available_cartons = [c for c in self.stock_app.stock_data 
                           if c['product_id'] == self.identified_product_id_for_sale 
                           and c['date_outwarded'] is None]
        
        if not available_cartons:
            messagebox.showerror('Error', 'No available stock for this product.')
            return
        
        # Sort by expiry date first (FEFO), then by inward date (FIFO)
        from utils.date_utils import parse_date
        available_cartons.sort(key=lambda x: (
            parse_date(x['expiry_date']) or datetime.date(9999, 12, 31),
            parse_date(x['date_inwarded']) or datetime.date(1, 1, 1)
        ))
        
        total_units_to_sell = full_cartons * available_cartons[0]['quantity_per_carton'] + loose_pieces
        total_available = sum(c['quantity_per_carton'] - c['damaged_units'] for c in available_cartons)
        
        if total_units_to_sell > total_available:
            messagebox.showerror('Error', f'Insufficient stock. Available: {total_available} units, Requested: {total_units_to_sell} units.')
            return
        
        # Process the sale
        units_remaining = total_units_to_sell
        total_sales_value = 0
        cartons_sold = []
        
        for carton in available_cartons:
            if units_remaining <= 0:
                break
            
            available_in_carton = carton['quantity_per_carton'] - carton['damaged_units']
            if available_in_carton <= 0:
                continue
            
            units_from_this_carton = min(units_remaining, available_in_carton)
            
            # Calculate sales value using actual sales price
            sales_price_per_unit = carton.get('sales_price', 0)
            purchase_price_per_unit = carton.get('purchase_price', 0)
            sales_value = units_from_this_carton * sales_price_per_unit
            purchase_value = units_from_this_carton * purchase_price_per_unit
            total_sales_value += sales_value
            
            # Update carton
            carton['quantity_per_carton'] -= units_from_this_carton
            if carton['quantity_per_carton'] == 0:
                carton['date_outwarded'] = format_date(datetime.date.today())
            
            cartons_sold.append({
                'carton_id': carton['carton_id'],
                'units_sold': units_from_this_carton,
                'sales_value': sales_value,
                'purchase_value': purchase_value,
                'sales_price': sales_price_per_unit,
                'purchase_price': purchase_price_per_unit
            })
            
            units_remaining -= units_from_this_carton
        
        # Save updated stock data
        save_stock_data(self.stock_app.stock_data, self.stock_app.selected_json_file)
        
        # Log the sale
        sales_log_file = get_log_file_path(self.stock_app.selected_json_file, 'sales')
        for sale in cartons_sold:
            # Find the original carton to get MRP
            original_carton = next((c for c in self.stock_app.stock_data if c['carton_id'] == sale['carton_id']), {})
            append_log_entry(sales_log_file, {
                'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'product_id': self.identified_product_id_for_sale,
                'product_name': next(c['product_name'] for c in self.stock_app.stock_data if c['product_id'] == self.identified_product_id_for_sale),
                'carton_id': sale['carton_id'],
                'quantity': sale['units_sold'],
                'sales_price': sale['sales_price'],
                'purchase_price': sale['purchase_price'],
                'mrp': original_carton.get('mrp', 0),
                'sales_value': sale['sales_value'],
                'purchase_value': sale['purchase_value'],
                'type': 'sale'
            })
        
        # Show success message
        messagebox.showinfo('Success', f"Sale processed successfully!\nTotal units sold: {total_units_to_sell}\nTotal sales value: ₹{total_sales_value:.2f}")
        
        # Clear form and refresh UI
        self.clear_sell_stock_form()
        if hasattr(self.stock_app, 'dashboard_ui'):
            self.stock_app.dashboard_ui.update_dashboard()
    
    def clear_sell_stock_form(self):
        """Clear the sell stock form."""
        self.sell_product_query_entry.delete(0, tk.END)
        self.sell_num_full_cartons_entry.delete(0, tk.END)
        self.sell_num_full_cartons_entry.insert(0, "0")
        self.sell_num_loose_pieces_entry.delete(0, tk.END)
        self.sell_num_loose_pieces_entry.insert(0, "0")
        self.sell_product_summary_text.config(state=tk.NORMAL)
        self.sell_product_summary_text.delete(1.0, tk.END)
        self.sell_product_summary_text.config(state=tk.DISABLED)
        self.identified_product_id_for_sale = None