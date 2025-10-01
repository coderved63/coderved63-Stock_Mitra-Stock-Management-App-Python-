"""
Base UI components and styling utilities.
"""

import tkinter as tk
from tkinter import ttk
from config.colors import *
from config.settings import FONTS


class BaseUIComponent:
    """Base class for all UI components."""
    
    def __init__(self, parent, stock_app_ref):
        self.parent = parent
        self.stock_app = stock_app_ref  # Reference to main app for data access
    
    def create_frame(self, padding="20"):
        """Create a styled frame."""
        frame = ttk.Frame(self.parent, padding=padding)
        return frame


def configure_styles(style):
    """Configure global TTK styles."""
    style.theme_use('clam')
    style.configure('TFrame', background=FRAME_BG)
    style.configure('TLabel', background=FRAME_BG, foreground=LABEL_FG, font=FONTS['label'])
    style.configure('Header.TLabel', background=HEADER_BG, foreground=HEADER_FG, font=FONTS['heading'])
    style.configure('SubHeader.TLabel', background=FRAME_BG, foreground=PRIMARY_COLOR, font=FONTS['subheading'])
    style.configure('TButton', font=FONTS['button'], padding=12, background=BUTTON_BG, foreground=BUTTON_FG, borderwidth=0)
    style.map('TButton',
        background=[('active', BUTTON_HOVER_BG), ('!disabled', BUTTON_BG)],
        foreground=[('active', BUTTON_FG), ('!disabled', BUTTON_FG)])
    style.configure('TEntry', padding=10, font=FONTS['entry'], fieldbackground=ENTRY_BG, foreground=ENTRY_FG)
    style.configure('TCombobox', padding=10, font=FONTS['entry'], fieldbackground=ENTRY_BG, foreground=ENTRY_FG)
    style.configure('TNotebook', background=FRAME_BG, tabposition='n')
    style.configure('TNotebook.Tab', font=FONTS['button'], padding=[20, 12], background=ACCENT_COLOR, foreground=PRIMARY_COLOR)
    style.map('TNotebook.Tab',
        background=[('selected', '#334155')],
        foreground=[('selected', PRIMARY_COLOR)])
    style.configure('Treeview', font=FONTS['tree'], rowheight=36, fieldbackground=FRAME_BG, background=FRAME_BG, foreground=LABEL_FG)
    style.configure('Treeview.Heading', font=FONTS['tree_heading'], background=TREE_HEADER_BG, foreground=TREE_HEADER_FG)
    style.map('Treeview', background=[('selected', '#2563eb')], foreground=[('selected', '#f1f5f9')])
    style.configure('TLabelframe', background=FRAME_BG, borderwidth=0)
    style.configure('TLabelframe.Label', background=FRAME_BG, foreground=PRIMARY_COLOR)