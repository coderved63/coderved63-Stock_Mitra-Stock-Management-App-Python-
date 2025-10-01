"""
Stock and carton data models.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class StockCarton:
    """Represents a stock carton with all its properties."""
    carton_id: str
    product_id: str
    product_name: str
    quantity_per_carton: int
    damaged_units: int
    date_inwarded: str
    expiry_date: Optional[str]
    location: str
    mrp: float
    date_outwarded: Optional[str] = None
    
    def to_dict(self):
        """Convert the carton to a dictionary for JSON serialization."""
        return {
            'carton_id': self.carton_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'quantity_per_carton': self.quantity_per_carton,
            'damaged_units': self.damaged_units,
            'date_inwarded': self.date_inwarded,
            'expiry_date': self.expiry_date,
            'location': self.location,
            'mrp': self.mrp,
            'date_outwarded': self.date_outwarded
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a StockCarton from a dictionary."""
        return cls(
            carton_id=data['carton_id'],
            product_id=data['product_id'],
            product_name=data['product_name'],
            quantity_per_carton=data['quantity_per_carton'],
            damaged_units=data['damaged_units'],
            date_inwarded=data['date_inwarded'],
            expiry_date=data.get('expiry_date'),
            location=data['location'],
            mrp=data['mrp'],
            date_outwarded=data.get('date_outwarded')
        )