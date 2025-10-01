"""
Main Stock Manager Application - Refactored Version
This is the entry point for the refactored Stock Manager application.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from config.settings import WINDOW_GEOMETRY, APP_TITLE, ensure_data_directory
from config.colors import FRAME_BG
from database.stock_data import load_stock_data, load_company_configs, save_company_configs
from ui.base import configure_styles
from ui.dashboard import DashboardUI
from ui.find_stock import FindStockUI
from ui.add_stock import AddStockUI
from ui.sell_stock import SellStockUI
from ui.update_carton import UpdateCartonUI
from ui.sales_summary import SalesSummaryUI
from ui.transaction_log import TransactionLogUI


class StockManagerApp(tk.Tk):
    """Main Stock Manager Application."""
    
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(WINDOW_GEOMETRY)
        self.configure(bg=FRAME_BG)
        
        # Ensure data directory exists
        ensure_data_directory()
        
        # Initialize data
        self.company_configs = load_company_configs()
        self.selected_company = None
        self.selected_json_file = None
        self.stock_data = []
        
        # Setup menu
        self.menu_bar = tk.Menu(self)
        self.create_menu_bar()
        self.config(menu=self.menu_bar)
        
        # Company selection on startup
        self.prompt_for_company()
        if not self.selected_company or not self.selected_json_file:
            self.destroy()
            return
        
        self.load_selected_company_data()
        
        # Configure styles
        self.style = ttk.Style(self)
        configure_styles(self.style)
        
        # Create header
        self.create_header()
        
        # Show welcome message
        self.after(100, lambda: messagebox.showinfo("Welcome to Stock Mitra", 
                   f"Hello! Welcome to Stock Mitra.\n\nYou are managing stock for: {self.selected_company}"))
        
        # Create main interface
        self.create_main_interface()
    
    def create_header(self):
        """Create application header."""
        header = ttk.Frame(self)
        header.pack(fill='x', side='top')
        header_label = ttk.Label(header, text="Stock Mitra", style='Header.TLabel', anchor='center')
        header_label.pack(fill='x', pady=(0, 8))
    
    def create_main_interface(self):
        """Create the main tabbed interface."""
        # Main Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Create UI components
        self.dashboard_ui = DashboardUI(self.notebook, self)
        self.notebook.add(self.dashboard_ui.frame, text="Dashboard")
        
        self.find_stock_ui = FindStockUI(self.notebook, self)
        self.notebook.add(self.find_stock_ui.frame, text="Find Stock")
        
        self.add_stock_ui = AddStockUI(self.notebook, self)
        self.notebook.add(self.add_stock_ui.frame, text="Add Stock")
        
        self.sell_stock_ui = SellStockUI(self.notebook, self)
        self.notebook.add(self.sell_stock_ui.frame, text="Sell Stock")
        
        self.update_carton_ui = UpdateCartonUI(self.notebook, self)
        self.notebook.add(self.update_carton_ui.frame, text="Update Carton")
        
        self.sales_summary_ui = SalesSummaryUI(self.notebook, self)
        self.notebook.add(self.sales_summary_ui.frame, text="Sales Summary")
        
        self.transaction_log_ui = TransactionLogUI(self.notebook, self)
        self.notebook.add(self.transaction_log_ui.frame, text="Transaction Log")
        
        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
        
        # Initialize data
        self.find_stock_ui.update_find_stock_suggestions()
        self.dashboard_ui.update_dashboard()
    

    
    def on_tab_change(self, event):
        """Handle tab change events."""
        selected_tab_text = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab_text == "Dashboard":
            self.dashboard_ui.update_dashboard()
    
    def prompt_for_company(self):
        """Prompt user to select a company."""
        companies = list(self.company_configs.keys())
        if not companies:
            # No companies configured, add one
            self.add_new_company()
            return
        
        # Create a simple dialog to select company
        from tkinter import simpledialog
        company_choice = simpledialog.askstring(
            "Select Company", 
            f"Available companies: {', '.join(companies)}\n\nEnter company name:"
        )
        
        if company_choice and company_choice in self.company_configs:
            self.selected_company = company_choice
            self.selected_json_file = self.company_configs[company_choice]
        else:
            # Option to add new company
            if messagebox.askyesno("Add New Company", "Company not found. Would you like to add a new company?"):
                self.add_new_company()
    
    def add_new_company(self):
        """Add a new company."""
        from tkinter import simpledialog, filedialog
        
        company_name = simpledialog.askstring("New Company", "Enter company name:")
        if not company_name:
            return
        
        json_file = filedialog.asksaveasfilename(
            title=f"Select JSON file for {company_name}",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if json_file:
            self.company_configs[company_name] = json_file
            save_company_configs(self.company_configs)
            self.selected_company = company_name
            self.selected_json_file = json_file
    
    def load_selected_company_data(self):
        """Load data for the selected company."""
        if self.selected_json_file:
            self.stock_data = load_stock_data(self.selected_json_file)
    
    def create_menu_bar(self):
        """Create the application menu bar."""
        company_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Company", menu=company_menu)
        company_menu.add_command(label="Switch Company", command=self.switch_company)
        company_menu.add_command(label="Add New Company", command=self.add_new_company_and_reload)
    
    def switch_company(self):
        """Switch to a different company."""
        self.prompt_for_company()
        if self.selected_company and self.selected_json_file:
            self.load_selected_company_data()
            self.refresh_all_ui()
    
    def add_new_company_and_reload(self):
        """Add a new company and reload the interface."""
        self.add_new_company()
        if self.selected_company and self.selected_json_file:
            self.load_selected_company_data()
            self.refresh_all_ui()
    
    def refresh_all_ui(self):
        """Refresh all UI components."""
        self.find_stock_ui.update_find_stock_suggestions()
        self.dashboard_ui.update_dashboard()
        self.add_stock_ui.add_company_label.config(text=self.selected_company)
        
        # Update company stock view if it exists
        if hasattr(self, 'company_stock_view_ui'):
            self.company_stock_view_ui.update_company_stock_view()
            # Update tab title
            for i, tab in enumerate(self.notebook.tabs()):
                if str(tab) == str(self.company_stock_view_ui.frame):
                    self.notebook.tab(i, text=f"{self.selected_company} Stock")
                    break


def main():
    """Main application entry point."""
    app = StockManagerApp()
    app.mainloop()


if __name__ == "__main__":
    main()