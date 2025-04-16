
# Dome Auctions Subcategory Checker

This script logs into the Dome Auctions admin interface, navigates through all lots in a given auction, and compares their subcategories against an Excel sheet.

## 📦 Requirements
- Python 3.8+
- Google Chrome
- ChromeDriver (automatically handled)
- Install dependencies:

```
pip install selenium pandas openpyxl webdriver-manager
```

## ▶️ How to Use

1. Place your Excel file (e.g. `Marton AG_Final -2 (1).xlsx`) in the same folder as the script.
2. Run the script:
```
python check_subcategories.py
```
3. Log in to the website manually when prompted.
4. The script will loop through all lots and pages.
5. A file `subcategory_discrepancies.csv` will be created with mismatches.

Enjoy!
