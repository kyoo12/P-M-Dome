from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import pandas as pd

# --- Config ---
START_TIME = datetime.strptime("14:00", "%H:%M")
END_TIME = datetime.strptime("19:00", "%H:%M")
CSV_LOG_PATH = "closing_time_changes.csv"
LOG_ENTRIES = []

# --- Setup browser ---
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# --- Login manually ---
driver.get("https://dome-auctions.com/administration/auctions/1001/?page=1")
input("🔐 Log in manually, then press ENTER...")

lot_links_visited = set()
all_lot_urls = []
page = 1

# --- Collect all lot links from all pages ---
while True:
    print(f"🔍 Scanning page {page}")
    driver.get(f"https://dome-auctions.com/administration/auctions/1001/?page={page}")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    lot_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/lots/') and contains(@href, '/update/')]")
    links = [l.get_attribute("href") for l in lot_links if l.get_attribute("href") not in lot_links_visited]

    if not links:
        break

    for link in links:
        lot_links_visited.add(link)
        all_lot_urls.append(link)

    page += 1

# --- Sort and distribute closing times ---
all_lot_urls = sorted(all_lot_urls, key=lambda url: int(url.split("/lots/")[1].split("/")[0]))
total_lots = len(all_lot_urls)
print(f"\n🔢 Total lots found: {total_lots}")

total_minutes = (END_TIME - START_TIME).seconds // 60
interval_minutes = total_minutes / total_lots  # precise spacing

# --- Process each lot ---
for index, lot_url in enumerate(all_lot_urls):
    closing_time = (START_TIME + timedelta(minutes=index * interval_minutes)).strftime("%H:%M")

    print(f"\n🛠 Lot #{index+1} → {lot_url}")
    print(f"   ⏰ Assigned closing time: {closing_time}")

    try:
        driver.get(lot_url)

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "id_closing_date_1"))
        )

        time_input = driver.find_element(By.ID, "id_closing_date_1")
        current_time = time_input.get_attribute("value")

        if current_time == closing_time:
            print("   ✅ Already correct.")
            LOG_ENTRIES.append([index+1, lot_url, closing_time, current_time, "Skipped", "Already correct"])
            continue

        time_input.clear()
        time_input.send_keys(closing_time)
        time_input.send_keys(Keys.TAB)
        print(f"   ✍️ Updated from {current_time} → {closing_time}")

        save_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.NAME, "save_exit"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", save_button)
        driver.execute_script("arguments[0].click();", save_button)

        WebDriverWait(driver, 6).until(EC.url_contains("/auctions/1001"))
        print("   💾 Saved and exited.")

        LOG_ENTRIES.append([index+1, lot_url, closing_time, current_time, "Updated", "Time changed"])

    except TimeoutException:
        print("   ⚠️ Timeout or page issue.")
        LOG_ENTRIES.append([index+1, lot_url, closing_time, "N/A", "Skipped", "Page timeout or missing"])
    except Exception as e:
        print(f"   ❗ Error: {e}")
        LOG_ENTRIES.append([index+1, lot_url, closing_time, "N/A", "Error", str(e)])

driver.quit()

# --- Save CSV log ---
df = pd.DataFrame(LOG_ENTRIES, columns=["Lot #", "Lot URL", "Expected Time", "Current Time", "Status", "Note"])
df.to_csv(CSV_LOG_PATH, index=False)
print(f"\n📄 Log saved to: {CSV_LOG_PATH}")
print("🏁 Done. All lots processed.")
