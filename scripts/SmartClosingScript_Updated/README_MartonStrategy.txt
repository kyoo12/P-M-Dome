# Smart Closing Time Updater (Marton Strategy)

This automation script updates auction lot closing times based on subcategory, price, and other rules. It ensures an orderly, human-like time distribution for online lots and respects business priorities.

---

## 🎯 Rules Overview

| Rule ID | Time Range     | Description                                                            | Criteria |
|---------|----------------|------------------------------------------------------------------------|---------|
| 1       | 14:00 – 14:30  | Warm-up: small items, loose tools (not machines or machine parts), max 30–40 lots | `manual tools`, `Battery tools`, `Measuring instruments`, `Fastening material`, `Pneumatic tools`, `Cleaning equipment`, `Installation material`, `Fastening machines`, `Tooling` |
| 2       | 14:30 – 16:00  | Top machines (≥ 3000 CHF) and anything not related to other groups      | All machines estimated over 3000 CHF (Laser cutting, CNC, Press brakes, etc.) |
| 3       | 16:00 – 17:00  | Other machines, welding, spare parts, then combinations                | `Welding machines`, `Welding tables`, `Welding parts & accessories`, `Press brake tools`, `Processing machines`, `Forming machines`, `Grinders`, `Polishing machines`, `CNC lathes`, `Vertical machining centers`, `Robots`, `Separator systems`, `Deburring machines` |
| 4       | 17:00 – 18:00  | Remaining stock, inventory, rolling stock                             | `Workshop Inventory`, `Warehouse inventory`, `Forklifts`, `Pallets`, `Waste containers`, `racking`, `Car trailers`, `Metal stock`, `Intern transport`, `Stock storage` |
| 5       | 17:30 – 19:00  | Everything else: office-related and leftovers                         | `Office units`, `IT equipment`, `Electrical installation materials`, `Electrical components`, `Various metalworking`, `Office inventory`, `Packaging equipment`, `Computer & tablets`, `Printers, scanners and Copiers` |
| 6       | Up to 19:00    | Extension buffer (uncategorized) — no lot goes past 19:00              | Anything uncategorized or not matched in rules above |

---

## 💡 Features

- **Selenium-driven scraping** of all lots from Dome Auctions.
- Determines optimal closing times by **subcategory, bid, and price**.
- **Dry run mode** allows previewing before making live changes.
- **CSV export** logs every decision.

---

## ⚙️ Usage

1. Install dependencies:

```
pip install selenium pandas webdriver-manager
```

2. Run the script:

```
python update_closing_times_by_marton.py
```

3. Login manually when prompted. Script takes over after login.

---

## 📁 Output CSV

The CSV includes:
- Lot ID
- Category (matched rule group)
- Subcategory
- Estimated Price
- Bid Presence
- Old Time
- New Time
- Rule ID
- Status (DRY RUN / Updated / Skipped)
- Note

---

## 👀 Notes

- The script intelligently halts if pages repeat.
- Time ranges are randomized **within defined intervals** to simulate natural pacing.
- Script respects the lot editing format of Dome Auctions and ensures lot combinations remain near each other.

---

🛠 Made for Dome Auctions — internal use only.