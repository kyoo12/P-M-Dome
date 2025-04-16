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
DRY_RUN = False  # If True, no changes will be applied; only logs will be generated
LOG_FILE = "marton_closing_times.csv"  # File to save the log of processed lots

# Rule-based subcategories and their respective time ranges
rule_1_subcats = {
    "manual tools", "Battery tools", "Measuring instruments", "Fastening material",
    "Pneumatic tools", "Cleaning equipment", "Installation material", "Fastening machines", "Tooling"
}
rule_3_subcats = {
    "Welding machines", "Welding tables", "Welding parts & accessories", "Press brake tools",
    "Processing machines", "Forming machines", "Grinders", "Polishing machines", "CNC lathes",
    "Vertical machining centers", "Robots", "Separator systems", "Deburring machines"
}
rule_4_subcats = {
    "Workshop Inventory", "Warehouse inventory", "Forklifts", "Pallets", "Waste containers",
    "racking", "Car trailers", "Metal stock", "Intern transport", "Stock storage"
}
rule_5_subcats = {
    "Office units", "IT equipment", "Electrical installation materials", "Electrical components",
    "Various metalworking", "Office inventory", "Packaging equipment", "Computer & tablets",
    "Printers, scanners and Copiers"
}

# Function to generate a random time within a given hour range
def random_time(start_hour, end_hour):
    hour = random.randint(start_hour, end_hour - 1)
    minute = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}"

# Function to categorize lots based on subcategory, price, and bid status
def categorize(subcat, price, has_bid):
    try:
        price_val = float(price)  # Convert price to float for comparison
    except:
        # Fallback category if price conversion fails
        return "fallback", (14, 19), 6

    # Determine category and time range based on rules
    if subcat in rule_1_subcats:
        return "Warm-up", (14, 15), 1
    elif price_val >= 3000:
        return "Top machines", (14, 16), 2
    elif subcat in rule_3_subcats:
        return "Other machines & welding", (16, 17), 3
    elif subcat in rule_4_subcats:
        return "Stock & rolling", (17, 18), 4
    elif subcat in rule_5_subcats:
        return "Office & misc.", (17, 19), 5
    else:
        return "Buffer zone", (14, 19), 6

# --- Setup browser ---
# Configure Chrome browser options
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # Start browser maximized
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# --- Login manually ---
# Open the auction page and prompt the user to log in manually
driver.get("https://dome-auctions.com/administration/auctions/1001/?page=1")
input("🔐 Log in manually, then press ENTER to continue...")

# --- Collect lot data ---
lot_data = {}  # Dictionary to store lot details
seen_ids = set()  # Set to track already processed lot IDs
page = 1  # Start from the first page

while True:
    print(f"📄 Scanning page {page}...")
    driver.get(f"https://dome-auctions.com/administration/auctions/1001/?page={page}")

    try:
        # Wait for the table to load on the page
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
    except TimeoutException:
        # Stop if no table is found on the page
        print(f"🚫 No table on page {page}. Stopping.")
        break

    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    if not rows:
        # Stop if no rows are found in the table
        print(f"⚠️ No rows found — stopping.")
        break

    new_lots_this_page = 0  # Counter for new lots found on the current page

    for row in rows:
        try:
            # Extract lot links from the row
            links = row.find_elements(By.CSS_SELECTOR, 'a[href*="/lots/"]')
            if not links:
                continue
            link = links[0]
            lot_id = int(link.get_attribute("href").split("/lots/")[1].split("/")[0])
            if lot_id in seen_ids:
                # Skip already processed lots
                continue

            seen_ids.add(lot_id)  # Mark lot as seen
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 7:
                # Skip rows with insufficient data
                continue

            # Extract estimate and bid status
            estimate_text = cells[6].text.replace("CHF", "").replace(",", "").strip()
            bid_text = cells[7].text.strip()
            has_bid = bid_text and bid_text != "—"

            # Store lot data
            lot_data[lot_id] = {
                "url": link.get_attribute("href"),
                "estimate": estimate_text,
                "has_bid": has_bid
            }
            new_lots_this_page += 1
            print(f"   ✔ Lot {lot_id} scraped.")

        except Exception as e:
            # Handle errors during row processing
            print(f"   ❌ Error scraping row: {e}")

    if new_lots_this_page == 0:
        # Stop if no new lots are found on the current page
        print("🛑 No new lots found — likely hit the final page. Stopping.")
        break

    page += 1  # Move to the next page

# --- Process lots ---
log = []  # List to store log entries
sorted_lots = sorted(lot_data.items())  # Sort lots by ID
print(f"🔢 Processing {len(sorted_lots)} lots")

for lot_id, data in sorted_lots:
    print(f"\n🔍 Lot {lot_id}: {data['url']}")
    driver.get(data["url"])
    try:
        # Wait for the closing date input field to load
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "id_closing_date_1")))
        # Extract the subcategory of the lot
        subcat = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "id_subcategory"))
        ).find_element(By.CSS_SELECTOR, "option:checked").text.strip()

        # Categorize the lot and determine the new closing time
        category, (start_hr, end_hr), rule_id = categorize(subcat, data["estimate"], data["has_bid"])
        new_time = random_time(start_hr, end_hr)
        time_input = driver.find_element(By.ID, "id_closing_date_1")
        current_val = time_input.get_attribute("value")

        if current_val == new_time:
            # Skip if the current time is already correct
            print("   ✅ Already set correctly.")
            log.append([lot_id, category, subcat, data["estimate"], data["has_bid"], current_val, new_time, "Skipped", "Already correct", rule_id])
            continue

        print(f"   🕓 Changing to: {new_time} (Rule {rule_id})")
        if not DRY_RUN:
            # Update the closing time if not in dry run mode
            time_input.clear()
            time_input.send_keys(new_time)
            time_input.send_keys(Keys.TAB)
            save = WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.NAME, "save_exit")))
            driver.execute_script("arguments[0].click();", save)
            WebDriverWait(driver, 6).until(EC.url_contains("/auctions/1001"))

        log.append([lot_id, category, subcat, data["estimate"], data["has_bid"], current_val, new_time, "DRY RUN" if DRY_RUN else "Updated", "No change made" if DRY_RUN else "Time changed", rule_id])

    except Exception as e:
        # Handle errors during lot processing
        print(f"   ❌ Error: {e}")
        log.append([lot_id, "N/A", "N/A", data["estimate"], data["has_bid"], "N/A", "N/A", "Error", str(e), "N/A"])

# Close the browser
driver.quit()

# Convert the log list to a DataFrame
columns = ["Lot ID", "Category", "Subcategory", "Estimate", "Has Bid", "Current Time", "New Time", "Status", "Details", "Rule ID"]
df = pd.DataFrame(log, columns=columns)

# Save the log to a CSV file with a safe save fallback
try:
    df.to_csv(LOG_FILE, index=False)
    print(f"📄 Log saved to: {LOG_FILE}")
except PermissionError:
    fallback = LOG_FILE.replace(".csv", "_autosave.csv")
    df.to_csv(fallback, index=False)
    print(f"⚠️ Original log was open, so saved to: {fallback}")
