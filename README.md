# Stock Mitra - Professional Inventory Management System

[![Windows](https://img.shields.io/badge/platform-Windows-blue)]()
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Stock Mitra** is a comprehensive, modern inventory and stock management application designed for distributors, wholesalers, and businesses of all sizes. Built with a clean, modular architecture for enhanced maintainability and extensibility.

- 📦 **Multi-Company Management** - Handle inventory for multiple companies
- 🎨 **Modern Dark Interface** - Professional, easy-on-the-eyes design
- 🏗️ **Modular Architecture** - Clean, maintainable codebase
- 🔍 **Smart Search & Suggestions** - Intelligent product recommendations
- 📊 **Comprehensive Reporting** - Detailed analytics and insights
- 🔒 **Local Data Storage** - Your data stays secure on your computer
- 🚀 **User-Friendly** - No technical knowledge required

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [Project Structure](#project-structure)
- [Data Management](#data-management)
- [FAQ](#faq)
- [Contributing](#contributing)

## Features

### 🏢 **Multi-Company Management**
- Manage inventory for unlimited companies
- Easy company switching with separate data files
- Company-specific configurations and reports

### 📊 **Comprehensive Dashboard**
- **Key Metrics**: Live stock, damaged/expired items, total value
- **Smart Alerts**: Low stock warnings, expiry notifications
- **Quick Actions**: One-click access to all major functions
- **Company Stock Overview**: Detailed product-wise breakdown with 13 data columns

### 📦 **Advanced Inventory Features**
- **FIFO/FEFO Support**: First-in-first-out and first-expiry-first-out logic
- **Automatic Carton IDs**: Smart generation (e.g., APX_P001-C01, APX_P001-C02)
- **Batch Tracking**: Individual carton management with unique identifiers
- **Damage Tracking**: Monitor damaged and expired inventory
- **Location Management**: Multi-location inventory support

### 🔍 **Smart Stock Operations**
- **Intelligent Search**: Find products by ID, name, or partial matches
- **Auto-Suggestions**: Smart recommendations when adding stock
- **Auto-Fill**: Automatic form completion based on existing products
- **Bulk Operations**: Add multiple cartons efficiently

### 📈 **Reporting & Analytics**
- **Sales Summary**: Comprehensive sales reports and analytics
- **Transaction Log**: Complete audit trail of all operations
- **Company Overview**: Product-wise inventory analysis with status tracking
- **Export Options**: PDF and other format exports

### 🔧 **Individual Carton Management**
- **Update Quantities**: Adjust stock levels for damage, loss, or corrections
- **Damage Tracking**: Mark and track damaged items
- **Carton Deletion**: Remove cartons permanently with confirmation
- **Status Management**: In Stock ✅, Out of Stock ❌, Damaged ⚠️

## Quick Start

### Option 1: Run from Source (Recommended)
```bash
# 1. Navigate to the refactored directory
cd stock_manager_refactored

# 2. Launch the application
python app.py
```

### Option 2: Alternative Launch Methods
```bash
# Using batch file (Windows)
run.bat

# Direct execution (may have import issues)
python main.py
```

## Usage Guide

### 🚀 **Getting Started**

1. **First Launch**: Stock Mitra will load your existing company data automatically
2. **Company Setup**: Create or switch between companies using the menu
3. **Data Integration**: All existing JSON files work seamlessly
4. **Start Managing**: Access all features through the intuitive interface

### 📊 **Dashboard Operations**

#### Key Metrics Overview
- **Total Live Stock**: Current sellable inventory count
- **Damaged/Expired**: Items requiring attention  
- **Total Cartons**: Overall inventory containers
- **Stock Value**: Total inventory monetary value

#### Quick Actions Bar
All major functions accessible with one click:
- **Add New Stock** | **Find Stock** | **Sell Stock** | **Update Carton**
- **Sales Summary** | **Transaction Log** | **📊 VIEW COMPANY STOCK**

### 📦 **Smart Stock Management**

#### Adding Stock with Auto-Suggestions
1. **Start Typing**: Enter Product ID or Name
2. **Get Suggestions**: System shows matching products from history
3. **Auto-Fill**: Click suggestion to automatically fill details
4. **Bulk Add**: Configure multiple cartons with individual pricing

#### Carton ID Management (Automatic)
- **Format**: `{ProductID}-C{SequentialNumber}`
- **Examples**: APX_P001-C01, APX_P001-C02, APX_P003-C01
- **Smart Generation**: System finds highest number and increments
- **No Manual Input**: Completely automated, error-free

#### Advanced Search & Find
- **Intelligent Matching**: Partial ID/name searches
- **Real-time Results**: Instant search with detailed displays
- **Stock Status**: Live inventory levels and locations

#### Sales Processing
- **FIFO Logic**: First-in-first-out automatic selection
- **Mixed Quantities**: Full cartons + loose pieces
- **Automatic Updates**: Inventory and transaction logging
- **Sales History**: Complete transaction records

#### Individual Carton Updates
- **Find by ID**: Enter specific carton identifier
- **Update Options**: Modify quantities, mark damage, or delete
- **Audit Trail**: All changes logged for tracking
- **Safety Checks**: Confirmation for permanent deletions

### 📈 **Comprehensive Reporting**

#### Company Stock Overview
Navigate to: Dashboard → **📊 VIEW COMPANY STOCK**
- **13 Data Columns**: Complete product analysis
- **Status Indicators**: Visual stock status with icons
- **Financial Data**: MRP, purchase, and sales prices per piece
- **Date Tracking**: Inward, expiry, and outward dates
- **Location Info**: Storage location details

#### Sales & Transaction Reports
- **Sales Summary**: Revenue analysis and product performance
- **Transaction Log**: Complete purchase and sales history
- **Export Options**: PDF generation for external use
- **Monthly Views**: Time-based reporting

## Project Structure

```
stock_manager_refactored/
├── app.py                    # Application launcher
├── main.py                   # Main application logic
├── .gitignore               # Git ignore rules
├── README.md                # This documentation
├── 
├── config/                  # Configuration management
│   ├── __init__.py
│   ├── colors.py           # UI color schemes and themes
│   └── settings.py         # Application settings
│
├── database/                # Data persistence layer
│   ├── __init__.py
│   └── stock_data.py       # JSON data operations
│
├── models/                  # Data models and structures
│   ├── __init__.py
│   └── stock_item.py       # Stock item definitions
│
├── services/                # Business logic layer
│   ├── __init__.py
│   └── stock_manager.py    # Core stock operations and analytics
│
├── ui/                      # User interface components
│   ├── __init__.py
│   ├── base.py             # Base UI components and styling
│   ├── dashboard.py        # Dashboard interface with metrics
│   ├── find_stock.py       # Advanced stock search interface
│   ├── add_stock.py        # Stock addition with auto-suggestions
│   ├── sell_stock.py       # Sales processing interface
│   ├── update_carton.py    # Individual carton management
│   ├── sales_summary.py    # Sales reporting and analytics
│   ├── transaction_log.py  # Transaction history viewer
│   └── company_stock_view.py # Comprehensive company overview
│
└── utils/                   # Utility functions
    ├── __init__.py
    ├── date_utils.py       # Date handling and formatting
    └── file_utils.py       # File operations and path management
```

## Data Management

### 🗃️ **Data Compatibility**
- **Seamless Integration**: Works with all existing JSON files
- **No Migration Needed**: apex_stock.json, tech_stock.json, etc. work as-is
- **Company Configs**: Automatic detection and loading
- **Log Files**: Sales/purchase logs maintained automatically

### 📁 **File Structure**
```
Your Data Directory/
├── company_config.json          # Company configurations
├── apex_stock.json             # APEX company stock data
├── apex_stock_sales_log.json   # APEX sales transactions
├── apex_stock_purchase_log.json # APEX purchase records
├── tech_stock.json             # Tech company stock data
└── tech_stock_sales_log.json   # Tech sales transactions
```

### 🔐 **Data Security & Privacy**
- **Local Storage Only**: All data stays on your computer
- **No Cloud Uploads**: Complete privacy and control
- **Easy Backup**: Simple JSON file copying
- **Cross-Platform**: Works on any system with Python

## FAQ

### ❓ **Common Questions**

**Q: Will this work with my existing data?**
A: Yes! The refactored version uses the same data format and files. No migration needed.

**Q: How are Carton IDs managed?**
A: Completely automatic! Format: ProductID-C01, ProductID-C02, etc. No manual input required.

**Q: What's different from the original?**
A: Same functionality, better code organization. Easier to maintain, extend, and debug.

**Q: Can I still use the original version?**
A: Absolutely! Both versions work with the same data files.

**Q: Is the interface the same?**
A: Yes, with improvements! Added auto-suggestions, better company stock view, and enhanced navigation.

### 🔧 **Technical Benefits**

- **Maintainable Code**: Organized into logical modules
- **Easy Extensions**: Add new features without breaking existing code
- **Better Testing**: Individual components can be unit tested
- **Code Reusability**: Common functionality centralized
- **Clean Architecture**: Clear separation of concerns

## Contributing

### 🤝 **How to Contribute**
- **Bug Reports**: Open GitHub issues for any problems
- **Feature Requests**: Suggest new functionality
- **Code Contributions**: Submit pull requests
- **Documentation**: Help improve guides

### 🛠️ **Development Setup**
1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes in the modular structure
4. Test thoroughly with existing data
5. Submit pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Stock Mitra - Professional inventory management with modular architecture**

*Built for scalability, designed for usability* ✨

---

**Note**: This refactored version maintains 100% functional compatibility with the original application while providing a much cleaner, more maintainable codebase.