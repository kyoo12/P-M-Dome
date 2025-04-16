import csv
import random
from datetime import datetime, timedelta
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
DRY_RUN = False  # Set to False to actually apply the changes
LOG_FILE = "smart_closing_times.csv"

office_it_subcats = {
    "Electrical components", "Electrical installation materials", "Internal transportation",
    "IT equipment", "Computer & tablets", "Office inventory", "Printers, scanners and Copiers", "Office units"
}

workshop_subcats = {
    "Workshop Inventory", "Welding tables", "Racking", "Manual tools",
    "Ladders and stairs", "Tooling", "Battery tools"
}

def random_time(start_hour, end_hour):
    hour = random.randint(start_hour, end_hour - 1)
    minute = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}"

def categorize(subcat, price, has_bid):
    try:
        price_val = float(price)
    except:
        return "fallback", (14, 19), 6  # fallback = rule 6

    if subcat in office_it_subcats:
        return "Office/IT", (18, 19), 1
    elif subcat in workshop_subcats:
        return "Workshop/Tools", (17, 18), 2
    elif price_val < 4000 and has_bid:
        return "Warm-up", (14, 15), 3
    elif price_val < 4000:
        return "Small Machine", (16, 17), 4
    elif price_val >= 4000:
        return "Expensive", (15, 16), 5
    else:
        return "Other", (14, 19), 6

# --- Setup browser ---
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# --- Login manually ---
driver.get("https://dome-auctions.com/administration/auctions/1001/?page=1")
input("🔐 Log in manually, then press ENTER to continue...")

# --- Collect lot data ---
lot_data = {}
seen_ids = set()
page = 1

while True:
    print(f"📄 Scanning page {page}...")
    driver.get(f"https://dome-auctions.com/administration/auctions/1001/?page={page}")

    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
    except TimeoutException:
        print(f"🚫 No table on page {page}. Stopping.")
        break

    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    if not rows:
        print(f"⚠️ No rows found — stopping.")
        break

    valid_lots_this_page = 0
    new_lots_this_page = 0

    for row in rows:
        try:
            links = row.find_elements(By.CSS_SELECTOR, 'a[href*="/lots/"]')
            if not links:
                continue
            link = links[0]

            lot_id = int(link.get_attribute("href").split("/lots/")[1].split("/")[0])
            if lot_id in seen_ids:
                continue

            seen_ids.add(lot_id)

            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 7:
                continue

            estimate_text = cells[6].text.replace("CHF", "").replace(",", "").strip()
            bid_text = cells[7].text.strip()
            has_bid = bid_text and bid_text != "—"

            lot_data[lot_id] = {
                "url": link.get_attribute("href"),
                "estimate": estimate_text,
                "has_bid": has_bid
            }
            valid_lots_this_page += 1
            new_lots_this_page += 1
            print(f"   ✔ Lot {lot_id} scraped.")

        except Exception as e:
            print(f"   ❌ Error scraping row: {e}")

    if new_lots_this_page == 0:
        print("🛑 No new lots found — likely hit the final page. Stopping.")
        break

    page += 1

# --- Process each lot ---
log = []
sorted_lots = sorted(lot_data.items())
print(f"\n🔢 Total lots to process: {len(sorted_lots)}")

for idx, (lot_id, data) in enumerate(sorted_lots):
    print(f"\n🔍 Processing Lot ID {lot_id} → {data['url']}")
    driver.get(data["url"])

    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "id_closing_date_1")))
        subcat = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "id_subcategory"))
        ).find_element(By.CSS_SELECTOR, "option:checked").text.strip()

        category, (start_hr, end_hr), rule_id = categorize(subcat, data["estimate"], data["has_bid"])
        new_time = random_time(start_hr, end_hr)

        time_input = driver.find_element(By.ID, "id_closing_date_1")
        current_val = time_input.get_attribute("value")

        if current_val == new_time:
            print("   ✅ Time already correct.")
            log.append([
                lot_id, category, subcat, data["estimate"], data["has_bid"],
                current_val, new_time, "Skipped", "Already correct", rule_id
            ])
            continue

        print(f"   🕓 Assigning new time: {new_time} (Rule {rule_id})")
        if not DRY_RUN:
            time_input.clear()
            time_input.send_keys(new_time)
            time_input.send_keys(Keys.TAB)

            save = WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.NAME, "save_exit")))
            driver.execute_script("arguments[0].click();", save)
            WebDriverWait(driver, 6).until(EC.url_contains("/auctions/1001"))

            log.append([
                lot_id, category, subcat, data["estimate"], data["has_bid"],
                current_val, new_time, "Updated", "Time changed", rule_id
            ])
        else:
            log.append([
                lot_id, category, subcat, data["estimate"], data["has_bid"],
                current_val, new_time, "DRY RUN", "No change made", rule_id
            ])

    except Exception as e:
        print(f"   ❌ Error: {e}")
        log.append([lot_id, "N/A", "N/A", data["estimate"], data["has_bid"], "N/A", "N/A", "Error", str(e), "N/A"])

driver.quit()

df = pd.DataFrame(log, columns=[
    "Lot ID", "Category", "Subcategory", "Estimated Price", "Has Bid",
    "Old Time", "New Time", "Status", "Note", "Rule ID"
])
df.to_csv(LOG_FILE, index=False)
print(f"\n📄 Log saved to: {LOG_FILE}")
