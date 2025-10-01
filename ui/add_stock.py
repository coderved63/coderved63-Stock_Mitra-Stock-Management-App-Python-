"""
Add Stock UI component for adding new stock inventory.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from ui.base import BaseUIComponent
from database.stock_data import save_stock_data, append_log_entry
from utils.date_utils import parse_date
from utils.file_utils import get_log_file_path
from config.colors import *


class AddStockUI(BaseUIComponent):
    """Add Stock interface component."""
    
    def __init__(self, parent, stock_app_ref):
        super().__init__(parent, stock_app_ref)
        self.frame = self.create_frame()
        self.carton_entries = []
        self.create_widgets()
    
    def create_widgets(self):
        """Create add stock widgets."""
        # Title
        ttk.Label(self.frame, text="Add New Stock", style='SubHeader.TLabel').pack(pady=(0, 18))
        
        # Main horizontal layout frame
        main_content_frame = ttk.Frame(self.frame)
        main_content_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left: Product Details
        details_frame = ttk.Frame(main_content_frame)
        details_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 20), pady=5)
        
        # Right: Carton Details
        cartons_frame = ttk.Frame(main_content_frame)
        cartons_frame.grid(row=0, column=1, sticky='nsew', padx=(20, 0), pady=5)
        main_content_frame.columnconfigure(0, weight=1)
        main_content_frame.columnconfigure(1, weight=1)
        main_content_frame.rowconfigure(0, weight=1)
        
        # Product Details on the left
        ttk.Label(details_frame, text="Company Name:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.add_company_label = ttk.Label(details_frame, text=self.stock_app.selected_company)
        self.add_company_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(details_frame, text="Product ID:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        # Product ID frame with suggestion dropdown
        product_id_frame = ttk.Frame(details_frame)
        product_id_frame.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        product_id_frame.columnconfigure(0, weight=1)
        
        self.add_product_id_entry = ttk.Entry(product_id_frame)
        self.add_product_id_entry.grid(row=0, column=0, sticky='ew')
        self.add_product_id_entry.bind('<KeyRelease>', self.on_product_id_key_release)
        self.add_product_id_entry.bind('<Down>', self.focus_suggestions)
        self.add_product_id_entry.bind('<Up>', self.focus_suggestions)
        self.add_product_id_entry.bind('<FocusOut>', self.on_product_id_focus_out)
        
        # Suggestions listbox (initially hidden)
        self.suggestions_listbox = tk.Listbox(product_id_frame, height=5)
        self.suggestions_listbox.bind('<Button-1>', self.on_suggestion_select)
        self.suggestions_listbox.bind('<Double-Button-1>', self.on_suggestion_select)
        self.suggestions_listbox.bind('<Return>', self.on_suggestion_select)
        self.suggestions_listbox.bind('<Key>', self.on_suggestion_key)
        
        ttk.Label(details_frame, text="Product Name:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        
        # Product Name frame with suggestion dropdown
        product_name_frame = ttk.Frame(details_frame)
        product_name_frame.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        product_name_frame.columnconfigure(0, weight=1)
        
        self.add_product_name_entry = ttk.Entry(product_name_frame)
        self.add_product_name_entry.grid(row=0, column=0, sticky='ew')
        self.add_product_name_entry.bind('<KeyRelease>', self.on_product_name_key_release)
        self.add_product_name_entry.bind('<Down>', self.focus_name_suggestions)
        self.add_product_name_entry.bind('<Up>', self.focus_name_suggestions)
        self.add_product_name_entry.bind('<FocusOut>', self.on_product_name_focus_out)
        
        # Name suggestions listbox (initially hidden)
        self.name_suggestions_listbox = tk.Listbox(product_name_frame, height=5)
        self.name_suggestions_listbox.bind('<Button-1>', self.on_name_suggestion_select)
        self.name_suggestions_listbox.bind('<Double-Button-1>', self.on_name_suggestion_select)
        self.name_suggestions_listbox.bind('<Return>', self.on_name_suggestion_select)
        self.name_suggestions_listbox.bind('<Key>', self.on_name_suggestion_key)
        
        ttk.Label(details_frame, text="Location:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.add_location_entry = ttk.Entry(details_frame)
        self.add_location_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(details_frame, text="Date Inwarded (YYYY-MM-DD):").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.add_date_inwarded_entry = ttk.Entry(details_frame)
        self.add_date_inwarded_entry.grid(row=4, column=1, padx=5, pady=5, sticky='ew')
        self.add_date_inwarded_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        
        ttk.Label(details_frame, text="Expiry Date (YYYY-MM-DD, Optional):").grid(row=5, column=0, padx=5, pady=5, sticky='w')
        self.add_expiry_date_entry = ttk.Entry(details_frame)
        self.add_expiry_date_entry.grid(row=5, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(details_frame, text="Number of NEW Cartons:").grid(row=6, column=0, padx=5, pady=5, sticky='w')
        self.add_num_cartons_var = tk.IntVar(value=1)
        self.add_num_cartons_spinbox = ttk.Spinbox(details_frame, from_=1, to=100, textvariable=self.add_num_cartons_var, width=5)
        self.add_num_cartons_spinbox.grid(row=6, column=1, padx=5, pady=5, sticky='w')
        self.add_num_cartons_var.trace_add('write', lambda *args: self.update_add_carton_details_fields())
        
        details_frame.columnconfigure(1, weight=1)
        
        # Carton Details on the right (VERTICAL SCROLLABLE)
        self.carton_canvas = tk.Canvas(cartons_frame, borderwidth=0, background=FRAME_BG, height=350)
        self.carton_scrollbar = ttk.Scrollbar(cartons_frame, orient="vertical", command=self.carton_canvas.yview)
        self.carton_canvas.configure(yscrollcommand=self.carton_scrollbar.set)
        self.carton_canvas.pack(side="left", fill="both", expand=True)
        self.carton_scrollbar.pack(side="right", fill="y")
        self.add_carton_details_frame = ttk.Frame(self.carton_canvas)
        self.carton_canvas.create_window((0, 0), window=self.add_carton_details_frame, anchor="nw")
        
        def _on_frame_configure(event):
            self.carton_canvas.configure(scrollregion=self.carton_canvas.bbox("all"))
        self.add_carton_details_frame.bind("<Configure>", _on_frame_configure)
        
        def _on_mousewheel(event):
            self.carton_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.carton_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        self.update_add_carton_details_fields()  # Initial call to create fields for 1 carton
        
        # Buttons centered below both columns
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(pady=18)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_add_stock_form).pack(side='left', padx=16)
        ttk.Button(button_frame, text="Add Stock", command=self.perform_add_stock).pack(side='left', padx=16)
    
    def update_add_carton_details_fields(self):
        """Update carton detail fields based on number of cartons."""
        # Clear existing entries
        for widget in self.add_carton_details_frame.winfo_children():
            widget.destroy()
        self.carton_entries = []
        
        try:
            num_cartons = int(self.add_num_cartons_var.get())
        except Exception:
            num_cartons = 1
        num_cartons = max(1, min(100, num_cartons))
        
        for i in range(num_cartons):
            carton_label_frame = ttk.LabelFrame(self.add_carton_details_frame, text=f"Carton {i+1}", padding="10")
            carton_label_frame.grid(row=i, column=0, padx=10, pady=5, sticky='ew')
            
            ttk.Label(carton_label_frame, text="Pieces (Units):").grid(row=0, column=0, padx=5, pady=2, sticky='w')
            qty_entry = ttk.Entry(carton_label_frame)
            qty_entry.grid(row=1, column=0, padx=5, pady=2, sticky='ew')
            
            ttk.Label(carton_label_frame, text="Damaged Units:").grid(row=2, column=0, padx=5, pady=2, sticky='w')
            damaged_entry = ttk.Entry(carton_label_frame)
            damaged_entry.grid(row=3, column=0, padx=5, pady=2, sticky='ew')
            damaged_entry.insert(0, "0")  # Default to 0 damaged
            
            ttk.Label(carton_label_frame, text="MRP:").grid(row=4, column=0, padx=5, pady=2, sticky='w')
            mrp_entry = ttk.Entry(carton_label_frame)
            mrp_entry.grid(row=5, column=0, padx=5, pady=2, sticky='ew')
            
            self.carton_entries.append({
                'qty_entry': qty_entry,
                'damaged_entry': damaged_entry,
                'mrp_entry': mrp_entry
            })
            carton_label_frame.columnconfigure(0, weight=1)
    
    def perform_add_stock(self):
        """Add new stock to inventory."""
        product_id = self.add_product_id_entry.get().strip().upper()
        product_name = self.add_product_name_entry.get().strip()
        location = self.add_location_entry.get().strip().upper()
        date_inwarded_str = self.add_date_inwarded_entry.get().strip()
        expiry_date_str = self.add_expiry_date_entry.get().strip()
        
        if not all([product_id, product_name, location, date_inwarded_str]):
            messagebox.showerror('Error', 'Please fill in all required product details.')
            return
        
        try:
            parse_date(date_inwarded_str)
            if expiry_date_str:
                parse_date(expiry_date_str)
        except ValueError:
            messagebox.showerror('Error', 'Invalid date format. Please use YYYY-MM-DD.')
            return
        
        cartons_data_for_add = []
        for entry_set in self.carton_entries:
            try:
                qty = int(entry_set['qty_entry'].get())
                damaged = int(entry_set['damaged_entry'].get())
                mrp = float(entry_set['mrp_entry'].get())
                if qty <= 0 or damaged < 0 or damaged > qty or mrp < 0:
                    raise ValueError
                cartons_data_for_add.append({'quantity': qty, 'damaged': damaged, 'mrp': mrp})
            except ValueError:
                messagebox.showerror('Error', 'Please enter valid positive numbers for quantity and MRP, and non-negative for damaged units (damaged <= quantity).')
                return
        
        # Check for product ID/name conflict
        existing_product = next((item for item in self.stock_app.stock_data if item['product_id'] == product_id and item['product_name'] != product_name), None)
        if existing_product:
            if not messagebox.askyesno("Warning", f"Product ID {product_id} is already used for '{existing_product['product_name']}'. Are you sure you want to add '{product_name}' with this ID?"):
                messagebox.showinfo('Info', 'Stock addition cancelled.')
                return
        
        added_carton_ids = []
        for carton_detail in cartons_data_for_add:
            existing_cartons_for_product = [c for c in self.stock_app.stock_data if c['product_id'] == product_id]
            max_carton_num = 0
            for carton in existing_cartons_for_product:
                try:
                    parts = carton['carton_id'].split('-C')
                    if len(parts) > 1:
                        max_carton_num = max(max_carton_num, int(parts[-1]))
                except (ValueError, IndexError):
                    pass
            new_carton_num = max_carton_num + 1
            carton_id = f"{product_id}-C{str(new_carton_num).zfill(2)}"
            
            new_carton = {
                "product_id": product_id,
                "product_name": product_name,
                "company": self.stock_app.selected_company,
                "carton_id": carton_id,
                "quantity_per_carton": carton_detail['quantity'],
                "damaged_units": carton_detail['damaged'],
                "location": location,
                "date_inwarded": date_inwarded_str,
                "expiry_date": expiry_date_str if expiry_date_str else None,
                "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "date_outwarded": None,
                "mrp": carton_detail['mrp']
            }
            self.stock_app.stock_data.append(new_carton)
            added_carton_ids.append(carton_id)
            
            # Log purchase
            purchase_log_file = get_log_file_path(self.stock_app.selected_json_file, 'purchase')
            append_log_entry(purchase_log_file, {
                'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'product_id': product_id,
                'product_name': product_name,
                'carton_id': carton_id,
                'quantity': carton_detail['quantity'],
                'mrp': carton_detail['mrp'],
                'type': 'purchase',
            })
        
        save_stock_data(self.stock_app.stock_data, self.stock_app.selected_json_file)
        messagebox.showinfo('Success', f"Successfully added {len(cartons_data_for_add)} new carton(s) for '{product_name}' ({product_id}). New Carton IDs: {', '.join(added_carton_ids)}")
        self.clear_add_stock_form()
        
        # Refresh dashboard and suggestions
        if hasattr(self.stock_app, 'dashboard_ui'):
            self.stock_app.dashboard_ui.update_dashboard()
        if hasattr(self.stock_app, 'find_stock_ui'):
            self.stock_app.find_stock_ui.update_find_stock_suggestions()
    
    def clear_add_stock_form(self):
        """Clear the add stock form."""
        self.add_company_label.config(text=self.stock_app.selected_company)
        self.add_product_id_entry.delete(0, tk.END)
        self.add_product_name_entry.delete(0, tk.END)
        self.add_location_entry.delete(0, tk.END)
        self.add_date_inwarded_entry.delete(0, tk.END)
        self.add_date_inwarded_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.add_expiry_date_entry.delete(0, tk.END)
        self.add_num_cartons_var.set(1)
        self.update_add_carton_details_fields()  # Reset carton details fields
        self.hide_suggestions()  # Hide any open suggestions
        self.hide_name_suggestions()  # Hide any open name suggestions
    
    def get_product_suggestions(self, query):
        """Get product suggestions based on query."""
        if not query or len(query) < 1:
            return []
        
        suggestions = []
        query_lower = query.lower()
        
        # Get unique products from existing stock data
        seen_products = set()
        for item in self.stock_app.stock_data:
            product_key = (item['product_id'], item['product_name'])
            if product_key not in seen_products:
                product_id = item['product_id'].lower()
                product_name = item['product_name'].lower()
                
                # Match by product ID or product name
                if (query_lower in product_id or query_lower in product_name):
                    suggestions.append({
                        'product_id': item['product_id'],
                        'product_name': item['product_name'],
                        'location': item.get('location', ''),
                        'display': f"{item['product_id']} - {item['product_name']}"
                    })
                    seen_products.add(product_key)
        
        # Sort suggestions by relevance (exact ID match first, then name match)
        suggestions.sort(key=lambda x: (
            0 if x['product_id'].lower().startswith(query_lower) else 1,
            x['product_id'].lower()
        ))
        
        return suggestions[:8]  # Limit to 8 suggestions
    
    def on_product_id_key_release(self, event):
        """Handle key release in product ID entry."""
        query = self.add_product_id_entry.get()
        
        if event.keysym in ('Up', 'Down', 'Left', 'Right', 'Tab'):
            return
        
        suggestions = self.get_product_suggestions(query)
        
        if suggestions and len(query) >= 1:
            self.show_suggestions(suggestions)
        else:
            self.hide_suggestions()
    
    def show_suggestions(self, suggestions):
        """Show suggestions dropdown."""
        self.suggestions_listbox.delete(0, tk.END)
        
        for suggestion in suggestions:
            self.suggestions_listbox.insert(tk.END, suggestion['display'])
        
        # Store suggestions data for later use
        self.current_suggestions = suggestions
        
        # Position and show the listbox
        self.suggestions_listbox.grid(row=1, column=0, sticky='ew', pady=(2, 0))
        self.suggestions_listbox.lift()
    
    def hide_suggestions(self, event=None):
        """Hide suggestions dropdown."""
        # Use after() to delay hiding to allow for click events
        self.frame.after(100, self._hide_suggestions_delayed)
    
    def _hide_suggestions_delayed(self):
        """Actually hide the suggestions after delay."""
        try:
            self.suggestions_listbox.grid_remove()
        except:
            pass
    
    def on_suggestion_select(self, event=None):
        """Handle suggestion selection."""
        try:
            # Get selection index - for single click, select the item first
            if event and event.type == '4':  # Button click
                # Get the index of the item clicked
                clicked_index = self.suggestions_listbox.nearest(event.y)
                self.suggestions_listbox.selection_clear(0, tk.END)
                self.suggestions_listbox.selection_set(clicked_index)
                self.suggestions_listbox.activate(clicked_index)
            
            selection_indices = self.suggestions_listbox.curselection()
            if not selection_indices:
                return
                
            selection_index = selection_indices[0]
            selected_suggestion = self.current_suggestions[selection_index]
            
            # Auto-fill product ID and name
            self.add_product_id_entry.delete(0, tk.END)
            self.add_product_id_entry.insert(0, selected_suggestion['product_id'])
            
            self.add_product_name_entry.delete(0, tk.END)
            self.add_product_name_entry.insert(0, selected_suggestion['product_name'])
            
            # Auto-fill location if available and current location is empty
            if selected_suggestion['location'] and not self.add_location_entry.get():
                self.add_location_entry.delete(0, tk.END)
                self.add_location_entry.insert(0, selected_suggestion['location'])
            
            # Hide suggestions
            self.hide_suggestions()
            
            # Focus on next field (location)
            self.add_location_entry.focus_set()
            
        except (IndexError, AttributeError, KeyError):
            pass
    
    def on_suggestion_key(self, event):
        """Handle keyboard navigation in suggestions."""
        if event.keysym == 'Return':
            self.on_suggestion_select(event)
    
    def on_product_name_key_release(self, event):
        """Handle key release in product name entry."""
        query = self.add_product_name_entry.get()
        
        if event.keysym in ('Up', 'Down', 'Left', 'Right', 'Tab'):
            return
        
        suggestions = self.get_product_suggestions(query)
        
        if suggestions and len(query) >= 1:
            self.show_name_suggestions(suggestions)
        else:
            self.hide_name_suggestions()
    
    def show_name_suggestions(self, suggestions):
        """Show name suggestions dropdown."""
        self.name_suggestions_listbox.delete(0, tk.END)
        
        for suggestion in suggestions:
            self.name_suggestions_listbox.insert(tk.END, suggestion['display'])
        
        # Store suggestions data for later use
        self.current_name_suggestions = suggestions
        
        # Position and show the listbox
        self.name_suggestions_listbox.grid(row=1, column=0, sticky='ew', pady=(2, 0))
        self.name_suggestions_listbox.lift()
    
    def hide_name_suggestions(self, event=None):
        """Hide name suggestions dropdown."""
        # Use after() to delay hiding to allow for click events
        self.frame.after(100, self._hide_name_suggestions_delayed)
    
    def _hide_name_suggestions_delayed(self):
        """Actually hide the name suggestions after delay."""
        try:
            self.name_suggestions_listbox.grid_remove()
        except:
            pass
    
    def on_name_suggestion_select(self, event=None):
        """Handle name suggestion selection."""
        try:
            # Get selection index - for single click, select the item first
            if event and event.type == '4':  # Button click
                # Get the index of the item clicked
                clicked_index = self.name_suggestions_listbox.nearest(event.y)
                self.name_suggestions_listbox.selection_clear(0, tk.END)
                self.name_suggestions_listbox.selection_set(clicked_index)
                self.name_suggestions_listbox.activate(clicked_index)
            
            selection_indices = self.name_suggestions_listbox.curselection()
            if not selection_indices:
                return
                
            selection_index = selection_indices[0]
            selected_suggestion = self.current_name_suggestions[selection_index]
            
            # Auto-fill product name and ID
            self.add_product_name_entry.delete(0, tk.END)
            self.add_product_name_entry.insert(0, selected_suggestion['product_name'])
            
            self.add_product_id_entry.delete(0, tk.END)
            self.add_product_id_entry.insert(0, selected_suggestion['product_id'])
            
            # Auto-fill location if available and current location is empty
            if selected_suggestion['location'] and not self.add_location_entry.get():
                self.add_location_entry.delete(0, tk.END)
                self.add_location_entry.insert(0, selected_suggestion['location'])
            
            # Hide suggestions
            self.hide_name_suggestions()
            
            # Focus on next field (location)
            self.add_location_entry.focus_set()
            
        except (IndexError, AttributeError, KeyError):
            pass
    
    def on_name_suggestion_key(self, event):
        """Handle keyboard navigation in name suggestions."""
        if event.keysym == 'Return':
            self.on_name_suggestion_select(event)
    
    def on_product_id_focus_out(self, event):
        """Handle focus out from product ID entry."""
        # Check if focus is moving to the suggestions listbox
        focused_widget = self.frame.focus_get()
        if focused_widget != self.suggestions_listbox:
            self.hide_suggestions()
    
    def on_product_name_focus_out(self, event):
        """Handle focus out from product name entry."""
        # Check if focus is moving to the suggestions listbox
        focused_widget = self.frame.focus_get()
        if focused_widget != self.name_suggestions_listbox:
            self.hide_name_suggestions()
    
    def focus_suggestions(self, event):
        """Focus on suggestions listbox for keyboard navigation."""
        try:
            if self.suggestions_listbox.winfo_viewable():
                self.suggestions_listbox.focus_set()
                if self.suggestions_listbox.size() > 0:
                    self.suggestions_listbox.selection_set(0)
                    self.suggestions_listbox.activate(0)
                return 'break'
        except:
            pass
    
    def focus_name_suggestions(self, event):
        """Focus on name suggestions listbox for keyboard navigation."""
        try:
            if self.name_suggestions_listbox.winfo_viewable():
                self.name_suggestions_listbox.focus_set()
                if self.name_suggestions_listbox.size() > 0:
                    self.name_suggestions_listbox.selection_set(0)
                    self.name_suggestions_listbox.activate(0)
                return 'break'
        except:
            pass