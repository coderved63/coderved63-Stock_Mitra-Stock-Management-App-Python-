"""
Update Carton UI component for updating individual carton details.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from ui.base import BaseUIComponent
from database.stock_data import save_stock_data
from utils.date_utils import format_date
from config.colors import *


class UpdateCartonUI(BaseUIComponent):
    """Update Carton interface component."""
    
    def __init__(self, parent, stock_app_ref):
        super().__init__(parent, stock_app_ref)
        self.frame = self.create_frame()
        self.current_carton_for_update = None
        self.create_widgets()
    
    def create_widgets(self):
        """Create update carton widgets."""
        # Title
        ttk.Label(self.frame, text="Update Individual Carton", style='SubHeader.TLabel').pack(pady=10)
        
        # Carton ID input
        carton_id_frame = ttk.Frame(self.frame)
        carton_id_frame.pack(pady=5)
        ttk.Label(carton_id_frame, text="Carton ID:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.update_carton_id_entry = ttk.Entry(carton_id_frame, width=40)
        self.update_carton_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.update_carton_id_entry.bind("<Return>", lambda event: self.find_carton_for_update())
        ttk.Button(carton_id_frame, text="Find Carton", command=self.find_carton_for_update).grid(row=0, column=2, padx=5, pady=5)
        
        # Carton details display
        self.update_carton_details_label = ttk.Label(self.frame, text="", wraplength=500)
        self.update_carton_details_label.pack(pady=5, padx=5)
        
        # Action selection
        self.update_action_frame = ttk.LabelFrame(self.frame, text="Choose Action", padding="10")
        self.update_action_frame.pack(fill='x', padx=5, pady=10)
        self.update_action_var = tk.StringVar(value="update")
        ttk.Radiobutton(self.update_action_frame, text="Update Quantity/Damaged", 
                       variable=self.update_action_var, value="update", 
                       command=self.toggle_update_fields).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Radiobutton(self.update_action_frame, text="Delete This Carton", 
                       variable=self.update_action_var, value="delete", 
                       command=self.toggle_update_fields).grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        # Update fields
        self.update_fields_frame = ttk.Frame(self.frame, padding="10")
        self.update_fields_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(self.update_fields_frame, text="New Total Quantity:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.update_new_qty_entry = ttk.Entry(self.update_fields_frame)
        self.update_new_qty_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(self.update_fields_frame, text="New Damaged Units:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.update_new_damaged_entry = ttk.Entry(self.update_fields_frame)
        self.update_new_damaged_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        
        self.update_fields_frame.columnconfigure(1, weight=1)
        self.toggle_update_fields()  # Initial call
        
        # Buttons
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_update_carton_form).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Perform Action", command=self.perform_update_carton).grid(row=0, column=1, padx=5)
    
    def find_carton_for_update(self):
        """Find carton by ID for updating."""
        query_carton_id = self.update_carton_id_entry.get().strip().upper()
        if not query_carton_id:
            messagebox.showerror('Error', 'Please enter a Carton ID to find.')
            return
        
        all_stock_data_combined = self.stock_app.stock_data
        carton = next((c for c in all_stock_data_combined if c['carton_id'] == query_carton_id), None)
        
        if carton:
            if carton['date_outwarded'] is not None:
                messagebox.showinfo('Info', f"Carton {carton['carton_id']} is already outwarded on {carton['date_outwarded']}. No further updates possible.")
                self.current_carton_for_update = None
                self.update_carton_details_label.config(text="")
                return
            
            self.current_carton_for_update = carton
            details_text = f"Product: {carton['product_name']}\nCompany: {carton.get('company', 'N/A')}\nLocation: {carton['location']}\n" \
                          f"Current Quantity: {carton['quantity_per_carton']}\nDamaged: {carton['damaged_units']}\n" \
                          f"Inwarded: {carton['date_inwarded']}\nExpires: {carton['expiry_date'] or 'N/A'}"
            self.update_carton_details_label.config(text=details_text)
            self.update_new_qty_entry.delete(0, tk.END)
            self.update_new_qty_entry.insert(0, str(carton['quantity_per_carton']))
            self.update_new_damaged_entry.delete(0, tk.END)
            self.update_new_damaged_entry.insert(0, str(carton['damaged_units']))
            messagebox.showinfo('Success', f"Carton {carton['carton_id']} found. Ready to update.")
        else:
            messagebox.showerror('Error', f"Carton ID '{query_carton_id}' not found.")
            self.current_carton_for_update = None
            self.update_carton_details_label.config(text="")
    
    def toggle_update_fields(self):
        """Toggle update fields based on action selection."""
        action = self.update_action_var.get()
        if action == 'update':
            self.update_fields_frame.pack(fill='x', padx=5, pady=5)
        else:
            self.update_fields_frame.pack_forget()
    
    def perform_update_carton(self):
        """Perform the carton update or delete action."""
        if not self.current_carton_for_update:
            messagebox.showerror('Error', 'Please find a carton to update first.')
            return
        
        target_carton_id = self.current_carton_for_update['carton_id']
        
        if self.update_action_var.get() == 'update':
            try:
                new_qty = int(self.update_new_qty_entry.get())
                new_damaged = int(self.update_new_damaged_entry.get())
                if new_qty < 0 or new_damaged < 0 or new_damaged > new_qty:
                    raise ValueError
            except ValueError:
                messagebox.showerror('Error', 'Invalid quantity or damaged units. Please enter non-negative numbers, with damaged <= quantity.')
                return
            
            # Find and update the carton in the actual list
            for i, carton in enumerate(self.stock_app.stock_data):
                if carton['carton_id'] == target_carton_id:
                    self.stock_app.stock_data[i]['quantity_per_carton'] = new_qty
                    self.stock_app.stock_data[i]['damaged_units'] = new_damaged
                    self.stock_app.stock_data[i]['last_updated'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if new_qty == 0:
                        self.stock_app.stock_data[i]['date_outwarded'] = format_date(datetime.date.today())
                        messagebox.showinfo('Info', f"Carton {target_carton_id} is now empty and marked as outwarded.")
                    break
            
            save_stock_data(self.stock_app.stock_data, self.stock_app.selected_json_file)
            messagebox.showinfo('Success', f"Carton {target_carton_id} updated successfully. New Quantity: {new_qty}, New Damaged: {new_damaged}.")
        
        elif self.update_action_var.get() == 'delete':
            if messagebox.askyesno("Confirm Delete", f"WARNING: This will PERMANENTLY DELETE Carton {target_carton_id} from records. This action cannot be undone. Are you absolutely sure?"):
                # Remove the carton from the list
                self.stock_app.stock_data[:] = [c for c in self.stock_app.stock_data if c['carton_id'] != target_carton_id]
                save_stock_data(self.stock_app.stock_data, self.stock_app.selected_json_file)
                messagebox.showinfo('Success', f"Carton {target_carton_id} has been permanently DELETED.")
            else:
                messagebox.showinfo('Info', 'Deletion cancelled.')
                return
        
        self.clear_update_carton_form()
        # Refresh dashboard after update/delete
        if hasattr(self.stock_app, 'dashboard_ui'):
            self.stock_app.dashboard_ui.update_dashboard()
    
    def clear_update_carton_form(self):
        """Clear the update carton form."""
        self.update_carton_id_entry.delete(0, tk.END)
        self.update_carton_details_label.config(text="")
        self.update_new_qty_entry.delete(0, tk.END)
        self.update_new_damaged_entry.delete(0, tk.END)
        self.update_action_var.set("update")
        self.toggle_update_fields()
        self.current_carton_for_update = None