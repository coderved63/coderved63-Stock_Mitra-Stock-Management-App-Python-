# Stock Mitra

[![Windows](https://img.shields.io/badge/platform-Windows-blue)]()
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Stock Mitra** is a modern, user-friendly inventory and stock management application for distributors, wholesalers, and businesses of all sizes.

- 📦 Manage stock for any company
- 🖱️ Simple, beautiful interface  
- �️ All data stored safely on your computer
- 🚀 No technical knowledge or Python installation required—just download and run!

## Table of Contents

- [Screenshots](#screenshots)
- [Features](#features)
- [Quick Start (No Python Needed)](#quick-start-no-python-needed)
- [Developer Setup](#developer-setup)
- [Usage Guide](#usage-guide)
- [Project Structure](#project-structure)
- [Data Storage](#data-storage)
- [FAQ](#faq)
- [Contributing](#contributing)
- [Contact](#contact)

## Features

- Multi-company support: manage stock for any number of companies
- Add, update, and sell stock with ease
- Modern, dark-themed interface
- No Python required for end users (Windows EXE provided)
- Data stored securely in your Documents folder
- Easy switching between companies
- User-friendly error messages and guidance

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

## Quick Start (No Python Needed)

**Stock Mitra is designed for everyone—even if you don't have Python installed!**

1. **Download the latest Stock Mitra executable (`.exe`) from our [Google Drive link](#) or the [Releases](https://github.com/coderved63/coderved63-Stock_Mitra-Stock-Management-App-Python-/releases) section.**
2. **Extract the ZIP file (if provided).**
3. **Double-click `app.exe` to start Stock Mitra!**
   - No installation, no setup, no Python required.
   - All your data is stored safely in your Documents folder.

> **Note:** If you see a Windows security warning, click "More info" and then "Run anyway."  
> If you get a permissions error, try running as administrator.

## Developer Setup

If you want to run or modify Stock Mitra from source, follow these steps:

### Requirements
- Python 3.8 or higher
- `tkinter` (usually included with Python)

### Installation
1. **Clone the repository:**
   ```sh
   git clone https://github.com/coderved63/coderved63-Stock_Mitra-Stock-Management-App-Python-.git
   cd coderved63-Stock_Mitra-Stock-Management-App-Python-
   ```
2. **(Optional) Create a virtual environment:**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

### Running the App
```sh
# Option 1: Run from Source (Recommended)
python app.py

# Option 2: Using batch file (Windows)
run.bat

# Option 3: Direct execution
python main.py
```

- The app will launch in a window. You can now use all features as described below.

## Usage Guide

### First Launch
- On first launch, you'll be greeted with a welcome message.
- You'll be prompted to enter your company name and select or create a JSON file for your company's stock data.
- You can add more companies later from the "Company" menu.

### Adding a Company
- Go to the "Company" menu and select "Add New Company."
- Enter the company name and choose a location for the company's data file.
- Switch between companies anytime from the "Company" menu.

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

### Adding Stock
- Go to the "Add Stock" tab.
- Fill in the product details (Product ID, Name, Location, etc.).
- Enter the number of cartons and details for each carton.
- Click "Add Stock" to save.
- The company name is shown at the top and cannot be changed here (it's always the currently selected company).
- ![Add Stock Screenshot](https://github.com/user-attachments/assets/1164b293-22d1-4e6f-8f3c-e183a0f7bc73)

### Selling Stock
- Go to the "Sell Stock" tab.
- Enter the Product ID or Name to find the product.
- Specify the number of full cartons and/or loose pieces to sell.
- Click "Process Sale" to update the stock.

### Viewing Reports
- The "Dashboard" tab shows an overview of your stock, including live, damaged, and expired stock.
- Click "View [Company] Stock Details" for a detailed, product-wise breakdown.
- ![Dashboard Screenshot](https://github.com/user-attachments/assets/8195d53c-0687-48dc-a870-ca443661eef6)

### Switching Companies
- Use the "Company" menu to switch between companies or add new ones at any time.
- All data and views will update to reflect the selected company.

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

## Data Storage

- **Each company's stock data is stored in its own JSON file.**
- By default, these files are saved in your **Documents** folder (e.g., `C:\Users\YourName\Documents\StockMitraData\`).
- You can choose a different location when creating a new company.
- **To back up your data:** Simply copy the JSON files to a safe location (USB drive, cloud storage, etc.).
- **To move your data to a new computer:** Copy the JSON files to the same location on the new computer and select them when adding or switching companies in Stock Mitra.
- Your data is never sent to the cloud or any third party—**it stays on your computer.**

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

### I get a "Permission Denied" or "Access is Denied" error when running the app.
- Make sure you have permission to write to the folder where your data is stored (usually your Documents folder).
- Try running the app as administrator.
- Avoid running the app from a protected system folder (like `C:\Program Files`).

### My antivirus or Windows SmartScreen warns me about the app. Is it safe?
- If you downloaded Stock Mitra from the official Google Drive link or GitHub Releases, it is safe.
- Click "More info" and then "Run anyway" to proceed.
- If you have concerns, you can scan the file with your antivirus or check the source code on GitHub.

### The app won't start and says something about missing Python or tkinter.
- This only applies if you are running from source (not the .exe).
- Make sure you have Python 3.8+ and tkinter installed.
- On Windows, tkinter is included with most Python installations.

### How do I reset or delete all my data?
- You can delete the company's JSON file(s) from your Documents folder or wherever you saved them.
- Be careful: this cannot be undone!

### How do I move my data to a new computer?
- Copy your company's JSON file(s) to the new computer.
- When you first run Stock Mitra, select the existing JSON file when adding or switching companies.

### I found a bug or have a feature request. What should I do?
- Please open an issue on the GitHub repository or contact the maintainer (see Contact section below).

### ❓ **Technical Questions**

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

We welcome all contributions to Stock Mitra!

- **Found a bug?** Please [open an issue](https://github.com/coderved63/coderved63-Stock_Mitra-Stock-Management-App-Python-/issues).
- **Have a feature request?** Open an issue or start a discussion.
- **Want to submit code?** Fork the repo, create a new branch, and submit a pull request.

All feedback, suggestions, and improvements are appreciated. Thank you for helping make Stock Mitra better for everyone!

### 🛠️ **Development Setup**
1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes in the modular structure
4. Test thoroughly with existing data
5. Submit pull request

## Contact

For questions, suggestions, or support:
- **GitHub Issues**: [Report bugs or request features](https://github.com/coderved63/coderved63-Stock_Mitra-Stock-Management-App-Python-/issues)
- **Repository**: [Stock Mitra on GitHub](https://github.com/coderved63/coderved63-Stock_Mitra-Stock-Management-App-Python-)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Stock Mitra - Professional inventory management with modular architecture**

*Built for scalability, designed for usability* ✨

---

**Note**: This refactored version maintains 100% functional compatibility with the original application while providing a much cleaner, more maintainable codebase.