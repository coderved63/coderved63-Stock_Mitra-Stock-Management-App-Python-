import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import datetime
import os
import matplotlib
matplotlib.use('Agg')  # For headless environments, but will be overridden by TkAgg in UI
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import difflib

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

# --- Logging Helpers ---
def get_log_file_path(company_json_file, log_type):
    # log_type: 'sales' or 'purchase'
    base_dir = os.path.dirname(company_json_file)
    company_name = os.path.splitext(os.path.basename(company_json_file))[0]
    return os.path.join(base_dir, f"{company_name}_{log_type}_log.json")

def load_log(log_file):
    if not os.path.exists(log_file):
        with open(log_file, 'w') as f:
            json.dump([], f)
        return []
    try:
        with open(log_file, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def append_log_entry(log_file, entry):
    log = load_log(log_file)
    log.append(entry)
    with open(log_file, 'w') as f:
        json.dump(log, f, indent=4)

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

        # --- Sales Summary Tab ---
        self.sales_summary_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.sales_summary_frame, text="Sales Summary")
        self.create_sales_summary_widgets(self.sales_summary_frame)

        # --- Transaction Log Tab ---
        self.transaction_log_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.transaction_log_frame, text="Transaction Log")
        self.create_transaction_log_widgets(self.transaction_log_frame)

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
        total_stock_value = 0
        low_stock_products = []
        expiry_alerts = []
        LOW_STOCK_THRESHOLD = 10  # You can adjust this threshold
        EXPIRY_SOON_DAYS = 60

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
                    total_stock_value += c['quantity_per_carton'] * c.get('mrp', 0)
                    # Low stock check
                    if c['quantity_per_carton'] <= LOW_STOCK_THRESHOLD:
                        low_stock_products.append(f"{c['product_name']} ({c['product_id']}) - {c['quantity_per_carton']} units")
                    # Expiry soon check
                    if c['expiry_date']:
                        expiry_date_obj = parse_date(c['expiry_date'])
                        if expiry_date_obj and 0 < (expiry_date_obj - current_date).days <= EXPIRY_SOON_DAYS:
                            expiry_alerts.append(f"{c['product_name']} ({c['product_id']}) - Expires on {c['expiry_date']}")

        self.total_live_label.config(text=f"{total_live}")
        self.total_damaged_expired_label.config(text=f"{total_damaged_expired}")
        self.total_cartons_label.config(text=f"{len(all_stock)}")

        # Update stock value label
        if hasattr(self, 'total_stock_value_label'):
            self.total_stock_value_label.config(text=f"₹{total_stock_value:,.2f}")
        # Update low stock label
        if hasattr(self, 'low_stock_label'):
            if low_stock_products:
                self.low_stock_label.config(text="Low Stock: " + ", ".join(low_stock_products), foreground="#dc2626")
            else:
                self.low_stock_label.config(text="Low Stock: None", foreground="#059669")
        # Update expiry alerts label
        if hasattr(self, 'expiry_alerts_label'):
            if expiry_alerts:
                self.expiry_alerts_label.config(text="Expiring Soon: " + ", ".join(expiry_alerts), foreground="#dc2626")
            else:
                self.expiry_alerts_label.config(text="Expiring Soon: None", foreground="#059669")

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

        # --- New: Total Stock Value ---
        value_frame = ttk.Frame(parent_frame, style='TFrame')
        value_frame.pack(pady=10)
        ttk.Label(value_frame, text="Current Stock Value (₹)", font=self.subheading_font, background=FRAME_BG, foreground=PRIMARY_COLOR).pack(side='left', padx=(0, 10))
        self.total_stock_value_label = ttk.Label(value_frame, text="₹0.00", font=('Segoe UI', 22, 'bold'), foreground=PRIMARY_COLOR, background=FRAME_BG)
        self.total_stock_value_label.pack(side='left')

        # --- New: Low Stock Alerts ---
        self.low_stock_label = ttk.Label(parent_frame, text="Low Stock: None", font=('Segoe UI', 14), background=FRAME_BG, foreground="#059669")
        self.low_stock_label.pack(pady=5)

        # --- New: Expiry Alerts ---
        self.expiry_alerts_label = ttk.Label(parent_frame, text="Expiring Soon: None", font=('Segoe UI', 14), background=FRAME_BG, foreground="#059669")
        self.expiry_alerts_label.pack(pady=5)

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
                    'mrp_per_piece_sum': 0,
                    'purchase_per_piece_sum': 0,
                    'sales_per_piece_sum': 0,
                    'mrp_per_piece_count': 0,
                    'purchase_per_piece_count': 0,
                    'sales_per_piece_count': 0,
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

            # Calculate per piece prices
            qty = carton.get('quantity_per_carton', 0)
            if carton.get('mrp') is not None and qty:
                product['mrp_per_piece_sum'] += carton['mrp'] / qty
                product['mrp_per_piece_count'] += 1
            if carton.get('purchase_price') is not None and qty:
                product['purchase_per_piece_sum'] += carton['purchase_price'] / qty
                product['purchase_per_piece_count'] += 1
            if carton.get('sales_price') is not None and qty:
                product['sales_per_piece_sum'] += carton['sales_price'] / qty
                product['sales_per_piece_count'] += 1

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
                   "Last Outwarded", "MRP per Piece", "Purchase Price per Piece", "Sales Price per Piece", "Locations", "Status")
        self.tree = ttk.Treeview(self.company_stock_view_frame, columns=columns, show='headings', height=12, style='Small.Treeview')
        self.tree.pack(expand=True, fill='both', pady=10)
        col_widths = [90, 120, 80, 80, 100, 100, 100, 100, 100, 100, 100, 120, 100]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col, anchor=tk.CENTER)
            self.tree.column(col, width=width, anchor=tk.CENTER)
        # Populate data
        for product in sorted_aggregated_products:
            status_text = 'In Stock'
            if product['totalLivePieces'] == 0 and product['totalDamagedUnits'] == 0:
                status_text = 'Out of Stock'
            elif product['hasExpiredStock'] and product['totalLivePieces'] == 0:
                status_text = 'All Expired'
            elif product['hasExpiredStock'] or product['hasDamagedStock']:
                status_text = 'Some Damaged/Expired'
            avg_mrp_per_piece = product['mrp_per_piece_sum'] / product['mrp_per_piece_count'] if product['mrp_per_piece_count'] else 0
            avg_purchase_per_piece = product['purchase_per_piece_sum'] / product['purchase_per_piece_count'] if product['purchase_per_piece_count'] else 0
            avg_sales_per_piece = product['sales_per_piece_sum'] / product['sales_per_piece_count'] if product['sales_per_piece_count'] else 0
            self.tree.insert("", tk.END, values=(
                product['productId'],
                product['productName'],
                product['totalLiveCartons'],
                product['totalLivePieces'],
                product['totalDamagedUnits'],
                format_date(product['earliestInwarded']) if product['earliestInwarded'].year != 9999 else 'N/A',
                format_date(product['earliestExpiry']) if product['earliestExpiry'].year != 9999 else 'N/A',
                format_date(product['latestOutwarded']) if product['latestOutwarded'].year != 1 else 'N/A',
                f"₹{avg_mrp_per_piece:.2f}" if avg_mrp_per_piece else 'N/A',
                f"₹{avg_purchase_per_piece:.2f}" if avg_purchase_per_piece else 'N/A',
                f"₹{avg_sales_per_piece:.2f}" if avg_sales_per_piece else 'N/A',
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
        self.add_product_id_entry.bind('<KeyRelease>', lambda e, w=self.add_product_id_entry: self.show_add_stock_suggestions(w))
        ttk.Label(details_frame, text="Product Name:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.add_product_name_entry = ttk.Entry(details_frame)
        self.add_product_name_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        self.add_product_name_entry.bind('<KeyRelease>', lambda e, w=self.add_product_name_entry: self.show_add_stock_suggestions(w))
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
            # --- New: Sales Price ---
            ttk.Label(carton_label_frame, text="Sales Price:", font=self.label_font).grid(row=4, column=0, padx=5, pady=2, sticky='w')
            sales_price_entry = ttk.Entry(carton_label_frame, font=self.entry_font)
            sales_price_entry.grid(row=5, column=0, padx=5, pady=2, sticky='ew')
            # --- New: Purchase Price ---
            ttk.Label(carton_label_frame, text="Purchase Price:", font=self.label_font).grid(row=6, column=0, padx=5, pady=2, sticky='w')
            purchase_price_entry = ttk.Entry(carton_label_frame, font=self.entry_font)
            purchase_price_entry.grid(row=7, column=0, padx=5, pady=2, sticky='ew')
            self.carton_entries.append({
                'qty_entry': qty_entry,
                'damaged_entry': damaged_entry,
                'sales_price_entry': sales_price_entry,
                'purchase_price_entry': purchase_price_entry
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
                sales_price = float(entry_set['sales_price_entry'].get())
                purchase_price = float(entry_set['purchase_price_entry'].get())
                if qty <= 0 or damaged < 0 or damaged > qty or sales_price < 0 or purchase_price < 0:
                    raise ValueError
                cartons_data_for_add.append({'quantity': qty, 'damaged': damaged, 'sales_price': sales_price, 'purchase_price': purchase_price})
            except ValueError:
                self.show_message('error', 'Please enter valid positive numbers for quantity, sales price, and purchase price, and non-negative for damaged units (damaged <= quantity).')
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
                "sales_price": carton_detail['sales_price'],
                "purchase_price": carton_detail['purchase_price']
            }
            self.stock_data.append(new_carton)
            added_carton_ids.append(carton_id)
            # Log purchase
            purchase_log_file = get_log_file_path(self.selected_json_file, 'purchase')
            append_log_entry(purchase_log_file, {
                'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'product_id': product_id,
                'product_name': product_name,
                'carton_id': carton_id,
                'quantity': carton_detail['quantity'],
                'sales_price': carton_detail['sales_price'],
                'purchase_price': carton_detail['purchase_price'],
                'sales_value': carton_detail['quantity'] * carton_detail['sales_price'],
                'purchase_value': carton_detail['quantity'] * carton_detail['purchase_price'],
                'type': 'purchase',
            })
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
        self.sell_product_query_entry.bind('<KeyRelease>', self.show_sell_stock_suggestions)
        self.sell_stock_suggestion_window = None
        self.sell_stock_suggestion_listbox = None

        # Use a fixed-height, read-only Text widget for summary
        self.sell_product_summary_text = tk.Text(parent_frame, height=5, width=70, wrap=tk.WORD, font=('Arial', 10), bg=ACCENT_COLOR, fg=LABEL_FG, relief='flat')
        self.sell_product_summary_text.pack(pady=5, padx=5, fill='x')
        self.sell_product_summary_text.config(state=tk.DISABLED)

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
            self.sell_product_summary_text.config(state=tk.NORMAL)
            self.sell_product_summary_text.delete(1.0, tk.END)
            self.sell_product_summary_text.insert(tk.END, summary_text)
            self.sell_product_summary_text.config(state=tk.DISABLED)
            self.show_message('info', f"Product identified: {product_name} ({product_id}). Ready to sell.")
        else:
            self.identified_product_id_for_sale = None
            self.sell_product_summary_text.config(state=tk.NORMAL)
            self.sell_product_summary_text.delete(1.0, tk.END)
            self.sell_product_summary_text.insert(tk.END, message)
            self.sell_product_summary_text.config(state=tk.DISABLED)
            self.show_message('error', message)

    def clear_sell_stock_form(self):
        self.sell_product_query_entry.delete(0, tk.END)
        self.sell_num_full_cartons_entry.delete(0, tk.END)
        self.sell_num_full_cartons_entry.insert(0, "0")
        self.sell_num_loose_pieces_entry.delete(0, tk.END)
        self.sell_num_loose_pieces_entry.insert(0, "0")
        self.sell_product_summary_text.config(state=tk.NORMAL)
        self.sell_product_summary_text.delete(1.0, tk.END)
        self.sell_product_summary_text.config(state=tk.DISABLED)
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

    def create_sales_summary_widgets(self, parent_frame):
        ttk.Label(parent_frame, text="Monthly Sales Summary", font=self.heading_font, background=FRAME_BG, foreground=PRIMARY_COLOR).pack(pady=(0, 18))
        self.sales_summary_tree = ttk.Treeview(parent_frame, columns=("Month", "Product ID", "Product Name", "Units Sold", "Sales Price", "Purchase Price", "Total Sales (₹)", "Profit/Loss (₹)"), show='headings', height=10)
        # Use a smaller font for table
        style = ttk.Style()
        style.configure('Small.Treeview', font=('Segoe UI', 11))
        style.configure('Small.Treeview.Heading', font=('Segoe UI', 10, 'bold'))
        self.sales_summary_tree.configure(style='Small.Treeview')
        for col, width in zip(("Month", "Product ID", "Product Name", "Units Sold", "Sales Price", "Purchase Price", "Total Sales (₹)", "Profit/Loss (₹)"), [80, 90, 140, 80, 90, 90, 110, 110]):
            self.sales_summary_tree.heading(col, text=col)
            self.sales_summary_tree.column(col, width=width, anchor='center')
        self.sales_summary_tree.pack(expand=True, fill='both', pady=10)
        btn_frame = ttk.Frame(parent_frame)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Refresh", command=self.update_sales_summary).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Export to PDF", command=self.export_sales_summary_pdf).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Clear Sales Summary", command=self.clear_sales_summary).pack(side='left', padx=5)
        # Chart area
        self.sales_chart_frame = ttk.Frame(parent_frame, style='TFrame')
        self.sales_chart_frame.pack(fill='both', expand=True, pady=10)
        self.sales_chart_canvas = None
        # Pie chart area
        self.sales_pie_frame = ttk.Frame(parent_frame, style='TFrame')
        self.sales_pie_frame.pack(fill='both', expand=True, pady=10)
        self.sales_pie_canvas = None
        self.update_sales_summary()

    def clear_sales_summary(self):
        if not messagebox.askyesno("Confirm Clear", "Are you sure you want to CLEAR the entire sales summary? This cannot be undone."):
            return
        sales_log_file = get_log_file_path(self.selected_json_file, 'sales')
        with open(sales_log_file, 'w') as f:
            json.dump([], f)
        self.update_sales_summary()
        self.show_message('success', 'Sales summary cleared.')

    def export_sales_summary_pdf(self):
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.lib.utils import ImageReader
            from reportlab.lib import colors
        except ImportError:
            self.show_message('error', 'reportlab is not installed. Please install it with "pip install reportlab".')
            return
        file_path = filedialog.asksaveasfilename(defaultextension='.pdf', filetypes=[('PDF files', '*.pdf')], title='Export Sales Summary PDF')
        if not file_path:
            return
        # Gather table data
        table_data = [("Month", "Product ID", "Product Name", "Units Sold", "Sales Price", "Purchase Price", "Total Sales (₹)", "Profit/Loss (₹)")]
        for row in self.sales_summary_tree.get_children():
            table_data.append(self.sales_summary_tree.item(row)['values'])
        # Save charts as images
        chart_img_path = "_temp_sales_chart.png"
        pie_img_path = "_temp_sales_pie.png"
        if self.sales_chart_canvas:
            self.sales_chart_canvas.figure.savefig(chart_img_path, bbox_inches='tight', dpi=150)
        if self.sales_pie_canvas:
            self.sales_pie_canvas.figure.savefig(pie_img_path, bbox_inches='tight', dpi=150)
        # Create PDF
        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter
        y = height - 40
        c.setFont("Helvetica-Bold", 18)
        c.drawString(40, y, f"Stock Mitra - Sales Summary Report")
        c.setFont("Helvetica", 12)
        y -= 25
        c.drawString(40, y, f"Company: {self.selected_company}")
        c.drawString(350, y, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
        y -= 30
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "Monthly Sales Summary Table:")
        y -= 20
        # Draw table
        col_widths = [70, 70, 120, 60, 80, 80, 100, 100]
        for i, row in enumerate(table_data):
            for j, val in enumerate(row):
                c.setFont("Helvetica-Bold" if i == 0 else "Helvetica", 10)
                c.setFillColor(colors.black if i == 0 else colors.darkblue)
                c.drawString(40 + sum(col_widths[:j]), y, str(val))
            y -= 18
            if y < 120:
                c.showPage()
                y = height - 40
        y -= 10
        # Add charts
        if os.path.exists(chart_img_path):
            c.setFont("Helvetica-Bold", 14)
            c.drawString(40, y, "Monthly Sales & Profit/Loss Chart:")
            y -= 10
            c.drawImage(chart_img_path, 40, y-180, width=400, height=180, preserveAspectRatio=True, mask='auto')
            y -= 200
        if os.path.exists(pie_img_path):
            c.setFont("Helvetica-Bold", 14)
            c.drawString(40, y, "Sales Share by Product (Pie Chart):")
            y -= 10
            c.drawImage(pie_img_path, 40, y-180, width=300, height=180, preserveAspectRatio=True, mask='auto')
            y -= 200
        c.save()
        # Clean up temp images
        if os.path.exists(chart_img_path):
            os.remove(chart_img_path)
        if os.path.exists(pie_img_path):
            os.remove(pie_img_path)
        self.show_message('success', f'Sales summary exported to {file_path}')

    def update_sales_summary(self):
        # Clear tree
        for row in self.sales_summary_tree.get_children():
            self.sales_summary_tree.delete(row)
        # Load sales log
        sales_log_file = get_log_file_path(self.selected_json_file, 'sales')
        sales_log = load_log(sales_log_file)
        # Aggregate by month and product, including profit/loss
        summary = {}
        for entry in sales_log:
            date = entry.get('date', '')
            month = date[:7]  # YYYY-MM
            key = (month, entry['product_id'], entry['product_name'])
            if key not in summary:
                summary[key] = {'units': 0, 'sales_value': 0, 'purchase_value': 0, 'sales_price': 0, 'purchase_price': 0, 'count': 0}
            summary[key]['units'] += entry.get('quantity', 0)
            summary[key]['sales_value'] += entry.get('sales_value', 0)
            summary[key]['purchase_value'] += entry.get('purchase_value', 0)
            summary[key]['sales_price'] += entry.get('sales_price', 0)
            summary[key]['purchase_price'] += entry.get('purchase_price', 0)
            summary[key]['count'] += 1
        # Insert into tree
        for (month, pid, pname), vals in sorted(summary.items()):
            avg_sales_price = vals['sales_price'] / vals['count'] if vals['count'] else 0
            avg_purchase_price = vals['purchase_price'] / vals['count'] if vals['count'] else 0
            profit_loss = vals['sales_value'] - vals['purchase_value']
            self.sales_summary_tree.insert('', 'end', values=(month, pid, pname, vals['units'], f"₹{avg_sales_price:.2f}", f"₹{avg_purchase_price:.2f}", f"₹{vals['sales_value']:.2f}", f"₹{profit_loss:.2f}"))
        # --- Chart: Monthly Sales and Profit/Loss ---
        self.plot_sales_summary_chart(summary)
        self.plot_sales_pie_chart(summary)

    def plot_sales_summary_chart(self, summary):
        # Remove previous chart if exists
        if self.sales_chart_canvas:
            self.sales_chart_canvas.get_tk_widget().destroy()
            self.sales_chart_canvas = None
        # Aggregate by month (all products)
        month_data = {}
        for (month, pid, pname), vals in summary.items():
            if month not in month_data:
                month_data[month] = {'units': 0, 'sales_value': 0, 'profit_loss': 0}
            month_data[month]['units'] += vals['units']
            month_data[month]['sales_value'] += vals['sales_value']
            month_data[month]['profit_loss'] += vals['sales_value'] - vals['purchase_value']
        months = sorted(month_data.keys())
        units = [month_data[m]['units'] for m in months]
        values = [month_data[m]['sales_value'] for m in months]
        profits = [month_data[m]['profit_loss'] for m in months]
        # Create figure
        fig = Figure(figsize=(7, 3.5), dpi=100)
        ax1 = fig.add_subplot(111)
        ax1.bar(months, values, color='#3b82f6', alpha=0.7, label='Sales Value (₹)')
        ax1.plot(months, profits, color='#059669', marker='o', linewidth=2, label='Profit/Loss (₹)')
        ax1.set_ylabel('₹')
        ax1.set_xlabel('Month')
        ax1.set_title('Monthly Sales Value & Profit/Loss')
        ax1.legend()
        ax1.grid(True, linestyle='--', alpha=0.3)
        fig.tight_layout()
        # Embed in Tkinter
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        self.sales_chart_canvas = FigureCanvasTkAgg(fig, master=self.sales_chart_frame)
        self.sales_chart_canvas.draw()
        self.sales_chart_canvas.get_tk_widget().pack(fill='both', expand=True)

    def plot_sales_pie_chart(self, summary):
        # Remove previous pie chart if exists
        if self.sales_pie_canvas:
            self.sales_pie_canvas.get_tk_widget().destroy()
            self.sales_pie_canvas = None
        # Aggregate total sales value by product (all months)
        product_totals = {}
        for (month, pid, pname), vals in summary.items():
            key = f"{pname} ({pid})"
            if key not in product_totals:
                product_totals[key] = 0
            product_totals[key] += vals['sales_value']
        labels = list(product_totals.keys())
        sizes = list(product_totals.values())
        if not sizes or sum(sizes) == 0:
            return  # Nothing to plot
        # Modern color palette
        colors = ['#3b82f6', '#059669', '#f59e42', '#ef4444', '#a21caf', '#eab308', '#0ea5e9', '#10b981', '#f43f5e', '#6366f1']
        # Create figure
        fig = Figure(figsize=(4, 3.5), dpi=100)
        ax = fig.add_subplot(111)
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors[:len(labels)], textprops={'color': 'white', 'fontsize': 10})
        ax.set_title('Share of Total Sales Value by Product')
        fig.tight_layout()
        # Embed in Tkinter
        self.sales_pie_canvas = FigureCanvasTkAgg(fig, master=self.sales_pie_frame)
        self.sales_pie_canvas.draw()
        self.sales_pie_canvas.get_tk_widget().pack(fill='both', expand=True)

    def create_transaction_log_widgets(self, parent_frame):
        ttk.Label(parent_frame, text="Transaction Log (Sales & Purchases)", font=self.heading_font, background=FRAME_BG, foreground=PRIMARY_COLOR).pack(pady=(0, 18))
        # Button frame above the table
        btn_frame = ttk.Frame(parent_frame)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Refresh", command=self.update_transaction_log, style='TButton').pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Export to CSV", command=self.export_transaction_log_csv, style='TButton').pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Clear Transaction Logs", command=self.clear_transaction_logs, style='TButton').pack(side='left', padx=5)
        self.transaction_log_tree = ttk.Treeview(parent_frame, columns=("Date", "Type", "Product ID", "Product Name", "Carton ID", "Quantity", "Sales Price", "Purchase Price", "Sales Value (₹)", "Purchase Value (₹)"), show='headings', height=12, style='Small.Treeview')
        for col, width in zip(("Date", "Type", "Product ID", "Product Name", "Carton ID", "Quantity", "Sales Price", "Purchase Price", "Sales Value (₹)", "Purchase Value (₹)"), [110, 60, 90, 120, 90, 70, 80, 80, 100, 100]):
            self.transaction_log_tree.heading(col, text=col)
            self.transaction_log_tree.column(col, width=width, anchor='center')
        self.transaction_log_tree.pack(expand=True, fill='both', pady=10)
        self.update_transaction_log()

    def clear_transaction_logs(self):
        if not messagebox.askyesno("Confirm Clear", "Are you sure you want to CLEAR all transaction logs (sales and purchases)? This cannot be undone."):
            return
        sales_log_file = get_log_file_path(self.selected_json_file, 'sales')
        purchase_log_file = get_log_file_path(self.selected_json_file, 'purchase')
        with open(sales_log_file, 'w') as f:
            json.dump([], f)
        with open(purchase_log_file, 'w') as f:
            json.dump([], f)
        self.update_transaction_log()
        self.show_message('success', 'Transaction logs cleared.')

    def update_transaction_log(self):
        for row in self.transaction_log_tree.get_children():
            self.transaction_log_tree.delete(row)
        sales_log_file = get_log_file_path(self.selected_json_file, 'sales')
        purchase_log_file = get_log_file_path(self.selected_json_file, 'purchase')
        sales_log = load_log(sales_log_file)
        purchase_log = load_log(purchase_log_file)
        all_entries = sales_log + purchase_log
        all_entries.sort(key=lambda x: x.get('date', ''))
        for entry in all_entries:
            self.transaction_log_tree.insert('', 'end', values=(
                entry.get('date', ''),
                entry.get('type', ''),
                entry.get('product_id', ''),
                entry.get('product_name', ''),
                entry.get('carton_id', ''),
                entry.get('quantity', 0),
                f"₹{entry.get('sales_price', 0):.2f}",
                f"₹{entry.get('purchase_price', 0):.2f}",
                f"₹{entry.get('sales_value', 0):.2f}",
                f"₹{entry.get('purchase_value', 0):.2f}"
            ))

    def export_transaction_log_csv(self):
        import csv
        from tkinter import filedialog
        sales_log_file = get_log_file_path(self.selected_json_file, 'sales')
        purchase_log_file = get_log_file_path(self.selected_json_file, 'purchase')
        sales_log = load_log(sales_log_file)
        purchase_log = load_log(purchase_log_file)
        all_entries = sales_log + purchase_log
        all_entries.sort(key=lambda x: x.get('date', ''))
        file_path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')], title='Export Transaction Log')
        if not file_path:
            return
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Date", "Type", "Product ID", "Product Name", "Carton ID", "Quantity", "Sales Price", "Purchase Price", "Sales Value (₹)", "Purchase Value (₹)"])
            for entry in all_entries:
                writer.writerow([
                    entry.get('date', ''),
                    entry.get('type', ''),
                    entry.get('product_id', ''),
                    entry.get('product_name', ''),
                    entry.get('carton_id', ''),
                    entry.get('quantity', 0),
                    entry.get('sales_price', 0),
                    entry.get('purchase_price', 0),
                    entry.get('sales_value', 0),
                    entry.get('purchase_value', 0)
                ])

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
        sales_log_file = get_log_file_path(self.selected_json_file, 'sales')

        cartons_processed_for_full = 0
        idx = 0
        while cartons_processed_for_full < num_full_cartons and idx < len(active_sellable_cartons_references):
            carton = active_sellable_cartons_references[idx]
            if carton['quantity_per_carton'] > 0:
                original_qty_in_carton = carton['quantity_per_carton']
                # Log sale
                append_log_entry(sales_log_file, {
                    'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'product_id': carton['product_id'],
                    'product_name': carton['product_name'],
                    'carton_id': carton['carton_id'],
                    'quantity': original_qty_in_carton,
                    'sales_price': carton.get('sales_price', 0),
                    'purchase_price': carton.get('purchase_price', 0),
                    'sales_value': original_qty_in_carton * carton.get('sales_price', 0),
                    'purchase_value': original_qty_in_carton * carton.get('purchase_price', 0),
                    'type': 'sale',
                })
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
                # Log sale
                append_log_entry(sales_log_file, {
                    'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'product_id': carton['product_id'],
                    'product_name': carton['product_name'],
                    'carton_id': carton['carton_id'],
                    'quantity': deduct_from_this_carton,
                    'sales_price': carton.get('sales_price', 0),
                    'purchase_price': carton.get('purchase_price', 0),
                    'sales_value': deduct_from_this_carton * carton.get('sales_price', 0),
                    'purchase_value': deduct_from_this_carton * carton.get('purchase_price', 0),
                    'type': 'sale',
                })
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

    def show_sell_stock_suggestions(self, event):
        # Destroy previous suggestion window if exists
        if self.sell_stock_suggestion_window:
            self.sell_stock_suggestion_window.destroy()
            self.sell_stock_suggestion_window = None
        entry_widget = self.sell_product_query_entry
        typed = entry_widget.get().strip()
        if not typed:
            return
        # Gather all product IDs and names
        all_stock = self.stock_data
        product_ids = [item['product_id'] for item in all_stock]
        product_names = [item['product_name'] for item in all_stock]
        matches = set()
        import difflib
        matches.update(difflib.get_close_matches(typed.upper(), product_ids, n=5, cutoff=0.6))
        matches.update([product_ids[idx] for idx, name in enumerate(product_names) if name.lower() in difflib.get_close_matches(typed.lower(), [n.lower() for n in product_names], n=5, cutoff=0.6)])
        if not matches:
            return
        # Create a Toplevel window for suggestions
        x = entry_widget.winfo_rootx()
        y = entry_widget.winfo_rooty() + entry_widget.winfo_height()
        self.sell_stock_suggestion_window = tk.Toplevel(self)
        self.sell_stock_suggestion_window.wm_overrideredirect(True)
        self.sell_stock_suggestion_window.wm_geometry(f"{entry_widget.winfo_width()}x{min(6, len(matches))*22}+{x}+{y}")
        self.sell_stock_suggestion_window.lift()
        self.sell_stock_suggestion_window.attributes('-topmost', True)
        # Listbox inside the Toplevel
        self.sell_stock_suggestion_listbox = tk.Listbox(self.sell_stock_suggestion_window, height=min(6, len(matches)), font=('Arial', 10))
        self.sell_stock_suggestion_listbox.pack(fill='both', expand=True)
        for match in matches:
            self.sell_stock_suggestion_listbox.insert(tk.END, match)
        self.sell_stock_suggestion_listbox.focus_set()
        # Mouse click selection
        self.sell_stock_suggestion_listbox.bind('<<ListboxSelect>>', lambda e: self.select_sell_stock_suggestion())
        self.sell_stock_suggestion_listbox.bind('<ButtonRelease-1>', lambda e: self.select_sell_stock_suggestion())
        # Keyboard navigation
        self.sell_stock_suggestion_listbox.bind('<Return>', lambda e: self.select_sell_stock_suggestion())
        self.sell_stock_suggestion_listbox.bind('<Escape>', lambda e: self.close_sell_stock_suggestions())
        self.sell_stock_suggestion_listbox.bind('<Up>', self.move_sell_stock_suggestion_up)
        self.sell_stock_suggestion_listbox.bind('<Down>', self.move_sell_stock_suggestion_down)
        # Focus out closes suggestions
        self.sell_stock_suggestion_window.bind('<FocusOut>', lambda e: self.close_sell_stock_suggestions())

    def select_sell_stock_suggestion(self):
        if self.sell_stock_suggestion_listbox:
            selection = self.sell_stock_suggestion_listbox.curselection()
            if selection:
                value = self.sell_stock_suggestion_listbox.get(selection[0])
                self.sell_product_query_entry.delete(0, tk.END)
                self.sell_product_query_entry.insert(0, value)
            self.close_sell_stock_suggestions()

    def close_sell_stock_suggestions(self):
        if self.sell_stock_suggestion_window:
            self.sell_stock_suggestion_window.destroy()
            self.sell_stock_suggestion_window = None
        self.sell_stock_suggestion_listbox = None

    def move_sell_stock_suggestion_up(self, event):
        if self.sell_stock_suggestion_listbox:
            cur = self.sell_stock_suggestion_listbox.curselection()
            if cur:
                idx = cur[0]
                if idx > 0:
                    self.sell_stock_suggestion_listbox.selection_clear(0, tk.END)
                    self.sell_stock_suggestion_listbox.selection_set(idx-1)
                    self.sell_stock_suggestion_listbox.activate(idx-1)
            else:
                self.sell_stock_suggestion_listbox.selection_set(0)
                self.sell_stock_suggestion_listbox.activate(0)
        return "break"

    def move_sell_stock_suggestion_down(self, event):
        if self.sell_stock_suggestion_listbox:
            cur = self.sell_stock_suggestion_listbox.curselection()
            size = self.sell_stock_suggestion_listbox.size()
            if cur:
                idx = cur[0]
                if idx < size-1:
                    self.sell_stock_suggestion_listbox.selection_clear(0, tk.END)
                    self.sell_stock_suggestion_listbox.selection_set(idx+1)
                    self.sell_stock_suggestion_listbox.activate(idx+1)
            else:
                self.sell_stock_suggestion_listbox.selection_set(0)
                self.sell_stock_suggestion_listbox.activate(0)
        return "break"

    def show_add_stock_suggestions(self, entry_widget):
        # Destroy previous suggestion window if exists
        if self.add_stock_suggestion_window:
            self.add_stock_suggestion_window.destroy()
            self.add_stock_suggestion_window = None
        typed = entry_widget.get().strip()
        if not typed:
            return
        # Gather all product IDs and names
        all_stock = self.stock_data
        product_ids = [item['product_id'] for item in all_stock]
        product_names = [item['product_name'] for item in all_stock]
        matches = set()
        import difflib
        if entry_widget == self.add_product_id_entry:
            matches = set(difflib.get_close_matches(typed.upper(), product_ids, n=5, cutoff=0.6))
        elif entry_widget == self.add_product_name_entry:
            matches = set(difflib.get_close_matches(typed.lower(), [n.lower() for n in product_names], n=5, cutoff=0.6))
        if not matches:
            return
        # Create a Toplevel window for suggestions (always as child of root)
        x = entry_widget.winfo_rootx()
        y = entry_widget.winfo_rooty() + entry_widget.winfo_height()
        self.add_stock_suggestion_window = tk.Toplevel(self)
        self.add_stock_suggestion_window.wm_overrideredirect(True)
        self.add_stock_suggestion_window.wm_geometry(f"{entry_widget.winfo_width()}x{min(6, len(matches))*22}+{x}+{y}")
        self.add_stock_suggestion_window.lift()
        self.add_stock_suggestion_window.attributes('-topmost', True)
        self.add_stock_suggestion_window.configure(bg='#1e293b', borderwidth=2, relief='solid')
        print("[DEBUG] Add Stock suggestion window created at", x, y)
        # Listbox inside the Toplevel
        self.add_stock_suggestion_listbox = tk.Listbox(self.add_stock_suggestion_window, height=min(6, len(matches)), font=('Arial', 10), bg='#1e293b', fg='#f1f5f9', borderwidth=0, highlightthickness=0, selectbackground='#2563eb', selectforeground='#f1f5f9')
        self.add_stock_suggestion_listbox.pack(fill='both', expand=True)
        for match in matches:
            self.add_stock_suggestion_listbox.insert(tk.END, match)
        self.add_stock_suggestion_listbox.focus_set()
        # Mouse click selection
        self.add_stock_suggestion_listbox.bind('<<ListboxSelect>>', lambda e: self.select_add_stock_suggestion(entry_widget))
        self.add_stock_suggestion_listbox.bind('<ButtonRelease-1>', lambda e: self.select_add_stock_suggestion(entry_widget))
        # Keyboard navigation
        self.add_stock_suggestion_listbox.bind('<Return>', lambda e: self.select_add_stock_suggestion(entry_widget))
        self.add_stock_suggestion_listbox.bind('<Escape>', lambda e: self.close_add_stock_suggestions())
        self.add_stock_suggestion_listbox.bind('<Up>', self.move_add_stock_suggestion_up)
        self.add_stock_suggestion_listbox.bind('<Down>', self.move_add_stock_suggestion_down)
        # Focus out closes suggestions
        self.add_stock_suggestion_window.bind('<FocusOut>', lambda e: self.close_add_stock_suggestions())
        # Close on scroll (canvas)
        if hasattr(self, 'carton_canvas'):
            self.carton_canvas.bind('<MouseWheel>', lambda e: self.close_add_stock_suggestions())
            self.carton_canvas.bind('<Button-4>', lambda e: self.close_add_stock_suggestions())
            self.carton_canvas.bind('<Button-5>', lambda e: self.close_add_stock_suggestions())

    def select_add_stock_suggestion(self, entry_widget):
        if self.add_stock_suggestion_listbox:
            selection = self.add_stock_suggestion_listbox.curselection()
            if selection:
                value = self.add_stock_suggestion_listbox.get(selection[0])
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, value)
                # Auto-fill the other field if a known product
                all_stock = self.stock_data
                if entry_widget == self.add_product_id_entry:
                    # Fill product name
                    match = next((item for item in all_stock if item['product_id'] == value), None)
                    if match:
                        self.add_product_name_entry.delete(0, tk.END)
                        self.add_product_name_entry.insert(0, match['product_name'])
                elif entry_widget == self.add_product_name_entry:
                    # Fill product ID
                    match = next((item for item in all_stock if item['product_name'].lower() == value.lower()), None)
                    if match:
                        self.add_product_id_entry.delete(0, tk.END)
                        self.add_product_id_entry.insert(0, match['product_id'])
            self.close_add_stock_suggestions()

    def close_add_stock_suggestions(self):
        if self.add_stock_suggestion_window:
            self.add_stock_suggestion_window.destroy()
            self.add_stock_suggestion_window = None
        self.add_stock_suggestion_listbox = None

    def move_add_stock_suggestion_up(self, event):
        if self.add_stock_suggestion_listbox:
            cur = self.add_stock_suggestion_listbox.curselection()
            if cur:
                idx = cur[0]
                if idx > 0:
                    self.add_stock_suggestion_listbox.selection_clear(0, tk.END)
                    self.add_stock_suggestion_listbox.selection_set(idx-1)
                    self.add_stock_suggestion_listbox.activate(idx-1)
            else:
                self.add_stock_suggestion_listbox.selection_set(0)
                self.add_stock_suggestion_listbox.activate(0)
        return "break"

    def move_add_stock_suggestion_down(self, event):
        if self.add_stock_suggestion_listbox:
            cur = self.add_stock_suggestion_listbox.curselection()
            size = self.add_stock_suggestion_listbox.size()
            if cur:
                idx = cur[0]
                if idx < size-1:
                    self.add_stock_suggestion_listbox.selection_clear(0, tk.END)
                    self.add_stock_suggestion_listbox.selection_set(idx+1)
                    self.add_stock_suggestion_listbox.activate(idx+1)
            else:
                self.add_stock_suggestion_listbox.selection_set(0)
                self.add_stock_suggestion_listbox.activate(0)
        return "break"


# --- Main Application Entry Point ---
if __name__ == "__main__":
    app = StockApp()
    app.mainloop()