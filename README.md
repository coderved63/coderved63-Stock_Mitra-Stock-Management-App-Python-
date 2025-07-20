# Stock Mitra

[![Windows](https://img.shields.io/badge/platform-Windows-blue)]()
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Stock Mitra** is a modern, user-friendly inventory and stock management application for distributors, wholesalers, and businesses of all sizes.

- 📦 Manage stock for any company
- 🖱️ Simple, beautiful interface
- 🗃️ All data stored safely on your computer
- 🚀 No technical knowledge or Python installation required—just download and run!

## Table of Contents

- [Screenshots](#screenshots)
- [Features](#features)
- [Quick Start (No Python Needed)](#quick-start-no-python-needed)
- [Developer Setup](#developer-setup)
- [Usage Guide](#usage-guide)
- [Data Storage](#data-storage)
- [FAQ](#faq)
- [Contributing](#contributing)
- [Contact](#contact)

## Screenshots

### Dashboard
![Dashboard Screenshot](https://github.com/user-attachments/assets/8195d53c-0687-48dc-a870-ca443661eef6)

### Add Stock
![Add Stock Screenshot](https://github.com/user-attachments/assets/1164b293-22d1-4e6f-8f3c-e183a0f7bc73)

### Company Selection
![Company Selection Screenshot](https://github.com/user-attachments/assets/6debcc69-fc5c-44b4-bdf4-4e02ca7dff0c)

## Features

- Multi-company support: manage stock for any number of companies
- Add, update, and sell stock with ease
- Modern, dark-themed interface
- No Python required for end users (Windows EXE provided)
- Data stored securely in your Documents folder
- Easy switching between companies
- User-friendly error messages and guidance

## Quick Start (No Python Needed)

**Stock Mitra is designed for everyone—even if you don’t have Python installed!**

1. **Download the latest Stock Mitra executable (`.exe`) from our [Google Drive link](https://drive.google.com/drive/folders/16ghRTsO31DUkUIWFr4tru6TuJwOqvux4?usp=sharing) or the [Releases](https://github.com/your-username/your-repo/releases) section.**
2. **Extract the ZIP file (if provided).**
3. **Double-click `New_Stock_mngr_app.exe` to start Stock Mitra!**
   - No installation, no setup, no Python required.
   - All your data is stored safely in your Documents folder.

> **Note:** If you see a Windows security warning, click “More info” and then “Run anyway.”  
> If you get a permissions error, try running as administrator.

## Developer Setup

If you want to run or modify Stock Mitra from source, follow these steps:

### Requirements
- Python 3.8 or higher
- `tkinter` (usually included with Python)

### Installation
1. **Clone the repository:**
   ```sh
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
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
   *(If you don't have a requirements.txt, just ensure Python and tkinter are installed.)*

### Running the App
```sh
python Pythonbot/New_Stock_mngr_app.py
```

- The app will launch in a window. You can now use all features as described above.

## Usage Guide

### First Launch
- On first launch, you’ll be greeted with a welcome message.
- You’ll be prompted to enter your company name and select or create a JSON file for your company’s stock data.
- You can add more companies later from the “Company” menu.

### Adding a Company
- Go to the “Company” menu and select “Add New Company.”
- Enter the company name and choose a location for the company’s data file.
- Switch between companies anytime from the “Company” menu.

### Adding Stock
- Go to the “Add Stock” tab.
- Fill in the product details (Product ID, Name, Location, etc.).
- Enter the number of cartons and details for each carton.
- Click “Add Stock” to save.
- The company name is shown at the top and cannot be changed here (it’s always the currently selected company).
- ![Add Stock Screenshot](https://github.com/user-attachments/assets/1164b293-22d1-4e6f-8f3c-e183a0f7bc73)

### Selling Stock
- Go to the “Sell Stock” tab.
- Enter the Product ID or Name to find the product.
- Specify the number of full cartons and/or loose pieces to sell.
- Click “Process Sale” to update the stock.

### Viewing Reports
- The “Dashboard” tab shows an overview of your stock, including live, damaged, and expired stock.
- Click “View [Company] Stock Details” for a detailed, product-wise breakdown.
- ![Dashboard Screenshot](https://github.com/user-attachments/assets/8195d53c-0687-48dc-a870-ca443661eef6)

### Switching Companies
- Use the “Company” menu to switch between companies or add new ones at any time.
- All data and views will update to reflect the selected company.

## Data Storage

- **Each company’s stock data is stored in its own JSON file.**
- By default, these files are saved in your **Documents** folder (e.g., `C:\Users\YourName\Documents\StockMitraData\`).
- You can choose a different location when creating a new company.
- **To back up your data:** Simply copy the JSON files to a safe location (USB drive, cloud storage, etc.).
- **To move your data to a new computer:** Copy the JSON files to the same location on the new computer and select them when adding or switching companies in Stock Mitra.
- Your data is never sent to the cloud or any third party—**it stays on your computer.**

## FAQ

### I get a "Permission Denied" or "Access is Denied" error when running the app.
- Make sure you have permission to write to the folder where your data is stored (usually your Documents folder).
- Try running the app as administrator.
- Avoid running the app from a protected system folder (like `C:\Program Files`).

### My antivirus or Windows SmartScreen warns me about the app. Is it safe?
- If you downloaded Stock Mitra from the official Google Drive link or GitHub Releases, it is safe.
- Click “More info” and then “Run anyway” to proceed.
- If you have concerns, you can scan the file with your antivirus or check the source code on GitHub.

### The app won’t start and says something about missing Python or tkinter.
- This only applies if you are running from source (not the .exe).
- Make sure you have Python 3.8+ and tkinter installed.
- On Windows, tkinter is included with most Python installations.

### How do I reset or delete all my data?
- You can delete the company’s JSON file(s) from your Documents folder or wherever you saved them.
- Be careful: this cannot be undone!

### How do I move my data to a new computer?
- Copy your company’s JSON file(s) to the new computer.
- When you first run Stock Mitra, select the existing JSON file when adding or switching companies.

### I found a bug or have a feature request. What should I do?
- Please open an issue on the GitHub repository or contact the maintainer (see Contact section below).

## Contributing

We welcome all contributions to Stock Mitra!

- **Found a bug?** Please [open an issue](https://github.com/your-username/your-repo/issues).
- **Have a feature request?** Open an issue or start a discussion.
- **Want to submit code?** Fork the repo, create a new branch, and submit a pull request.

All feedback, suggestions, and improvements are appreciated. Thank you for helping make Stock Mitra better for everyone!
