
# Dome Auctions Lot Field Checker

This script compares Title, Description, and Starting Bid for each lot against a given Excel sheet.

## ✅ Required:
- Chrome installed
- Python 3.8+
- ChromeDriver (auto-managed)
- Dependencies:

```
pip install selenium pandas openpyxl webdriver-manager
```

## ▶️ How to Run:

1. Place `Marton AG1420251052.xlsx` in the same folder as this script.
2. Run:
```
python check_title_description_bid.py
```
3. Log in manually when prompted.
4. The script will go through each lot and compare the fields.
5. Mismatches will be saved to `title_description_bid_discrepancies.csv`.

Done!
