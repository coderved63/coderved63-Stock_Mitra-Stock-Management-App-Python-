"""
Stock management business logic services.
"""

import datetime
from utils.date_utils import parse_date
from config.settings import LOW_STOCK_THRESHOLD, EXPIRY_SOON_DAYS


class StockAnalyzer:
    """Handles stock analysis and dashboard calculations."""
    
    def __init__(self, stock_data):
        self.stock_data = stock_data
    
    def get_dashboard_stats(self):
        """Calculate dashboard statistics."""
        current_date = datetime.date.today()
        
        total_live = 0
        total_damaged_expired = 0
        total_stock_value = 0
        low_stock_products = []
        expiry_alerts = []
        
        for c in self.stock_data:
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
        
        return {
            'total_live': total_live,
            'total_damaged_expired': total_damaged_expired,
            'total_cartons': len(self.stock_data),
            'total_stock_value': total_stock_value,
            'low_stock_products': low_stock_products,
            'expiry_alerts': expiry_alerts
        }


class StockValidator:
    """Handles stock validation operations."""
    
    @staticmethod
    def validate_add_stock_data(form_data):
        """Validate stock addition form data."""
        errors = []
        
        if not form_data.get('carton_id'):
            errors.append("Carton ID is required")
        if not form_data.get('product_id'):
            errors.append("Product ID is required")
        if not form_data.get('product_name'):
            errors.append("Product name is required")
        
        try:
            quantity = int(form_data.get('quantity_per_carton', 0))
            if quantity <= 0:
                errors.append("Quantity must be a positive number")
        except ValueError:
            errors.append("Quantity must be a valid number")
        
        try:
            damaged = int(form_data.get('damaged_units', 0))
            if damaged < 0:
                errors.append("Damaged units cannot be negative")
        except ValueError:
            errors.append("Damaged units must be a valid number")
        
        try:
            mrp = float(form_data.get('mrp', 0))
            if mrp < 0:
                errors.append("MRP cannot be negative")
        except ValueError:
            errors.append("MRP must be a valid number")
        
        if not form_data.get('location'):
            errors.append("Location is required")
        
        return errors
    
    @staticmethod
    def validate_sell_stock_data(form_data):
        """Validate stock selling form data."""
        errors = []
        
        if not form_data.get('product_query'):
            errors.append("Product identification is required")
        
        try:
            quantity = int(form_data.get('quantity', 0))
            if quantity <= 0:
                errors.append("Sell quantity must be a positive number")
        except ValueError:
            errors.append("Sell quantity must be a valid number")
        
        return errors