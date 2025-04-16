# Dome Auctions – Closing Time Auto-Updater

This script automatically updates the **closing times** of auction lots on the Dome Auctions admin panel.

---

## ✅ Features

- Distributes closing times **evenly** between **14:00 and 19:00**
- Automatically detects and sorts all lot edit pages from all admin pages
- Uses the **lot ID in the URL** (e.g. `/lots/1149/update/`) for ordering
- Avoids using the misleading "lot number" in the form
- Skips lots with correct closing time
- Logs all activity (updated, skipped, errors) to a CSV

---

## 🛠 How It Works

1. You log in manually to the Dome Auctions admin interface
2. The script scans all pages to collect lot links
3. Calculates a unique closing time for each lot between 14:00 and 19:00
4. Visits each lot, checks its current closing time
5. Updates the time if needed and clicks **Save and exit**
6. Saves a full `closing_time_changes.csv` log at the end

---

## ▶️ Usage

### 1. Install dependencies

Make sure Python is installed. Then run:

```bash
pip install selenium webdriver-manager pandas
```

### 2. Run the script

```bash
python update_lots_distributed.py
```

### 3. Follow the prompt

A Chrome browser will open. Log in manually, then return to the terminal and press ENTER.

---

## 📝 Output

After running, a file named:

```
closing_time_changes.csv
```

Will be created with columns:

- `Lot #`
- `Lot URL`
- `Expected Time`
- `Current Time`
- `Status`
- `Note`

---

## 💡 Tips

- You can re-run the script any time to re-check and fix missed lots
- The script always respects the 14:00–19:00 time range
- You can adjust the start/end time directly in the script:
  ```python
  START_TIME = datetime.strptime("14:00", "%H:%M")
  END_TIME = datetime.strptime("19:00", "%H:%M")
  ```

---

## ⚠️ Warnings

- Don’t run this while manually editing lots!
- Avoid editing other fields during automated time updates

---

Enjoy!
