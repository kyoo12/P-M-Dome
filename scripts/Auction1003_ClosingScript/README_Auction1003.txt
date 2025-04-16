# Auction 1003 – Smart Closing Time Script

This script automatically assigns closing times to lots in Auction 1003 on Dome Auctions.

---

## 🧠 Time Rule Strategy

| Rule ID | Time Range     | Description                                       | Subcategory Criteria or Conditions                   |
|---------|----------------|---------------------------------------------------|------------------------------------------------------|
| 1       | 14:00–14:30    | Warm-up: small items, loose tools                 | Battery tools, Printers and toners, IT equipment     |
| 2       | 14:30–15:15    | Top machines (≥ 1000 CHF)                         | Machines by estimated price or subcategory           |
| 3       | 15:15–16:00    | Contractor equipment, electronics, combinations   | Contractor tools, electrical, and combination lots   |
| 4       | 16:00–16:30    | Inventory & stock                                 | Racking, workshop stock, metal stock, accessories    |
| 5       | 16:30–17:00    | Office & leftovers                                | Office units, other industries, fallback lots        |

---

## 🔗 Combination Groups

These lots will be grouped closely together in time:
- Lots 25–57 → Combo: Cable on reels
- Lots 127–145 → Combo: Electrical cabinet components
- Lots 251–277 → Combo: Circuit breakers

---

## ⚙️ Script Usage

1. **Install dependencies:**
```bash
pip install selenium pandas webdriver-manager
```

2. **Run script:**
```bash
python update_closing_times_auction_1003.py
```

3. **Manual login required:**  
   Log in to the auction admin site in the browser window when prompted.

4. **Script will:**
   - Scrape all pages of lots
   - Classify each lot by subcategory, estimated price, and combination rules
   - Assign a randomized closing time within the appropriate window
   - Save all changes (unless DRY_RUN = True)

---

## 📄 Output

The script creates a CSV log named `auction_1003_closing_times.csv` with:

- Lot ID
- Category
- Subcategory
- Estimated Price
- Bid Presence
- Old Time
- New Time
- Status (Updated, DRY RUN, Skipped)
- Note
- Rule ID

---

## 🔒 DRY_RUN Mode

By default, the script runs in **DRY_RUN = True** mode.

To actually save closing times:
```python
DRY_RUN = False
```

---

Developed for Dome Auctions by Aelon Farkash