"""
Company Stock View UI component for displaying comprehensive company stock details.
"""

import tkinter as tk
from tkinter import ttk
import datetime
from ui.base import BaseUIComponent


class CompanyStockViewUI(BaseUIComponent):
    """Company Stock View interface component."""
    
    def __init__(self, parent, stock_app_ref):
        super().__init__(parent, stock_app_ref)
        self.frame = self.create_frame()
        self.create_widgets()
        self.update_company_stock_view()
    
    def create_widgets(self):
        """Create company stock view widgets."""
        # Main scrollable frame
        self.canvas = tk.Canvas(self.frame)
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Content frame inside scrollable frame
        self.content_frame = ttk.Frame(self.scrollable_frame)
        self.content_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    def parse_date(self, date_str):
        """Parse date string to date object."""
        if not date_str:
            return None
        try:
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            try:
                return datetime.datetime.strptime(date_str, "%d/%m/%Y").date()
            except ValueError:
                return None
    
    def format_date(self, date_obj):
        """Format date object to string."""
        if not date_obj:
            return "N/A"
        return date_obj.strftime("%d/%m/%Y")
    
    def update_company_stock_view(self):
        """Update the company stock view with current data."""
        # Clear previous content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        if not self.stock_app.stock_data:
            ttk.Label(self.content_frame, text="No stock data available", 
                     style='SubHeader.TLabel').pack(pady=20)
            return
        
        # Back button
        ttk.Button(self.content_frame, text="← Back to Dashboard", 
                  command=lambda: self.stock_app.notebook.select(0)).pack(anchor='nw', pady=5)
        
        # Title
        title_frame = ttk.Frame(self.content_frame)
        title_frame.pack(fill='x', pady=(10, 20))
        
        ttk.Label(title_frame, text=f"{self.stock_app.selected_company} Stock Details", 
                 font=('Segoe UI', 18, 'bold')).pack(anchor='center')
        
        # Add separator
        ttk.Separator(self.content_frame, orient='horizontal').pack(fill='x', pady=(0, 15))
        
        company_stock = self.stock_app.stock_data
        current_date = datetime.date.today()
        
        # Aggregate data by product_id (matching original logic exactly)
        aggregated_products = {}
        for carton in company_stock:
            product_id = carton['product_id']
            if product_id not in aggregated_products:
                aggregated_products[product_id] = {
                    'productId': carton['product_id'],
                    'productName': carton['product_name'],
                    'purchase_per_piece_sum': 0,
                    'sales_per_piece_sum': 0,
                    'purchase_per_piece_count': 0,
                    'sales_per_piece_count': 0,
                    'mrp_sum': 0,
                    'mrp_count': 0,
                    'totalLiveCartons': 0,
                    'totalLivePieces': 0,
                    'totalDamagedUnits': 0,
                    'totalExpiredUnits': 0,
                    'earliestInwarded': datetime.date(9999, 12, 31),
                    'earliestExpiry': datetime.date(9999, 12, 31),
                    'latestOutwarded': datetime.date(1, 1, 1),
                    'locations': set(),
                    'hasActiveStock': False,
                    'hasExpiredStock': False,
                    'hasDamagedStock': False
                }
            product = aggregated_products[product_id]
            product['locations'].add(carton['location'])

            # Calculate per piece prices (prices in our data model are already per piece)
            if carton.get('purchase_price') is not None:
                product['purchase_per_piece_sum'] += carton['purchase_price']
                product['purchase_per_piece_count'] += 1
            if carton.get('sales_price') is not None:
                product['sales_per_piece_sum'] += carton['sales_price']
                product['sales_per_piece_count'] += 1
            if carton.get('mrp') is not None and carton.get('mrp') > 0:
                product['mrp_sum'] += carton['mrp']
                product['mrp_count'] += 1

            if carton['date_outwarded'] is None:
                product['hasActiveStock'] = True
                is_expired = False
                if carton['expiry_date']:
                    expiry_date_obj = self.parse_date(carton['expiry_date'])
                    if expiry_date_obj and expiry_date_obj <= current_date:
                        is_expired = True
                        product['hasExpiredStock'] = True
                        product['totalExpiredUnits'] += carton['quantity_per_carton']
                        product['totalDamagedUnits'] += carton['quantity_per_carton']
                    elif expiry_date_obj and expiry_date_obj < product['earliestExpiry']:
                        product['earliestExpiry'] = expiry_date_obj
                if not is_expired:
                    product['totalLiveCartons'] += 1
                    product['totalLivePieces'] += carton['quantity_per_carton']
                    product['totalDamagedUnits'] += carton['damaged_units']
                    if carton['damaged_units'] > 0:
                        product['hasDamagedStock'] = True
                    inward_date_obj = self.parse_date(carton['date_inwarded'])
                    if inward_date_obj and inward_date_obj < product['earliestInwarded']:
                        product['earliestInwarded'] = inward_date_obj
            else:
                outward_date_obj = self.parse_date(carton['date_outwarded'])
                if outward_date_obj and outward_date_obj > product['latestOutwarded']:
                    product['latestOutwarded'] = outward_date_obj

        sorted_aggregated_products = list(aggregated_products.values())
        sorted_aggregated_products.sort(key=lambda x: x['productId'])

        # Summary Statistics
        total_products = len(sorted_aggregated_products)
        total_live_cartons = sum(p['totalLiveCartons'] for p in sorted_aggregated_products)
        total_live_pieces = sum(p['totalLivePieces'] for p in sorted_aggregated_products)
        in_stock_products = sum(1 for p in sorted_aggregated_products if p['totalLivePieces'] > 0)
        out_of_stock_products = total_products - in_stock_products
        
        # Summary frame
        summary_frame = ttk.LabelFrame(self.content_frame, text="Summary", padding="15")
        summary_frame.pack(fill='x', pady=(0, 15))
        
        # Statistics in a grid
        stats_frame = ttk.Frame(summary_frame)
        stats_frame.pack(fill='x')
        
        ttk.Label(stats_frame, text=f"Total Products: {total_products}", 
                 font=('Segoe UI', 11, 'bold')).grid(row=0, column=0, padx=(0, 30), pady=5, sticky='w')
        ttk.Label(stats_frame, text=f"In Stock: {in_stock_products}", 
                 font=('Segoe UI', 11), foreground='#059669').grid(row=0, column=1, padx=(0, 30), pady=5, sticky='w')
        ttk.Label(stats_frame, text=f"Out of Stock: {out_of_stock_products}", 
                 font=('Segoe UI', 11), foreground='#dc2626').grid(row=0, column=2, padx=(0, 30), pady=5, sticky='w')
        
        ttk.Label(stats_frame, text=f"Total Live Cartons: {total_live_cartons}", 
                 font=('Segoe UI', 11, 'bold')).grid(row=1, column=0, padx=(0, 30), pady=5, sticky='w')
        ttk.Label(stats_frame, text=f"Total Live Pieces: {total_live_pieces}", 
                 font=('Segoe UI', 11, 'bold')).grid(row=1, column=1, padx=(0, 30), pady=5, sticky='w')

        # Create Treeview for table display with better column layout
        columns = ("Product ID", "Product Name", "Cartons (Live)", "Pieces (Live)", 
                   "Damaged/Expired", "Earliest Inwarded", "Earliest Expires", 
                   "Last Outwarded", "Purchase Price per Piece", "Sales Price per Piece", "Avg MRP", "Locations", "Status")
        
        # Create frame for treeview with scrollbars
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(expand=True, fill='both', pady=10)
        
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configure tree styling
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))
        style.configure("Treeview", font=('Segoe UI', 9))
        
        # Vertical scrollbar
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Horizontal scrollbar  
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        # Better column widths for proper display - optimized to fit screen
        col_widths = [80, 140, 70, 70, 90, 90, 90, 90, 85, 85, 70, 100, 80]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col, anchor=tk.CENTER)
            self.tree.column(col, width=width, anchor=tk.CENTER, minwidth=width)
        
        # Populate data
        for product in sorted_aggregated_products:
            status_text = 'In Stock'
            if product['totalLivePieces'] == 0 and product['totalDamagedUnits'] == 0:
                status_text = 'Out of Stock'
            elif product['hasExpiredStock'] and product['totalLivePieces'] == 0:
                status_text = 'All Expired'
            elif product['hasExpiredStock'] or product['hasDamagedStock']:
                status_text = 'Some Damaged/Expired'
            
            avg_purchase_per_piece = product['purchase_per_piece_sum'] / product['purchase_per_piece_count'] if product['purchase_per_piece_count'] else 0
            avg_sales_per_piece = product['sales_per_piece_sum'] / product['sales_per_piece_count'] if product['sales_per_piece_count'] else 0
            avg_mrp = product['mrp_sum'] / product['mrp_count'] if product['mrp_count'] else 0
            
            # Insert row with proper formatting
            item_id = self.tree.insert("", tk.END, values=(
                product['productId'],
                product['productName'],
                product['totalLiveCartons'],
                product['totalLivePieces'],
                product['totalDamagedUnits'],
                self.format_date(product['earliestInwarded']) if product['earliestInwarded'].year != 9999 else 'N/A',
                self.format_date(product['earliestExpiry']) if product['earliestExpiry'].year != 9999 else 'N/A',
                self.format_date(product['latestOutwarded']) if product['latestOutwarded'].year != 1 else 'N/A',
                f"₹{avg_purchase_per_piece:.2f}" if avg_purchase_per_piece else 'N/A',
                f"₹{avg_sales_per_piece:.2f}" if avg_sales_per_piece else 'N/A',
                f"₹{avg_mrp:.2f}" if avg_mrp else 'N/A',
                ", ".join(sorted(list(product['locations']))),
                status_text
            ))
            
            # Color coding based on status
            if status_text == 'Out of Stock':
                self.tree.set(item_id, 'Status', '❌ ' + status_text)
            elif status_text == 'In Stock':
                self.tree.set(item_id, 'Status', '✅ ' + status_text)
            elif 'Damaged' in status_text or 'Expired' in status_text:
                self.tree.set(item_id, 'Status', '⚠️ ' + status_text)
        
        # Add detailed carton information section
        self.create_detailed_carton_view(company_stock)
    
    def create_detailed_carton_view(self, company_stock):
        """Create detailed view of all individual cartons with Carton IDs."""
        # Detailed Carton Information Section
        ttk.Label(self.content_frame, text="🔍 Detailed Carton Information (All Cartons with IDs for Updates)", 
                 font=('Segoe UI', 14, 'bold')).pack(pady=(20, 10))
        
        # Create frame for detailed carton treeview
        detail_tree_frame = ttk.Frame(self.content_frame)
        detail_tree_frame.pack(expand=True, fill='both', pady=10)
        
        # Detailed carton columns including Carton ID prominently
        detail_columns = ("Carton ID", "Product ID", "Product Name", "Location", "Quantity", 
                         "Damaged", "Purchase Price", "Sales Price", "MRP", "Inwarded", "Expires", "Status")
        
        self.detail_tree = ttk.Treeview(detail_tree_frame, columns=detail_columns, show='headings', height=12)
        
        # Configure detail tree styling
        style = ttk.Style()
        style.configure("Detail.Treeview", rowheight=25)
        style.configure("Detail.Treeview.Heading", font=('Segoe UI', 10, 'bold'))
        style.configure("Detail.Treeview", font=('Segoe UI', 9))
        
        # Configure columns with appropriate widths
        for col, width in zip(detail_columns, [100, 90, 180, 80, 70, 70, 80, 80, 80, 90, 90, 100]):
            self.detail_tree.heading(col, text=col)
            self.detail_tree.column(col, width=width, anchor='center')
        
        # Vertical scrollbar for detailed view
        detail_v_scrollbar = ttk.Scrollbar(detail_tree_frame, orient="vertical", command=self.detail_tree.yview)
        self.detail_tree.configure(yscrollcommand=detail_v_scrollbar.set)
        
        # Horizontal scrollbar for detailed view
        detail_h_scrollbar = ttk.Scrollbar(detail_tree_frame, orient="horizontal", command=self.detail_tree.xview)
        self.detail_tree.configure(xscrollcommand=detail_h_scrollbar.set)
        
        # Pack scrollbars and tree
        self.detail_tree.pack(side="left", fill="both", expand=True)
        detail_v_scrollbar.pack(side="right", fill="y")
        detail_h_scrollbar.pack(side="bottom", fill="x")
        
        # Sort cartons by Product ID, then by Carton ID
        sorted_cartons = sorted(company_stock, key=lambda x: (x['product_id'], x['carton_id']))
        current_date = datetime.date.today()
        
        # Populate detailed carton information
        for carton in sorted_cartons:
            # Determine carton status
            carton_status = "Active"
            if carton['date_outwarded']:
                carton_status = "Outwarded"
            elif carton['expiry_date']:
                try:
                    expiry_date_obj = self.parse_date(carton['expiry_date'])
                    if expiry_date_obj and expiry_date_obj <= current_date:
                        carton_status = "Expired"
                    elif expiry_date_obj and (expiry_date_obj - current_date).days <= 30:
                        carton_status = "Expiring Soon"
                except:
                    pass
            
            if carton['damaged_units'] > 0 and carton_status == "Active":
                carton_status = "Has Damage"
            
            # Insert carton data
            item_id = self.detail_tree.insert('', 'end', values=(
                carton['carton_id'],
                carton['product_id'],
                carton['product_name'],
                carton['location'],
                carton['quantity_per_carton'],
                carton['damaged_units'],
                f"₹{carton.get('purchase_price', 0):.2f}",
                f"₹{carton.get('sales_price', 0):.2f}",
                f"₹{carton.get('mrp', 0):.2f}" if carton.get('mrp', 0) > 0 else 'N/A',
                carton['date_inwarded'],
                carton['expiry_date'] if carton['expiry_date'] else 'N/A',
                carton_status
            ))
            
            # Color coding for carton status
            if carton_status == 'Outwarded':
                self.detail_tree.set(item_id, 'Status', '❌ ' + carton_status)
            elif carton_status == 'Expired':
                self.detail_tree.set(item_id, 'Status', '🔴 ' + carton_status)
            elif carton_status == 'Expiring Soon':
                self.detail_tree.set(item_id, 'Status', '🟡 ' + carton_status)
            elif carton_status == 'Has Damage':
                self.detail_tree.set(item_id, 'Status', '⚠️ ' + carton_status)
            else:
                self.detail_tree.set(item_id, 'Status', '✅ ' + carton_status)
        
        # Add instruction label
        ttk.Label(self.content_frame, 
                 text="💡 Tip: Use the Carton ID from above to update individual cartons in the 'Update Carton' tab",
                 font=('Segoe UI', 11, 'italic')).pack(pady=(10, 0))
