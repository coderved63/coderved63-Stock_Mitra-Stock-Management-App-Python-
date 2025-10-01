"""
Dashboard UI component for displaying stock statistics and overview.
"""

import tkinter as tk
from tkinter import ttk
from ui.base import BaseUIComponent
from services.stock_manager import StockAnalyzer


class DashboardUI(BaseUIComponent):
    """Dashboard interface component."""
    
    def __init__(self, parent, stock_app_ref):
        super().__init__(parent, stock_app_ref)
        self.frame = self.create_frame()
        self.create_widgets()
    
    def create_widgets(self):
        """Create dashboard widgets."""
        # Dashboard Title
        title_label = ttk.Label(self.frame, text="Dashboard Overview", style='SubHeader.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Stats Frame
        stats_frame = ttk.Frame(self.frame)
        stats_frame.pack(fill='x', pady=(0, 20))
        
        # Key Metrics
        metrics_frame = ttk.LabelFrame(stats_frame, text="Key Metrics", padding="15")
        metrics_frame.pack(fill='x', pady=(0, 10))
        
        # Live Stock
        live_frame = ttk.Frame(metrics_frame)
        live_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(live_frame, text="Total Live Sellable Stock:").pack(side='left')
        self.total_live_label = ttk.Label(live_frame, text="0", font=('Segoe UI', 16, 'bold'))
        self.total_live_label.pack(side='right')
        
        # Damaged/Expired Stock
        damaged_frame = ttk.Frame(metrics_frame)
        damaged_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(damaged_frame, text="Total Damaged/Expired Stock:").pack(side='left')
        self.total_damaged_expired_label = ttk.Label(damaged_frame, text="0", font=('Segoe UI', 16, 'bold'))
        self.total_damaged_expired_label.pack(side='right')
        
        # Total Cartons
        cartons_frame = ttk.Frame(metrics_frame)
        cartons_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(cartons_frame, text="Total Cartons:").pack(side='left')
        self.total_cartons_label = ttk.Label(cartons_frame, text="0", font=('Segoe UI', 16, 'bold'))
        self.total_cartons_label.pack(side='right')
        
        # Stock Value
        value_frame = ttk.Frame(metrics_frame)
        value_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(value_frame, text="Total Stock Value:").pack(side='left')
        self.total_stock_value_label = ttk.Label(value_frame, text="₹0.00", font=('Segoe UI', 16, 'bold'))
        self.total_stock_value_label.pack(side='right')
        
        # Alerts Frame
        alerts_frame = ttk.LabelFrame(stats_frame, text="Alerts & Notifications", padding="15")
        alerts_frame.pack(fill='x', pady=(10, 0))
        
        # Low Stock Alert
        low_stock_frame = ttk.Frame(alerts_frame)
        low_stock_frame.pack(fill='x', pady=(0, 10))
        self.low_stock_label = ttk.Label(low_stock_frame, text="Low Stock: None", foreground="#059669")
        self.low_stock_label.pack(anchor='w')
        
        # Expiry Alerts
        expiry_frame = ttk.Frame(alerts_frame)
        expiry_frame.pack(fill='x')
        self.expiry_alerts_label = ttk.Label(expiry_frame, text="Expiry Alerts: None", foreground="#059669")
        self.expiry_alerts_label.pack(anchor='w')
        
        # Quick Actions Frame
        actions_frame = ttk.LabelFrame(self.frame, text="Quick Actions", padding="15")
        actions_frame.pack(fill='x', pady=(20, 0))
        
        # All buttons in one row - SIDE BY SIDE as requested
        button_frame = ttk.Frame(actions_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Add New Stock", 
                  command=lambda: self.stock_app.notebook.select(2)).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Find Stock", 
                  command=lambda: self.stock_app.notebook.select(1)).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Sell Stock", 
                  command=lambda: self.stock_app.notebook.select(3)).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Update Carton", 
                  command=lambda: self.stock_app.notebook.select(4)).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Sales Summary", 
                  command=lambda: self.stock_app.notebook.select(5)).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Transaction Log", 
                  command=lambda: self.stock_app.notebook.select(6)).pack(side='left', padx=(0, 10))
        
        # Company Stock View Button (PROMINENT and VISIBLE)
        self.company_view_button = ttk.Button(button_frame, 
                                            text=f"📊 VIEW {self.stock_app.selected_company.upper()} STOCK", 
                                            command=self.show_company_stock_view)
        self.company_view_button.pack(side='left', padx=(15, 0))
    
    def update_dashboard(self):
        """Update dashboard with current stock data."""
        analyzer = StockAnalyzer(self.stock_app.stock_data)
        stats = analyzer.get_dashboard_stats()
        
        self.total_live_label.config(text=f"{stats['total_live']}")
        self.total_damaged_expired_label.config(text=f"{stats['total_damaged_expired']}")
        self.total_cartons_label.config(text=f"{stats['total_cartons']}")
        self.total_stock_value_label.config(text=f"₹{stats['total_stock_value']:,.2f}")
        
        # Update alerts
        if stats['low_stock_products']:
            self.low_stock_label.config(text="Low Stock: " + ", ".join(stats['low_stock_products']), 
                                      foreground="#dc2626")
        else:
            self.low_stock_label.config(text="Low Stock: None", foreground="#059669")
        
        if stats['expiry_alerts']:
            self.expiry_alerts_label.config(text="Expiry Alerts: " + ", ".join(stats['expiry_alerts']), 
                                          foreground="#dc2626")
        else:
            self.expiry_alerts_label.config(text="Expiry Alerts: None", foreground="#059669")
    
    def show_company_stock_view(self):
        """Show the company stock view tab."""
        # Check if company stock view tab exists, if not create it
        if not hasattr(self.stock_app, 'company_stock_view_ui'):
            from ui.company_stock_view import CompanyStockViewUI
            self.stock_app.company_stock_view_ui = CompanyStockViewUI(self.stock_app.notebook, self.stock_app)
            self.stock_app.notebook.add(self.stock_app.company_stock_view_ui.frame, text=f"{self.stock_app.selected_company} Stock")
        else:
            # Update the tab title and refresh data
            tab_index = None
            for i, tab in enumerate(self.stock_app.notebook.tabs()):
                if str(tab) == str(self.stock_app.company_stock_view_ui.frame):
                    tab_index = i
                    break
            if tab_index is not None:
                self.stock_app.notebook.tab(tab_index, text=f"{self.stock_app.selected_company} Stock")
            self.stock_app.company_stock_view_ui.update_company_stock_view()
        
        # Switch to the company stock view tab
        self.stock_app.notebook.select(self.stock_app.company_stock_view_ui.frame)