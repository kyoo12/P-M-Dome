import csv
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

# --- Config ---
DRY_RUN = False
LOG_FILE = "smart_closing_debug_log.csv"
AUCTION_ID = 1003
START_URL = f"https://dome-auctions.com/administration/auctions/{AUCTION_ID}/?page=1"
TOP_LOT_CUTOFF = 1000  # in CHF
END_HOUR = 17

# --- Time Rules ---
subcategory_rules = {
    1: {
        "time_range": (14, 14),
        "subcategories": {
            "manual tools", "Battery tools", "Measuring instruments",
            "Fastening material", "Pneumatic tools", "Cleaning equipment",
            "Installation material", "Fastening machines", "Tooling"
        }
    },
    2: {
        "time_range": (14, 15),
        "price_over": TOP_LOT_CUTOFF  # Top lots
    },
    3: {
        "time_range": (15, 15),
        "subcategories": {
            "Welding machines", "Welding tables", "Welding parts & accessories",
            "Press brake tools", "Processing machines", "Forming machines", "Grinders",
            "Polishing machines", "CNC lathes", "Vertical machining centers", "Robots",
            "Separator systems", "Deburring machines"
        }
    },
    4: {
        "time_range": (15, 16),
        "subcategories": {
            "Workshop Inventory", "Warehouse inventory", "Forklifts", "Pallets",
            "Waste containers", "racking", "Car trailers", "Metal stock", "Intern transport",
            "Stock storage"
        }
    },
    5: {
        "time_range": (16, 16),
        "subcategories": {
            "Office units", "IT equipment", "Electrical installation materials",
            "Electrical components", "Various metalworking", "Office inventory",
            "Packaging equipment", "Computer & tablets", "Printers, scanners and Copiers"
        }
    },
}

def random_time(start, end):
    if start == end:
        return f"{start:02d}:{random.randint(0, 59):02d}"
    return f"{random.randint(start, end - 1):02d}:{random.randint(0, 59):02d}"

def categorize(subcat, price):
    price = float(price) if price else 0
    for rule_id, rule in subcategory_rules.items():
        if 'subcategories' in rule and subcat in rule['subcategories']:
            return rule_id, rule["time_range"], f"Matched subcategory in rule {rule_id}"
        if 'price_over' in rule and price >= rule['price_over']:
            return rule_id, rule["time_range"], f"Estimate {price} ≥ {rule['price_over']}"
    return 6, (14, END_HOUR), "Fallback to Rule 6"

# --- Setup driver ---
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get(START_URL)
input("🔐 Log in manually, then press ENTER to continue...")

lot_data = {}
seen_ids = set()
page = 1

while True:
    print(f"\n📄 Scanning page {page}...")
    driver.get(f"https://dome-auctions.com/administration/auctions/{AUCTION_ID}/?page={page}")
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
    except TimeoutException:
        print("🛑 No table found, stopping.")
        break

    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    if not rows:
        print("🛑 No rows found, stopping.")
        break

    new_lots = 0
    for row in rows:
        try:
            link = row.find_element(By.CSS_SELECTOR, 'a[href*="/lots/"]')
            lot_id = int(link.get_attribute("href").split("/lots/")[1].split("/")[0])
            if lot_id in seen_ids:
                continue
            seen_ids.add(lot_id)

            estimate_cell = row.find_elements(By.TAG_NAME, "td")[6]
            estimate = estimate_cell.text.replace("CHF", "").replace(",", "").strip()
            bid_cell = row.find_elements(By.TAG_NAME, "td")[7].text.strip()
            has_bid = bid_cell != "" and bid_cell != "—"

            lot_data[lot_id] = {
                "url": link.get_attribute("href"),
                "estimate": estimate,
                "has_bid": has_bid
            }
            print(f"   ✔ Found lot {lot_id} with estimate CHF {estimate}")
            new_lots += 1

        except Exception as e:
            print(f"   ❌ Failed to process row: {e}")

    if new_lots == 0:
        print("🛑 No new lots found — likely last page.")
        break
    page += 1

# --- Process Lots ---
log = []
for lot_id, data in sorted(lot_data.items()):
    print(f"\n🔍 Lot {lot_id}: {data['url']}")
    driver.get(data["url"])

    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "id_closing_date_1")))

        # Subcategory
        subcat = driver.find_element(By.ID, "id_subcategory").find_element(By.CSS_SELECTOR, "option:checked").text.strip()

        # Title
        title = driver.find_element(By.CSS_SELECTOR, "h1.h2.mb-0").text.strip()

        rule_id, (start_hr, end_hr), reason = categorize(subcat, data["estimate"])
        new_time = random_time(start_hr, end_hr)
        current_time = driver.find_element(By.ID, "id_closing_date_1").get_attribute("value")

        print(f"   📌 Title: {title}")
        print(f"   🧭 Subcategory: {subcat} | Rule: {rule_id} | Reason: {reason}")
        print(f"   ⏱ Current: {current_time} → New: {new_time}")

        if current_time == new_time:
            log.append([lot_id, title, rule_id, subcat, data["estimate"], data["has_bid"], current_time, new_time, "Skipped", "Already correct"])
            continue

        if not DRY_RUN:
            input_field = driver.find_element(By.ID, "id_closing_date_1")
            input_field.clear()
            input_field.send_keys(new_time)
            input_field.send_keys(Keys.TAB)
            save_btn = WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.NAME, "save_exit")))
            driver.execute_script("arguments[0].click();", save_btn)

        log.append([lot_id, title, rule_id, subcat, data["estimate"], data["has_bid"], current_time, new_time,
                    "DRY RUN" if DRY_RUN else "Updated", reason])
    except Exception as e:
        print(f"   ❌ Error: {e}")
        log.append([lot_id, "N/A", "N/A", "N/A", data["estimate"], data["has_bid"], "N/A", "N/A", "Error", f"Message: {e}"])

driver.quit()

# --- Export log ---
df = pd.DataFrame(log, columns=[
    "Lot ID", "Title", "Rule ID", "Subcategory", "Estimated", "Has Bid", "Old Time", "New Time", "Status", "Note"
])
df.to_csv(LOG_FILE, index=False)
print(f"\n📦 Done. Log saved to {LOG_FILE}")
