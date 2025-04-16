# Smart Closing Time Updater – Dome Auctions

## 🧠 What This Script Does

Automatically updates auction lot closing times on Dome Auctions based on smart category and value-based rules:

### Category Rules:
1. **Office/IT Equipment** – 18:00 to 19:00
2. **Workshop Tools** – 17:00 to 18:00
3. **Warm-up Items** – 14:00 to 15:00 (Estimate < 4000 CHF + Has Bid)
4. **Small Machines** – 15:00 to 16:00 (Estimate < 4000 CHF, not warm-up or tool/office)
5. **Expensive Items** – 16:00 to 17:00 (Estimate > 4000 CHF)
6. **Everything Else** – Random between 14:00 and 19:00

## ⚙️ How It Works

1. Scans all lots in the admin panel.
2. Grabs estimated price and bid info from the table page.
3. Opens each lot's edit page and reads subcategory.
4. Assigns a random closing time within the correct range.
5. Saves the form (unless DRY_RUN is set to True).
6. Writes all results to `smart_closing_times.csv`.

## 🧪 Dry Run Mode

Set this in the script:
```python
DRY_RUN = True  # Only logs, doesn’t change anything
```
Change to `False` to apply changes.

## ▶️ Run Instructions

1. Install dependencies:

```bash
pip install selenium webdriver-manager pandas
```

2. Run the script:

```bash
python update_closing_times_by_criteria.py
```

3. Log in manually to the Dome Auctions admin panel in the browser that opens.

## 📝 Output

A CSV file: `smart_closing_times.csv` containing:
- Lot ID
- Category
- Subcategory
- Estimated Price
- Has Bid
- Old Time
- New Time
- Status
- Notes
