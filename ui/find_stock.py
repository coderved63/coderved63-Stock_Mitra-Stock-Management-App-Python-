"""
Find Stock UI component for searching and displaying stock information.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import difflib
from ui.base import BaseUIComponent
from services.stock_search import get_product_summary_text
from config.colors import *


class FindStockUI(BaseUIComponent):
    """Find Stock interface component."""
    
    def __init__(self, parent, stock_app_ref):
        super().__init__(parent, stock_app_ref)
        self.frame = self.create_frame()
        self.all_product_suggestions = []
        self.suggestion_map = {}
        self.suggestion_window = None
        self.suggestion_listbox = None
        self.create_widgets()
    
    def create_widgets(self):
        """Create find stock widgets."""
        # Title
        ttk.Label(self.frame, text="Find Stock", style='SubHeader.TLabel').pack(pady=(0, 18))
        
        # Search Frame
        search_frame = ttk.Frame(self.frame)
        search_frame.pack(pady=5)
        
        ttk.Label(search_frame, text="Product ID or Name:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.find_stock_query_entry = ttk.Entry(search_frame, width=60)
        self.find_stock_query_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.find_stock_query_entry.bind("<Return>", lambda event: self.perform_find_stock())
        self.find_stock_query_entry.bind('<KeyRelease>', self.show_find_stock_suggestions)
        
        ttk.Button(search_frame, text="Search", command=self.perform_find_stock).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(search_frame, text="Clear", command=self.clear_find_stock).grid(row=0, column=3, padx=5, pady=5)
        
        # Results Text Area
        self.find_stock_results_text = tk.Text(
            self.frame, wrap=tk.WORD, height=20, width=90,
            font=('Segoe UI', 15), bg=ACCENT_COLOR, fg=LABEL_FG,
            relief='flat', padx=18, pady=18
        )
        self.find_stock_results_text.pack(pady=16, padx=5, fill='both', expand=True)
        self.find_stock_results_text.config(state=tk.DISABLED)  # Make it read-only
    
    def update_find_stock_suggestions(self):
        """Update product suggestions for autocomplete."""
        all_stock = self.stock_app.stock_data
        suggestions = set()
        self.suggestion_map = {}  # Map display string to (product_id, product_name, mrp)
        for item in all_stock:
            display = f"{item['product_id']} - {item['product_name']} (MRP: ₹{item.get('mrp', 0):.2f})"
            suggestions.add(display)
            self.suggestion_map[display] = (item['product_id'], item['product_name'], item.get('mrp', 0))
        self.all_product_suggestions = sorted(suggestions)
    
    def show_find_stock_suggestions(self, event):
        """Show autocomplete suggestions."""
        typed = self.find_stock_query_entry.get().strip().lower()
        # Destroy previous suggestion window if exists
        if hasattr(self, 'suggestion_window') and self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None
        if not typed:
            return
        matches = [s for s in self.all_product_suggestions if typed in s.lower()]
        if not matches:
            return
        # Create a Toplevel window for suggestions
        entry_widget = self.find_stock_query_entry
        x = entry_widget.winfo_rootx()
        y = entry_widget.winfo_rooty() + entry_widget.winfo_height()
        self.suggestion_window = tk.Toplevel(self.stock_app)
        self.suggestion_window.wm_overrideredirect(True)
        self.suggestion_window.wm_geometry(f"{entry_widget.winfo_width()}x{min(6, len(matches))*22}+{x}+{y}")
        self.suggestion_window.lift()
        self.suggestion_window.attributes('-topmost', True)
        # Listbox inside the Toplevel
        self.suggestion_listbox = tk.Listbox(self.suggestion_window, height=min(6, len(matches)), font=('Arial', 10))
        self.suggestion_listbox.pack(fill='both', expand=True)
        for match in matches:
            self.suggestion_listbox.insert(tk.END, match)
        self.suggestion_listbox.focus_set()
        # Mouse click selection
        self.suggestion_listbox.bind('<<ListboxSelect>>', lambda e: self.select_find_stock_suggestion())
        self.suggestion_listbox.bind('<ButtonRelease-1>', lambda e: self.select_find_stock_suggestion())
        # Keyboard navigation
        self.suggestion_listbox.bind('<Return>', lambda e: self.select_find_stock_suggestion())
        self.suggestion_listbox.bind('<Escape>', lambda e: self.close_find_stock_suggestions())
        self.suggestion_listbox.bind('<Up>', self.move_suggestion_up)
        self.suggestion_listbox.bind('<Down>', self.move_suggestion_down)
        # Focus out closes suggestions
        self.suggestion_window.bind('<FocusOut>', lambda e: self.close_find_stock_suggestions())
    
    def select_find_stock_suggestion(self):
        """Select a suggestion from the dropdown."""
        if self.suggestion_listbox:
            selection = self.suggestion_listbox.curselection()
            if selection:
                display_value = self.suggestion_listbox.get(selection[0])
                # Fill the entry with the product_id
                product_id, product_name, mrp = self.suggestion_map.get(display_value, (display_value, '', 0))
                self.find_stock_query_entry.delete(0, tk.END)
                self.find_stock_query_entry.insert(0, product_id)
            self.close_find_stock_suggestions()
    
    def close_find_stock_suggestions(self):
        """Close the suggestions dropdown."""
        if hasattr(self, 'suggestion_window') and self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None
        self.suggestion_listbox = None
    
    def move_suggestion_up(self, event):
        """Move selection up in suggestions."""
        if self.suggestion_listbox:
            cur = self.suggestion_listbox.curselection()
            if cur:
                idx = cur[0]
                if idx > 0:
                    self.suggestion_listbox.selection_clear(0, tk.END)
                    self.suggestion_listbox.selection_set(idx-1)
                    self.suggestion_listbox.activate(idx-1)
            else:
                self.suggestion_listbox.selection_set(0)
                self.suggestion_listbox.activate(0)
        return "break"
    
    def move_suggestion_down(self, event):
        """Move selection down in suggestions."""
        if self.suggestion_listbox:
            cur = self.suggestion_listbox.curselection()
            size = self.suggestion_listbox.size()
            if cur:
                idx = cur[0]
                if idx < size-1:
                    self.suggestion_listbox.selection_clear(0, tk.END)
                    self.suggestion_listbox.selection_set(idx+1)
                    self.suggestion_listbox.activate(idx+1)
            else:
                self.suggestion_listbox.selection_set(0)
                self.suggestion_listbox.activate(0)
        return "break"
    
    def perform_find_stock(self):
        """Perform stock search and display results."""
        if hasattr(self, 'suggestion_window') and self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None
        self.suggestion_listbox = None
        query = self.find_stock_query_entry.get().strip()
        if not query:
            messagebox.showerror('Error', 'Please enter a product ID or name to search.')
            return
        
        all_stock_data_combined = self.stock_app.stock_data
        summary = get_product_summary_text(query, all_stock_data_combined)
        self.find_stock_results_text.config(state=tk.NORMAL)  # Enable editing
        self.find_stock_results_text.delete(1.0, tk.END)  # Clear previous
        self.find_stock_results_text.insert(tk.END, summary)
        
        # --- Recommendations/Suggestions ---
        # If not an exact match, show similar product IDs/names
        product_ids = [item['product_id'] for item in all_stock_data_combined]
        product_names = [item['product_name'] for item in all_stock_data_combined]
        close_ids = difflib.get_close_matches(query.upper(), product_ids, n=5, cutoff=0.6)
        close_names = difflib.get_close_matches(query.lower(), [n.lower() for n in product_names], n=5, cutoff=0.6)
        suggestions = set(close_ids)
        for idx, name in enumerate(product_names):
            if name.lower() in close_names:
                suggestions.add(product_ids[idx])
        if suggestions and (not summary or summary.startswith("Sorry") or summary.startswith("I couldn't find")):
            self.find_stock_results_text.insert(tk.END, "\n\nDid you mean:\n")
            for sid in suggestions:
                name = next((item['product_name'] for item in all_stock_data_combined if item['product_id'] == sid), '')
                self.find_stock_results_text.insert(tk.END, f"  - {sid} ({name})\n")
        self.find_stock_results_text.config(state=tk.DISABLED)  # Disable editing
        
        if summary.startswith("Sorry,") or summary.startswith("I found multiple products"):
            messagebox.showerror('Error', summary.split('\n')[0])  # Show first line as error
        else:
            messagebox.showinfo('Success', 'Search results displayed.')
    
    def clear_find_stock(self):
        """Clear the search form."""
        self.find_stock_query_entry.delete(0, tk.END)
        self.find_stock_results_text.config(state=tk.NORMAL)
        self.find_stock_results_text.delete(1.0, tk.END)
        self.find_stock_results_text.config(state=tk.DISABLED)
        if hasattr(self, 'suggestion_window') and self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None
        self.suggestion_listbox = None
        messagebox.showinfo('Info', 'Find Stock search cleared.')