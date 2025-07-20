import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import datetime
import os

# --- Modern Dark Color Palette ---
PRIMARY_COLOR = '#3b82f6'  # Blue-500
ACCENT_COLOR = '#1e293b'   # Slate-800
HEADER_BG = '#0f172a'      # Slate-900
HEADER_FG = '#f1f5f9'      # Slate-100
BUTTON_BG = '#2563eb'
BUTTON_FG = '#f1f5f9'
BUTTON_HOVER_BG = '#1d4ed8'
FRAME_BG = '#0f172a'        # Slate-900
ENTRY_BG = '#1e293b'
ENTRY_FG = '#f1f5f9'
LABEL_FG = '#f1f5f9'
TREE_HEADER_BG = '#334155'
TREE_HEADER_FG = '#f1f5f9'
TREE_ROW_ALT = '#1e293b'
TREE_ROW_NORM = '#0f172a'

# --- Configuration ---
DATA_DIR = "data"

# Remove hardcoded company files; will be set dynamically
COMPANY_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'company_config.json')

# Ensure data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- Data Loading and Saving Functions ---
def load_stock_data(filepath):
    """Loads stock data from a JSON file."""
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f:
            json.dump([], f)
        return []
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_stock_data(data, filepath):
    """Saves stock data to a JSON file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        messagebox.showerror("Save Error", f"Error saving data to {filepath}: {e}")

# --- Helper to manage companies and their files ---
def load_company_configs():
    if not os.path.exists(COMPANY_CONFIG_FILE):
        return {}
    try:
        with open(COMPANY_CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_company_configs(configs):
    try:
        with open(COMPANY_CONFIG_FILE, 'w') as f:
            json.dump(configs, f, indent=4)
    except Exception as e:
        messagebox.showerror("Save Error", f"Error saving company configs: {e}")

# --- Global Stock Data (will be loaded on app start) ---
# apex_stock_data = []
# tech_stock_data = []

def load_initial_data():
    # No longer used; replaced by load_selected_company_data
    pass

# --- Helper Functions (ported from previous Python logic) ---
def format_date(date_obj):
    if not date_obj: return 'N/A'
    if isinstance(date_obj, datetime.date):
        return date_obj.strftime("%Y-%m-%d")
    return date_obj # Assume it's already a string if not a date object

def parse_date(date_str):
    if not date_str: return None
    try:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

def _get_product_for_action(query, all_stock_data):
    query_lower = query.lower().strip()
    potential_products = {}

    for carton in all_stock_data:
        if carton['product_id'].lower() == query_lower:
            potential_products[carton['product_id']] = carton['product_name']
            break
    
    if not potential_products:
        for carton in all_stock_data:
            if query_lower in carton['product_name'].lower() or \
               carton['product_name'].lower() in query_lower:
                potential_products[carton['product_id']] = carton['product_name']

    if not potential_products:
        return None, None, f"Sorry, I couldn't find any stock matching '{query}'. Please try a different name or ID."
    elif len(potential_products) > 1:
        matched_names = [f"{pid} ({pname})" for pid, pname in potential_products.items()]
        return None, None, f"I found multiple products matching '{query}': {', '.join(matched_names)}. Please be more specific or provide the exact Product ID."
    else:
        product_id = list(potential_products.keys())[0]
        product_name = potential_products[product_id]
        return product_id, product_name, ''

def get_product_summary_text(query, all_stock_data):
    product_id_found, product_name_found, identification_message = _get_product_for_action(query, all_stock_data)

    if not product_id_found:
        return identification_message

    found_cartons = [carton for carton in all_stock_data if carton['product_id'] == product_id_found]

    # Collect all unique MRPs for this product
    unique_mrps = sorted(set([carton.get('mrp', 0) for carton in found_cartons if carton.get('mrp') is not None]))
    mrp_text = ''
    if unique_mrps:
        if len(unique_mrps) == 1:
            mrp_text = f"MRP: ₹{unique_mrps[0]:.2f}"
        else:
            mrp_text = "MRPs: " + ", ".join([f"₹{mrp:.2f}" for mrp in unique_mrps])

    total_live_units = 0
    total_damaged_units = 0
    total_expired_units = 0
    unique_locations = set()
    active_carton_details = []
    outwarded_cartons_info = []

    oldest_inwarded_date = datetime.date(9999, 12, 31)
    oldest_inwarded_carton_id = None
    nearest_expiry_date = datetime.date(9999, 12, 31)
    nearest_expiry_carton_id = None

    current_date = datetime.date.today()

    for carton in found_cartons:
        unique_locations.add(carton['location'])

        if carton['date_outwarded'] is None:
            is_expired = False
            if carton['expiry_date']:
                try:
                    expiry_date_obj = parse_date(carton['expiry_date'])
                    if expiry_date_obj and expiry_date_obj <= current_date:
                        is_expired = True
                        total_expired_units += carton['quantity_per_carton']
                    elif expiry_date_obj and expiry_date_obj < nearest_expiry_date:
                        nearest_expiry_date = expiry_date_obj
                        nearest_expiry_carton_id = carton['carton_id']
                except (TypeError, ValueError):
                    pass
            
            if is_expired:
                total_damaged_units += carton['quantity_per_carton']
            else:
                total_live_units += carton['quantity_per_carton']
                total_damaged_units += carton['damaged_units']

            active_carton_details.append({
                'carton_id': carton['carton_id'],
                'quantity_per_carton': carton['quantity_per_carton'],
                'damaged_units': carton['damaged_units'],
                'date_inwarded': carton['date_inwarded'],
                'expiry_date': carton['expiry_date'],
                'is_expired': is_expired,
            })

            if not is_expired:
                inward_date_obj = parse_date(carton['date_inwarded'])
                if inward_date_obj and inward_date_obj < oldest_inwarded_date:
                    oldest_inwarded_date = inward_date_obj
                    oldest_inwarded_carton_id = carton['carton_id']
        else:
            outwarded_cartons_info.append(carton['carton_id'])

    summary_lines = []
    summary_lines.append(f"Searching for {product_name_found} ({product_id_found}).\n")
    if mrp_text:
        summary_lines.append(mrp_text)
    summary_lines.append("---")
    summary_lines.append(f"Total Live Sellable Stock: {total_live_units} units (across {len([c for c in active_carton_details if not c['is_expired']])} active non-expired carton(s)).")
    summary_lines.append(f"Total Damaged/Expired Stock: {total_damaged_units} units ({total_expired_units} expired, {total_damaged_units - total_expired_units} physically damaged).")
    summary_lines.append(f"Locations: {', '.join(sorted(list(unique_locations)))}")

    if active_carton_details:
        summary_lines.append("\nCarton Details (Live Stock):")
        active_carton_details.sort(key=lambda x: (
            parse_date(x['expiry_date']) or datetime.date(9999, 12, 31),
            parse_date(x['date_inwarded']) or datetime.date(1, 1, 1)
        ))

        for detail in active_carton_details:
            qty_status = f"{detail['quantity_per_carton']} units"
            if detail['damaged_units'] > 0:
                qty_status += f" ({detail['damaged_units']} physically damaged)"
            
            carton_remarks = []
            if detail['is_expired']:
                carton_remarks.append("EXPIRED")
            
            remark_text = f" ({', '.join(carton_remarks)})" if carton_remarks else ""

            summary_lines.append(
                f"  - Carton {detail['carton_id']}: {qty_status}{remark_text}. " +
                f"Inwarded: {detail['date_inwarded']}. " +
                f"Expires: {detail['expiry_date'] or 'N/A'}."
            )
    
    remarks = []
    if oldest_inwarded_carton_id and oldest_inwarded_date != datetime.date(9999, 12, 31):
        days_old = (current_date - oldest_inwarded_date).days
        if days_old > 90:
            remarks.append(f"Carton {oldest_inwarded_carton_id} (Inwarded: {format_date(oldest_inwarded_date)}) is older stock. Consider prioritizing its sale (FIFO).")
        else:
            remarks.append(f"The oldest active sellable stock is Carton {oldest_inwarded_carton_id} (Inwarded: {format_date(oldest_inwarded_date)}).")
    
    if nearest_expiry_carton_id and nearest_expiry_date != datetime.date(9999, 12, 31):
        days_to_expiry = (nearest_expiry_date - current_date).days
        if days_to_expiry <= 0:
            pass
        elif days_to_expiry <= 60:
            remarks.append(f"URGENT! Carton {nearest_expiry_carton_id} expires on {format_date(nearest_expiry_date)} (in {days_to_expiry} days). Prioritize selling this carton (FEFO).")
        elif days_to_expiry <= 180:
            remarks.append(f"Warning: Carton {nearest_expiry_carton_id} expires on {format_date(nearest_expiry_date)} (in {days_to_expiry} days). Keep an eye on this stock.")
        else:
            remarks.append(f"The earliest expiring active sellable stock is Carton {nearest_expiry_carton_id} (Expires: {format_date(nearest_expiry_date)}).")
        
    if outwarded_cartons_info:
        remarks.append(f"Some cartons ({', '.join(outwarded_cartons_info)}) of this product have been outwarded previously.")

    if remarks:
        summary_lines.append("\nRemarks:")
        summary_lines.extend([f"  - {r}" for r in remarks])

    return "\n".join(summary_lines)

# --- Main GUI Application Class ---
class StockApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stock Mitra")
        self.geometry("1100x750") # Larger size for modern look
        self.configure(bg=FRAME_BG)

        # --- Company selection on startup ---
        self.company_configs = load_company_configs()
        self.selected_company = None
        self.selected_json_file = None
        self.stock_data = []
        self.menu_bar = tk.Menu(self)
        self.create_menu_bar()
        self.config(menu=self.menu_bar)
        self.prompt_for_company()
        if not self.selected_company or not self.selected_json_file:
            self.destroy()
            return
        self.load_selected_company_data()

        # --- Modern Style Configuration ---
        # Use a large, readable, professional sans-serif font
        self.base_font = ('Segoe UI', 14)  # Large base font
        self.heading_font = ('Segoe UI', 22, 'bold')
        self.subheading_font = ('Segoe UI', 18, 'bold')
        self.label_font = ('Segoe UI', 15)
        self.button_font = ('Segoe UI', 15, 'bold')
        self.entry_font = ('Segoe UI', 15)
        self.tree_font = ('Segoe UI', 15)
        self.tree_heading_font = ('Segoe UI', 17, 'bold')

        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('TFrame', background=FRAME_BG)
        self.style.configure('TLabel', background=FRAME_BG, foreground=LABEL_FG, font=self.label_font)
        self.style.configure('Header.TLabel', background=HEADER_BG, foreground=HEADER_FG, font=self.heading_font)
        self.style.configure('SubHeader.TLabel', background=FRAME_BG, foreground=PRIMARY_COLOR, font=self.subheading_font)
        self.style.configure('TButton', font=self.button_font, padding=12, background=BUTTON_BG, foreground=BUTTON_FG, borderwidth=0)
        self.style.map('TButton',
            background=[('active', BUTTON_HOVER_BG), ('!disabled', BUTTON_BG)],
            foreground=[('active', BUTTON_FG), ('!disabled', BUTTON_FG)])
        self.style.configure('TEntry', padding=10, font=self.entry_font, fieldbackground=ENTRY_BG, foreground=ENTRY_FG)
        self.style.configure('TCombobox', padding=10, font=self.entry_font, fieldbackground=ENTRY_BG, foreground=ENTRY_FG)
        self.style.configure('TNotebook', background=FRAME_BG, tabposition='n')
        self.style.configure('TNotebook.Tab', font=self.button_font, padding=[20, 12], background=ACCENT_COLOR, foreground=PRIMARY_COLOR)
        self.style.map('TNotebook.Tab',
            background=[('selected', '#334155')],
            foreground=[('selected', PRIMARY_COLOR)])
        self.style.configure('Treeview', font=self.tree_font, rowheight=36, fieldbackground=FRAME_BG, background=FRAME_BG, foreground=LABEL_FG)
        self.style.configure('Treeview.Heading', font=self.tree_heading_font, background=TREE_HEADER_BG, foreground=TREE_HEADER_FG)
        self.style.map('Treeview', background=[('selected', '#2563eb')], foreground=[('selected', '#f1f5f9')])
        self.style.configure('TLabelframe', background=FRAME_BG, borderwidth=0)
        self.style.configure('TLabelframe.Label', background=FRAME_BG, foreground=PRIMARY_COLOR)

        # --- App Header Bar ---
        header = ttk.Frame(self, style='TFrame')
        header.pack(fill='x', side='top')
        header_label = ttk.Label(header, text="Stock Mitra", style='Header.TLabel', anchor='center')
        header_label.pack(fill='x', pady=(0, 8))

        # --- Greeting Message ---
        self.after(100, lambda: messagebox.showinfo("Welcome to Stock Mitra", f"Hello! Welcome to Stock Mitra.\n\nYou are managing stock for: {self.selected_company}"))

        # --- Main Notebook ---
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=20, pady=20)

        # --- Dashboard Tab ---
        self.dashboard_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.create_dashboard_widgets(self.dashboard_frame)

        # --- Find Stock Tab ---
        self.find_stock_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.find_stock_frame, text="Find Stock")
        self.create_find_stock_widgets(self.find_stock_frame)

        # --- Add Stock Tab ---
        self.add_stock_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.add_stock_frame, text="Add Stock")
        self.create_add_stock_widgets(self.add_stock_frame)

        # --- Sell Stock Tab ---
        self.sell_stock_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.sell_stock_frame, text="Sell Stock")
        self.create_sell_stock_widgets(self.sell_stock_frame)

        # --- Update Carton Tab ---
        self.update_carton_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.update_carton_frame, text="Update Carton")
        self.create_update_carton_widgets(self.update_carton_frame)

        # --- Company Stock View Tab (Dynamic) ---
        self.company_stock_view_frame = ttk.Frame(self.notebook, padding="20")
        # self.create_company_stock_view_widgets(self.company_stock_view_frame)  # Removed: method does not exist

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)
        load_initial_data() # Load data when app starts
        self.update_find_stock_suggestions() # Ensure suggestions are updated after data loads
        self.update_dashboard()

    def show_message(self, type, text):
        # Using messagebox for critical errors/success, or a status bar for transient messages
        if type == 'success':
            messagebox.showinfo("Success", text)
        elif type == 'error':
            messagebox.showerror("Error", text)
        elif type == 'info':
            messagebox.showinfo("Info", text)
        elif type == 'warning':
            messagebox.showwarning("Warning", text)

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # --- Dashboard Tab ---
        self.dashboard_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.create_dashboard_widgets(self.dashboard_frame)

        # --- Find Stock Tab ---
        self.find_stock_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.find_stock_frame, text="Find Stock")
        self.create_find_stock_widgets(self.find_stock_frame)

        # --- Add Stock Tab ---
        self.add_stock_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.add_stock_frame, text="Add Stock")
        self.create_add_stock_widgets(self.add_stock_frame)

        # --- Sell Stock Tab ---
        self.sell_stock_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.sell_stock_frame, text="Sell Stock")
        self.create_sell_stock_widgets(self.sell_stock_frame)

        # --- Update Carton Tab ---
        self.update_carton_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.update_carton_frame, text="Update Carton")
        self.create_update_carton_widgets(self.update_carton_frame)

        # --- Company Stock View Tab (Dynamic) ---
        self.company_stock_view_frame = ttk.Frame(self.notebook, padding="10")
        # self.create_company_stock_view_widgets(self.company_stock_view_frame)  # Removed: method does not exist

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        # Refresh dashboard when returning to it
        selected_tab_text = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab_text == "Dashboard":
            self.update_dashboard()
        # If navigating away from a dynamically added company stock tab, hide it
        if selected_tab_text != self.notebook.tab(self.company_stock_view_frame, "text") and \
           self.company_stock_view_frame.winfo_ismapped():
            # Check if the current tab is not the company stock view, and if it's currently shown
            # This logic needs to be careful not to hide if we're just switching between other main tabs
            pass # We'll handle showing/hiding dynamically when 'View Details' is clicked

    def update_dashboard(self):
        all_stock = self.stock_data
        current_date = datetime.date.today()

        total_live = 0
        total_damaged_expired = 0

        for c in all_stock:
            if c['date_outwarded'] is None:
                is_expired = False
                if c['expiry_date']:
                    expiry_date_obj = parse_date(c['expiry_date'])
                    if expiry_date_obj and expiry_date_obj <= current_date:
                        is_expired = True
                
                if is_expired:
                    total_damaged_expired += c['quantity_per_carton']
                else:
                    total_live += c['quantity_per_carton']
                    total_damaged_expired += c['damaged_units']

        self.total_live_label.config(text=f"{total_live}")
        self.total_damaged_expired_label.config(text=f"{total_damaged_expired}")
        self.total_cartons_label.config(text=f"{len(all_stock)}")

    def create_dashboard_widgets(self, parent_frame):
        # Dashboard Overview
        ttk.Label(parent_frame, text="Dashboard Overview", font=self.heading_font, background=FRAME_BG, foreground=PRIMARY_COLOR).pack(pady=(0, 18))

        stats_frame = ttk.Frame(parent_frame, style='TFrame')
        stats_frame.pack(pady=10)

        # Total Live Stock
        live_frame = ttk.Frame(stats_frame, padding="16", style='TFrame')
        live_frame.grid(row=0, column=0, padx=12, pady=8)
        ttk.Label(live_frame, text="Total Live Sellable Stock", font=self.subheading_font, background=FRAME_BG, foreground=PRIMARY_COLOR).pack(pady=(0, 8))
        self.total_live_label = ttk.Label(live_frame, text="0", font=('Segoe UI', 28, 'bold'), foreground=PRIMARY_COLOR, background=FRAME_BG)
        self.total_live_label.pack()

        # Total Damaged/Expired
        damaged_frame = ttk.Frame(stats_frame, padding="16", style='TFrame')
        damaged_frame.grid(row=0, column=1, padx=12, pady=8)
        ttk.Label(damaged_frame, text="Total Damaged/Expired", font=self.subheading_font, background=FRAME_BG, foreground='#dc2626').pack(pady=(0, 8))
        self.total_damaged_expired_label = ttk.Label(damaged_frame, text="0", font=('Segoe UI', 28, 'bold'), foreground='#dc2626', background=FRAME_BG)
        self.total_damaged_expired_label.pack()

        # Total Cartons
        cartons_frame = ttk.Frame(stats_frame, padding="16", style='TFrame')
        cartons_frame.grid(row=0, column=2, padx=12, pady=8)
        ttk.Label(cartons_frame, text="Total Cartons", font=self.subheading_font, background=FRAME_BG, foreground='#059669').pack(pady=(0, 8))
        self.total_cartons_label = ttk.Label(cartons_frame, text="0", font=('Segoe UI', 28, 'bold'), foreground='#059669', background=FRAME_BG)
        self.total_cartons_label.pack()

        # Company Stock Details Button
        ttk.Button(parent_frame, text=f"View {self.selected_company} Stock Details", style='TButton', command=lambda: self.show_company_stock(self.selected_company)).pack(pady=24)

    def show_company_stock(self, company_name):
        # Add the company stock view tab if not already present
        if self.company_stock_view_frame not in self.notebook.tabs():
            self.notebook.add(self.company_stock_view_frame, text=f"{company_name} Stock")
        else:
            self.notebook.tab(self.company_stock_view_frame, text=f"{company_name} Stock")
        self.notebook.select(self.company_stock_view_frame) # Switch to the tab
        self.update_company_stock_view(company_name) # Populate its data

    def update_company_stock_view(self, company_name):
        # Clear previous content
        for widget in self.company_stock_view_frame.winfo_children():
            widget.destroy()

        ttk.Button(self.company_stock_view_frame, text="← Back to Dashboard", command=lambda: self.notebook.select(self.dashboard_frame)).pack(anchor='nw', pady=5)
        ttk.Label(self.company_stock_view_frame, text=f"{company_name} Stock Details", font=('Arial', 16, 'bold')).pack(pady=10)

        company_stock = self.stock_data
        current_date = datetime.date.today()

        # Aggregate data by product_id
        aggregated_products = {}
        for carton in company_stock:
            product_id = carton['product_id']
            if product_id not in aggregated_products:
                aggregated_products[product_id] = {
                    'productId': carton['product_id'],
                    'productName': carton['product_name'],
                    'mrp': carton.get('mrp'),
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

            if carton['date_outwarded'] is None:
                product['hasActiveStock'] = True
                is_expired = False
                if carton['expiry_date']:
                    expiry_date_obj = parse_date(carton['expiry_date'])
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
                    inward_date_obj = parse_date(carton['date_inwarded'])
                    if inward_date_obj and inward_date_obj < product['earliestInwarded']:
                        product['earliestInwarded'] = inward_date_obj
            else:
                outward_date_obj = parse_date(carton['date_outwarded'])
                if outward_date_obj and outward_date_obj > product['latestOutwarded']:
                    product['latestOutwarded'] = outward_date_obj

        sorted_aggregated_products = list(aggregated_products.values())
        sorted_aggregated_products.sort(key=lambda x: x['productId'])

        # Create Treeview for table display
        columns = ("Product ID", "Product Name", "Cartons (Live)", "Pieces (Live)", 
                   "Damaged/Expired", "Earliest Inwarded", "Earliest Expires", 
                   "Last Outwarded", "MRP", "Locations", "Status")
        
        self.tree = ttk.Treeview(self.company_stock_view_frame, columns=columns, show='headings')
        self.tree.pack(expand=True, fill='both', pady=10)

        # Define column headings
        for col in columns:
            self.tree.heading(col, text=col, anchor=tk.W)
            self.tree.column(col, width=100, anchor=tk.W) # Default width

        # Adjust specific column widths
        self.tree.column("Product Name", width=150)
        self.tree.column("Locations", width=120)
        self.tree.column("Damaged/Expired", width=100)
        self.tree.column("Earliest Inwarded", width=100)
        self.tree.column("Earliest Expires", width=100)
        self.tree.column("Last Outwarded", width=100)
        self.tree.column("MRP", width=60)
        self.tree.column("Status", width=80)

        # Populate data
        for product in sorted_aggregated_products:
            status_text = 'In Stock'
            if product['totalLivePieces'] == 0 and product['totalDamagedUnits'] == 0:
                status_text = 'Out of Stock'
            elif product['hasExpiredStock'] and product['totalLivePieces'] == 0:
                status_text = 'All Expired'
            elif product['hasExpiredStock'] or product['hasDamagedStock']:
                status_text = 'Some Damaged/Expired'
            
            self.tree.insert("", tk.END, values=(
                product['productId'],
                product['productName'],
                product['totalLiveCartons'],
                product['totalLivePieces'],
                product['totalDamagedUnits'],
                format_date(product['earliestInwarded']) if product['earliestInwarded'].year != 9999 else 'N/A',
                format_date(product['earliestExpiry']) if product['earliestExpiry'].year != 9999 else 'N/A',
                format_date(product['latestOutwarded']) if product['latestOutwarded'].year != 1 else 'N/A',
                f"₹{product['mrp']:.2f}" if product['mrp'] is not None else 'N/A',
                ", ".join(sorted(list(product['locations']))),
                status_text
            ))

    def create_find_stock_widgets(self, parent_frame):
        ttk.Label(parent_frame, text="Find Stock", font=self.heading_font, background=FRAME_BG, foreground=PRIMARY_COLOR).pack(pady=(0, 18))

        search_frame = ttk.Frame(parent_frame, style='TFrame')
        search_frame.pack(pady=5)

        ttk.Label(search_frame, text="Product ID or Name:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.find_stock_query_entry = ttk.Entry(search_frame, width=60)
        self.find_stock_query_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.find_stock_query_entry.bind("<Return>", lambda event: self.perform_find_stock())
        self.find_stock_query_entry.bind('<KeyRelease>', self.show_find_stock_suggestions)

        ttk.Button(search_frame, text="Search", style='TButton', command=self.perform_find_stock).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(search_frame, text="Clear", style='TButton', command=self.clear_find_stock).grid(row=0, column=3, padx=5, pady=5)

        self.find_stock_results_text = tk.Text(
            parent_frame, wrap=tk.WORD, height=20, width=90,
            font=self.entry_font, bg=ACCENT_COLOR, fg=LABEL_FG,
            relief='flat', padx=18, pady=18
        )
        self.find_stock_results_text.pack(pady=16, padx=5, fill='both', expand=True)
        self.find_stock_results_text.config(state=tk.DISABLED) # Make it read-only

        # Prepare suggestions list (product IDs and names)
        self.all_product_suggestions = []
        # self.update_find_stock_suggestions() # Moved to __init__
        self.suggestion_listbox = None

    def update_find_stock_suggestions(self):
        # Call this after loading data or when data changes
        all_stock = self.stock_data
        suggestions = set()
        self.suggestion_map = {}  # Map display string to (product_id, product_name, mrp)
        for item in all_stock:
            display = f"{item['product_id']} - {item['product_name']} (MRP: ₹{item.get('mrp', 0):.2f})"
            suggestions.add(display)
            self.suggestion_map[display] = (item['product_id'], item['product_name'], item.get('mrp', 0))
        self.all_product_suggestions = sorted(suggestions)
        print("Suggestions loaded:", self.all_product_suggestions)  # Debug

    def show_find_stock_suggestions(self, event):
        print("show_find_stock_suggestions called")  # Debug
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
        self.suggestion_window = tk.Toplevel(self)
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
        if self.suggestion_listbox:
            selection = self.suggestion_listbox.curselection()
            if selection:
                display_value = self.suggestion_listbox.get(selection[0])
                # Fill the entry with the product_id (or product_name if you prefer)
                product_id, product_name, mrp = self.suggestion_map.get(display_value, (display_value, '', 0))
                self.find_stock_query_entry.delete(0, tk.END)
                self.find_stock_query_entry.insert(0, product_id)
            self.close_find_stock_suggestions()

    def close_find_stock_suggestions(self):
        if hasattr(self, 'suggestion_window') and self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None
        self.suggestion_listbox = None

    def move_suggestion_up(self, event):
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
        if hasattr(self, 'suggestion_window') and self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None
        self.suggestion_listbox = None
        query = self.find_stock_query_entry.get().strip()
        if not query:
            self.show_message('error', 'Please enter a product ID or name to search.')
            return
        all_stock_data_combined = self.stock_data
        summary = get_product_summary_text(query, all_stock_data_combined)
        self.find_stock_results_text.config(state=tk.NORMAL) # Enable editing
        self.find_stock_results_text.delete(1.0, tk.END) # Clear previous
        self.find_stock_results_text.insert(tk.END, summary)
        self.find_stock_results_text.config(state=tk.DISABLED) # Disable editing
        if summary.startswith("Sorry,") or summary.startswith("I found multiple products"):
            self.show_message('error', summary.split('\n')[0]) # Show first line as error
        else:
            self.show_message('success', 'Search results displayed.')

    def clear_find_stock(self):
        self.find_stock_query_entry.delete(0, tk.END)
        self.find_stock_results_text.config(state=tk.NORMAL)
        self.find_stock_results_text.delete(1.0, tk.END)
        self.find_stock_results_text.config(state=tk.DISABLED)
        if hasattr(self, 'suggestion_window') and self.suggestion_window:
            self.suggestion_window.destroy()
            self.suggestion_window = None
        self.suggestion_listbox = None
        self.show_message('info', 'Find Stock search cleared.')

    def create_add_stock_widgets(self, parent_frame):
        ttk.Label(parent_frame, text="Add New Stock", font=self.heading_font, background=FRAME_BG, foreground=PRIMARY_COLOR).pack(pady=(0, 18))

        # --- Main horizontal layout frame ---
        main_content_frame = ttk.Frame(parent_frame)
        main_content_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Left: Product Details
        details_frame = ttk.Frame(main_content_frame)
        details_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 20), pady=5)

        # Right: Carton Details (with vertical scroll)
        cartons_frame = ttk.Frame(main_content_frame)
        cartons_frame.grid(row=0, column=1, sticky='nsew', padx=(20, 0), pady=5)
        main_content_frame.columnconfigure(0, weight=1)
        main_content_frame.columnconfigure(1, weight=1)
        main_content_frame.rowconfigure(0, weight=1)

        # Product Details on the left (updated)
        ttk.Label(details_frame, text="Company Name:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.add_company_label = ttk.Label(details_frame, text=self.selected_company, font=self.label_font)
        self.add_company_label.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        ttk.Label(details_frame, text="Product ID:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.add_product_id_entry = ttk.Entry(details_frame)
        self.add_product_id_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        ttk.Label(details_frame, text="Product Name:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.add_product_name_entry = ttk.Entry(details_frame)
        self.add_product_name_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
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
        self.add_num_cartons_spinbox.bind('<KeyRelease>', lambda e: self.update_add_carton_details_fields())
        self.add_num_cartons_spinbox.bind('<<Increment>>', lambda e: self.update_add_carton_details_fields())
        self.add_num_cartons_spinbox.bind('<<Decrement>>', lambda e: self.update_add_carton_details_fields())
        self.add_num_cartons_var.trace_add('write', lambda *args: self.update_add_carton_details_fields())
        details_frame.columnconfigure(1, weight=1)

        # Carton Details on the right (VERTICAL SCROLLABLE)
        self.carton_canvas = tk.Canvas(cartons_frame, borderwidth=0, background=FRAME_BG, height=350)
        self.carton_scrollbar = ttk.Scrollbar(cartons_frame, orient="vertical", command=self.carton_canvas.yview)
        self.carton_canvas.configure(yscrollcommand=self.carton_scrollbar.set)
        self.carton_canvas.pack(side="left", fill="both", expand=True)
        self.carton_scrollbar.pack(side="right", fill="y")
        self.add_carton_details_frame = ttk.Frame(self.carton_canvas, style='TFrame')
        self.carton_canvas.create_window((0, 0), window=self.add_carton_details_frame, anchor="nw")
        def _on_frame_configure(event):
            self.carton_canvas.configure(scrollregion=self.carton_canvas.bbox("all"))
        self.add_carton_details_frame.bind("<Configure>", _on_frame_configure)
        def _on_mousewheel(event):
            self.carton_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.carton_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.carton_entries = [] # To store Entry widgets for quantity, damaged, MRP
        self.update_add_carton_details_fields() # Initial call to create fields for 1 carton

        # Buttons centered below both columns
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(pady=18)
        ttk.Button(button_frame, text="Clear Form", style='TButton', command=self.clear_add_stock_form).pack(side='left', padx=16)
        ttk.Button(button_frame, text="Add Stock", style='TButton', command=self.perform_add_stock).pack(side='left', padx=16)

    def _bind_carton_mousewheel_horizontal(self):
        self.carton_details_canvas.bind_all('<Shift-MouseWheel>', self._on_carton_mousewheel_horizontal)

    def _unbind_carton_mousewheel_horizontal(self):
        self.carton_details_canvas.unbind_all('<Shift-MouseWheel>')

    def _on_carton_mousewheel_horizontal(self, event):
        self.carton_details_canvas.xview_scroll(int(-1*(event.delta/120)), 'units')

    def update_add_carton_details_fields(self):
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
            ttk.Label(carton_label_frame, text="Pieces (Units):", font=self.label_font).grid(row=0, column=0, padx=5, pady=2, sticky='w')
            qty_entry = ttk.Entry(carton_label_frame, font=self.entry_font)
            qty_entry.grid(row=1, column=0, padx=5, pady=2, sticky='ew')
            ttk.Label(carton_label_frame, text="Damaged Units:", font=self.label_font).grid(row=2, column=0, padx=5, pady=2, sticky='w')
            damaged_entry = ttk.Entry(carton_label_frame, font=self.entry_font)
            damaged_entry.grid(row=3, column=0, padx=5, pady=2, sticky='ew')
            damaged_entry.insert(0, "0") # Default to 0 damaged
            ttk.Label(carton_label_frame, text="MRP:", font=self.label_font).grid(row=4, column=0, padx=5, pady=2, sticky='w')
            mrp_entry = ttk.Entry(carton_label_frame, font=self.entry_font)
            mrp_entry.grid(row=5, column=0, padx=5, pady=2, sticky='ew')
            self.carton_entries.append({
                'qty_entry': qty_entry,
                'damaged_entry': damaged_entry,
                'mrp_entry': mrp_entry
            })
            carton_label_frame.columnconfigure(0, weight=1)

    def perform_add_stock(self):
        product_id = self.add_product_id_entry.get().strip().upper()
        product_name = self.add_product_name_entry.get().strip()
        location = self.add_location_entry.get().strip().upper()
        date_inwarded_str = self.add_date_inwarded_entry.get().strip()
        expiry_date_str = self.add_expiry_date_entry.get().strip()
        num_cartons = self.add_num_cartons_var.get()

        if not all([product_id, product_name, location, date_inwarded_str]):
            self.show_message('error', 'Please fill in all required product details.')
            return

        try:
            parse_date(date_inwarded_str)
            if expiry_date_str: parse_date(expiry_date_str)
        except ValueError:
            self.show_message('error', 'Invalid date format. Please use YYYY-MM-DD.')
            return

        cartons_data_for_add = []
        for entry_set in self.carton_entries:
            try:
                qty = int(entry_set['qty_entry'].get())
                damaged = int(entry_set['damaged_entry'].get())
                mrp = float(entry_set['mrp_entry'].get())
                if qty <= 0 or damaged < 0 or damaged > qty or mrp <= 0:
                    raise ValueError
                cartons_data_for_add.append({'quantity': qty, 'damaged': damaged, 'mrp': mrp})
            except ValueError:
                self.show_message('error', 'Please enter valid positive numbers for quantity and MRP, and non-negative for damaged units (damaged <= quantity).')
                return

        # Check for product ID/name conflict
        existing_product = next((item for item in self.stock_data if item['product_id'] == product_id and item['product_name'] != product_name), None)
        if existing_product:
            if not messagebox.askyesno("Warning", f"Product ID {product_id} is already used for '{existing_product['product_name']}'. Are you sure you want to add '{product_name}' with this ID?"):
                self.show_message('info', 'Stock addition cancelled.')
                return

        added_carton_ids = []
        for carton_detail in cartons_data_for_add:
            existing_cartons_for_product = [c for c in self.stock_data if c['product_id'] == product_id]
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
                "company": self.selected_company,
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
            self.stock_data.append(new_carton)
            added_carton_ids.append(carton_id)
        save_stock_data(self.stock_data, self.selected_json_file)
        self.show_message('success', f"Successfully added {len(cartons_data_for_add)} new carton(s) for '{product_name}' ({product_id}). New Carton IDs: {', '.join(added_carton_ids)}")
        self.clear_add_stock_form()
        self.update_dashboard() # Refresh dashboard after adding stock

    def clear_add_stock_form(self):
        self.add_company_label.config(text=self.selected_company)
        self.add_product_id_entry.delete(0, tk.END)
        self.add_product_name_entry.delete(0, tk.END)
        self.add_location_entry.delete(0, tk.END)
        self.add_date_inwarded_entry.delete(0, tk.END)
        self.add_date_inwarded_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
        self.add_expiry_date_entry.delete(0, tk.END)
        self.add_num_cartons_var.set(1)
        self.update_add_carton_details_fields() # Reset carton details fields

    def create_sell_stock_widgets(self, parent_frame):
        ttk.Label(parent_frame, text="Sell Stock", font=('Arial', 16, 'bold')).pack(pady=10)

        product_id_frame = ttk.Frame(parent_frame)
        product_id_frame.pack(pady=5)
        ttk.Label(product_id_frame, text="Product ID or Name:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.sell_product_query_entry = ttk.Entry(product_id_frame, width=40)
        self.sell_product_query_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.sell_product_query_entry.bind("<Return>", lambda event: self.identify_product_for_sale())
        ttk.Button(product_id_frame, text="Find Product", command=self.identify_product_for_sale).grid(row=0, column=2, padx=5, pady=5)

        self.sell_product_summary_label = ttk.Label(parent_frame, text="", wraplength=500, font=('Arial', 10))
        self.sell_product_summary_label.pack(pady=5, padx=5)

        self.sell_quantity_frame = ttk.LabelFrame(parent_frame, text="Quantities to Sell", padding="10")
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

        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_sell_stock_form).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Process Sale", command=self.perform_sell_stock).grid(row=0, column=1, padx=5)

        self.identified_product_id_for_sale = None # Store identified product ID

    def identify_product_for_sale(self):
        query = self.sell_product_query_entry.get().strip()
        if not query:
            self.show_message('error', 'Please enter a product ID or name to identify.')
            return
        
        all_stock_data_combined = self.stock_data
        product_id, product_name, message = _get_product_for_action(query, all_stock_data_combined)

        if product_id:
            self.identified_product_id_for_sale = product_id
            summary_text = get_product_summary_text(product_id, all_stock_data_combined)
            self.sell_product_summary_label.config(text=summary_text)
            self.show_message('info', f"Product identified: {product_name} ({product_id}). Ready to sell.")
        else:
            self.identified_product_id_for_sale = None
            self.sell_product_summary_label.config(text=message)
            self.show_message('error', message)

    def perform_sell_stock(self):
        if not self.identified_product_id_for_sale:
            self.show_message('error', 'Please identify a product to sell first.')
            return

        try:
            num_full_cartons = int(self.sell_num_full_cartons_entry.get())
            num_loose_pieces = int(self.sell_num_loose_pieces_entry.get())
            if num_full_cartons < 0 or num_loose_pieces < 0:
                raise ValueError("Quantities cannot be negative.")
            if num_full_cartons == 0 and num_loose_pieces == 0:
                self.show_message('info', 'No units specified for sale. Action cancelled.')
                return
        except ValueError as e:
            self.show_message('error', f"Invalid quantity: {e}. Please enter non-negative whole numbers.")
            return

        active_sellable_cartons_references = []
        current_date = datetime.date.today()
        for carton in self.stock_data:
            if carton['product_id'] == self.identified_product_id_for_sale and carton['date_outwarded'] is None:
                is_expired = False
                if carton['expiry_date']:
                    expiry_date_obj = parse_date(carton['expiry_date'])
                    if expiry_date_obj and expiry_date_obj <= current_date:
                        is_expired = True
                if not is_expired:
                    active_sellable_cartons_references.append(carton)

        if not active_sellable_cartons_references:
            self.show_message('error', f"No active SELLABLE stock found for '{self.identified_product_id_for_sale}'. All current stock is either outwarded or expired.")
            return

        active_sellable_cartons_references.sort(key=lambda x: parse_date(x['date_inwarded']) or datetime.date(1,1,1))

        total_deducted_units_count = 0
        cartons_effected_summary = []

        cartons_processed_for_full = 0
        idx = 0
        while cartons_processed_for_full < num_full_cartons and idx < len(active_sellable_cartons_references):
            carton = active_sellable_cartons_references[idx]
            if carton['quantity_per_carton'] > 0:
                original_qty_in_carton = carton['quantity_per_carton']
                carton['quantity_per_carton'] = 0
                carton['damaged_units'] = 0
                carton['date_outwarded'] = format_date(current_date)
                carton['last_updated'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                total_deducted_units_count += original_qty_in_carton
                cartons_effected_summary.append(f"{carton['carton_id']} (Full Carton Sold, {original_qty_in_carton} units)")
                cartons_processed_for_full += 1
            idx += 1

        pieces_to_deduct_loose = num_loose_pieces
        while pieces_to_deduct_loose > 0 and idx < len(active_sellable_cartons_references):
            carton = active_sellable_cartons_references[idx]
            if carton['quantity_per_carton'] > 0:
                deduct_from_this_carton = min(pieces_to_deduct_loose, carton['quantity_per_carton'])
                carton['quantity_per_carton'] -= deduct_from_this_carton
                pieces_to_deduct_loose -= deduct_from_this_carton
                total_deducted_units_count += deduct_from_this_carton
                cartons_effected_summary.append(f"{carton['carton_id']} ({deduct_from_this_carton} loose pieces)")

                if carton['quantity_per_carton'] == 0:
                    carton['date_outwarded'] = format_date(current_date)
                    carton['damaged_units'] = 0
                carton['last_updated'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            idx += 1

        save_stock_data(self.stock_data, self.selected_json_file)

        response_message = f"Successfully processed sale for '{self.identified_product_id_for_sale}'. Total units deducted: {total_deducted_units_count}."
        if cartons_effected_summary:
            response_message += f" Units deducted from: {', '.join(cartons_effected_summary)}."

        if cartons_processed_for_full < num_full_cartons or pieces_to_deduct_loose > 0:
            remaining_req_msg = []
            if cartons_processed_for_full < num_full_cartons:
                remaining_cartons_needed = num_full_cartons - cartons_processed_for_full
                remaining_req_msg.append(f"{remaining_cartons_needed} full carton(s)")
            if pieces_to_deduct_loose > 0:
                remaining_req_msg.append(f"{pieces_to_deduct_loose} loose piece(s)")
            response_message += f" Warning: Could not fulfill entire request. Still needed: {', '.join(remaining_req_msg)}."
            self.show_message('warning', response_message)
        else:
            self.show_message('success', response_message)

        self.clear_sell_stock_form()
        self.update_dashboard() # Refresh dashboard after selling stock

    def clear_sell_stock_form(self):
        self.sell_product_query_entry.delete(0, tk.END)
        self.sell_num_full_cartons_entry.delete(0, tk.END)
        self.sell_num_full_cartons_entry.insert(0, "0")
        self.sell_num_loose_pieces_entry.delete(0, tk.END)
        self.sell_num_loose_pieces_entry.insert(0, "0")
        self.sell_product_summary_label.config(text="")
        self.identified_product_id_for_sale = None

    def create_update_carton_widgets(self, parent_frame):
        ttk.Label(parent_frame, text="Update Individual Carton", font=('Arial', 16, 'bold')).pack(pady=10)

        carton_id_frame = ttk.Frame(parent_frame)
        carton_id_frame.pack(pady=5)
        ttk.Label(carton_id_frame, text="Carton ID:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.update_carton_id_entry = ttk.Entry(carton_id_frame, width=40)
        self.update_carton_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.update_carton_id_entry.bind("<Return>", lambda event: self.find_carton_for_update())
        ttk.Button(carton_id_frame, text="Find Carton", command=self.find_carton_for_update).grid(row=0, column=2, padx=5, pady=5)

        self.update_carton_details_label = ttk.Label(parent_frame, text="", wraplength=500, font=('Arial', 10))
        self.update_carton_details_label.pack(pady=5, padx=5)

        self.update_action_frame = ttk.LabelFrame(parent_frame, text="Choose Action", padding="10")
        self.update_action_frame.pack(fill='x', padx=5, pady=10)
        self.update_action_var = tk.StringVar(value="update")
        ttk.Radiobutton(self.update_action_frame, text="Update Quantity/Damaged", variable=self.update_action_var, value="update", command=self.toggle_update_fields).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Radiobutton(self.update_action_frame, text="Delete This Carton", variable=self.update_action_var, value="delete", command=self.toggle_update_fields).grid(row=0, column=1, padx=5, pady=5, sticky='w')

        self.update_fields_frame = ttk.Frame(parent_frame, padding="10")
        self.update_fields_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(self.update_fields_frame, text="New Total Quantity:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.update_new_qty_entry = ttk.Entry(self.update_fields_frame)
        self.update_new_qty_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(self.update_fields_frame, text="New Damaged Units:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.update_new_damaged_entry = ttk.Entry(self.update_fields_frame)
        self.update_new_damaged_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        self.update_fields_frame.columnconfigure(1, weight=1)
        self.toggle_update_fields() # Initial call

        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Clear Form", command=self.clear_update_carton_form).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Perform Action", command=self.perform_update_carton).grid(row=0, column=1, padx=5)

        self.current_carton_for_update = None # Store identified carton object

    def find_carton_for_update(self):
        query_carton_id = self.update_carton_id_entry.get().strip().upper()
        if not query_carton_id:
            self.show_message('error', 'Please enter a Carton ID to find.')
            return

        all_stock_data_combined = self.stock_data
        carton = next((c for c in all_stock_data_combined if c['carton_id'] == query_carton_id), None)

        if carton:
            if carton['date_outwarded'] is not None:
                self.show_message('info', f"Carton {carton['carton_id']} is already outwarded on {carton['date_outwarded']}. No further updates possible.")
                self.current_carton_for_update = None
                self.update_carton_details_label.config(text="")
                return

            self.current_carton_for_update = carton
            details_text = f"Product: {carton['product_name']}\nCompany: {carton['company']}\nLocation: {carton['location']}\n" \
                           f"Current Quantity: {carton['quantity_per_carton']}\nDamaged: {carton['damaged_units']}\n" \
                           f"Inwarded: {carton['date_inwarded']}\nExpires: {carton['expiry_date'] or 'N/A'}"
            self.update_carton_details_label.config(text=details_text)
            self.update_new_qty_entry.delete(0, tk.END)
            self.update_new_qty_entry.insert(0, str(carton['quantity_per_carton']))
            self.update_new_damaged_entry.delete(0, tk.END)
            self.update_new_damaged_entry.insert(0, str(carton['damaged_units']))
            self.show_message('success', f"Carton {carton['carton_id']} found. Ready to update.")
        else:
            self.show_message('error', f"Carton ID '{query_carton_id}' not found.")
            self.current_carton_for_update = None
            self.update_carton_details_label.config(text="")

    def toggle_update_fields(self):
        action = self.update_action_var.get()
        if action == 'update':
            self.update_fields_frame.pack(fill='x', padx=5, pady=5)
        else:
            self.update_fields_frame.pack_forget()

    def perform_update_carton(self):
        if not self.current_carton_for_update:
            self.show_message('error', 'Please find a carton to update first.')
            return

        target_carton_id = self.current_carton_for_update['carton_id']

        if self.update_action_var.get() == 'update':
            try:
                new_qty = int(self.update_new_qty_entry.get())
                new_damaged = int(self.update_new_damaged_entry.get())
                if new_qty < 0 or new_damaged < 0 or new_damaged > new_qty:
                    raise ValueError
            except ValueError:
                self.show_message('error', 'Invalid quantity or damaged units. Please enter non-negative numbers, with damaged <= quantity.')
                return

            # Find and update the carton in the actual list
            for i, carton in enumerate(self.stock_data):
                if carton['carton_id'] == target_carton_id:
                    self.stock_data[i]['quantity_per_carton'] = new_qty
                    self.stock_data[i]['damaged_units'] = new_damaged
                    self.stock_data[i]['last_updated'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if new_qty == 0:
                        self.stock_data[i]['date_outwarded'] = format_date(datetime.date.today())
                        self.show_message('info', f"Carton {target_carton_id} is now empty and marked as outwarded.")
                    break

            save_stock_data(self.stock_data, self.selected_json_file)
            self.show_message('success', f"Carton {target_carton_id} updated successfully. New Quantity: {new_qty}, New Damaged: {new_damaged}.")

        elif self.update_action_var.get() == 'delete':
            if messagebox.askyesno("Confirm Delete", f"WARNING: This will PERMANENTLY DELETE Carton {target_carton_id} from records. This action cannot be undone. Are you absolutely sure?"):
                # Remove the carton from the list
                self.stock_data[:] = [c for c in self.stock_data if c['carton_id'] != target_carton_id]
                save_stock_data(self.stock_data, self.selected_json_file)
                self.show_message('success', f"Carton {target_carton_id} has been permanently DELETED.")
            else:
                self.show_message('info', 'Deletion cancelled.')
                return

        self.clear_update_carton_form()
        self.update_dashboard() # Refresh dashboard after update/delete

    def clear_update_carton_form(self):
        self.update_carton_id_entry.delete(0, tk.END)
        self.update_carton_details_label.config(text="")
        self.update_new_qty_entry.delete(0, tk.END)
        self.update_new_damaged_entry.delete(0, tk.END)
        self.update_action_var.set("update")
        self.toggle_update_fields()
        self.current_carton_for_update = None

    def prompt_for_company(self):
        # Dialog to select or create a company and its JSON file
        companies = list(self.company_configs.keys())
        if companies:
            choice = simpledialog.askstring("Stock Mitra - Company Selection", f"Enter your company name to manage, or type NEW to add a new company.\n\nAvailable: {', '.join(companies)}")
            if not choice:
                return
            if choice.strip().upper() == 'NEW':
                self.add_new_company()
            elif choice.strip() in self.company_configs:
                self.selected_company = choice.strip()
                self.selected_json_file = self.company_configs[self.selected_company]
            else:
                messagebox.showerror("Company Not Found", "Company not found. Please restart and try again.")
        else:
            self.add_new_company()

    def add_new_company(self):
        name = simpledialog.askstring("Add New Company", "Enter the new company name:")
        if not name:
            return
        file_path = filedialog.asksaveasfilename(
            title="Select or Create JSON File for Company Stock",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            initialdir=os.path.dirname(__file__)
        )
        if not file_path:
            return
        # Create file if doesn't exist
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump([], f)
        self.company_configs[name] = file_path
        save_company_configs(self.company_configs)
        self.selected_company = name
        self.selected_json_file = file_path

    def load_selected_company_data(self):
        self.stock_data = load_stock_data(self.selected_json_file)

    def create_menu_bar(self):
        company_menu = tk.Menu(self.menu_bar, tearoff=0)
        company_menu.add_command(label="Switch Company", command=self.switch_company)
        company_menu.add_command(label="Add New Company", command=self.add_new_company_and_reload)
        self.menu_bar.add_cascade(label="Company", menu=company_menu)

    def switch_company(self):
        companies = list(self.company_configs.keys())
        if not companies:
            messagebox.showinfo("No Companies", "No companies found. Please add a new company.")
            self.add_new_company_and_reload()
            return
        choice = simpledialog.askstring("Switch Company", f"Enter your company name to switch to:\n\nAvailable: {', '.join(companies)}")
        if not choice:
            return
        if choice.strip() in self.company_configs:
            self.selected_company = choice.strip()
            self.selected_json_file = self.company_configs[self.selected_company]
            self.load_selected_company_data()
            self.refresh_all_ui()
            messagebox.showinfo("Switched", f"Now managing stock for: {self.selected_company}")
        else:
            messagebox.showerror("Company Not Found", "Company not found.")

    def add_new_company_and_reload(self):
        self.add_new_company()
        if self.selected_company and self.selected_json_file:
            self.load_selected_company_data()
            self.refresh_all_ui()
            messagebox.showinfo("Added", f"Now managing stock for: {self.selected_company}")

    def refresh_all_ui(self):
        # Update dashboard and all relevant UI for the new company
        self.update_find_stock_suggestions()
        self.update_dashboard()
        # Update dashboard header button
        for widget in self.dashboard_frame.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.config(text=f"View {self.selected_company} Stock Details", command=lambda: self.show_company_stock(self.selected_company))
        # If company stock view is open, refresh it
        if self.notebook.index(self.notebook.select()) == self.notebook.tabs().index(str(self.company_stock_view_frame)):
            self.update_company_stock_view(self.selected_company)


# --- Main Application Entry Point ---
if __name__ == "__main__":
    app = StockApp()
    app.mainloop()