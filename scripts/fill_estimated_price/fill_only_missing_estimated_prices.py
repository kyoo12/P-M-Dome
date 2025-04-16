import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import Options
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# === CONFIG ===
AUCTION_ID = 1001
TOTAL_LOTS = 766
EXCEL_FILE = "Marton AG1420251621.xlsx"

# === Setup Chrome ===
options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# === Manual login step ===
driver.get(f"https://dome-auctions.com/administration/auctions/{AUCTION_ID}/?page=1")
input("🔐 Please log in to the site manually, then press ENTER to start...")

# === Build lot_number -> lot_id mapping ===
lot_map = {}
for page in range(1, 33):  # assume max 100 pages
    url = f"https://dome-auctions.com/administration/auctions/{AUCTION_ID}/?page={page}"
    driver.get(url)
 #   time.sleep(2)
    rows = driver.find_elements(By.CSS_SELECTOR, "a[href*='/lots/']")
    if not rows:
        break
    for row in rows:
        try:
            href = row.get_attribute("href")
            text = row.text.strip()
            if "/lots/" in href and text.isdigit():
                lot_number = int(text)
                lot_id = int(href.split("/lots/")[1].split("/")[0])
                lot_map[lot_number] = lot_id
        except Exception:
            continue

print(f"🔎 Found {len(lot_map)} lots.")

# === Load Excel and update missing Estimated Prices ===
df = pd.read_excel(EXCEL_FILE)

for _, row in df.iterrows():
    lot_number = int(row.iloc[0])
    estimated_price = row.iloc[1]
    if pd.isna(estimated_price):
        print(f"⏩ Lot {lot_number}: No estimated price in Excel, skipping.")
        continue
    lot_id = lot_map.get(lot_number)
    if not lot_id:
        print(f"❌ Lot {lot_number}: No matching lot_id found.")
        continue

    lot_url = f"https://dome-auctions.com/administration/auctions/{AUCTION_ID}/lots/{lot_id}/update/"
    driver.get(lot_url)
   # time.sleep(1.5)

    try:
        price_field = driver.find_element(By.ID, "id_estimated_price")
        current_value = price_field.get_attribute("value")
        if current_value.strip() != "" and current_value.strip() != "0":
            print(f"⏭️ Lot {lot_number} (id: {lot_id}): Already has estimated price: {current_value}")
            continue

        price_field.clear()
        price_field.send_keys(str(int(estimated_price)))
        save_btn = driver.find_element(By.NAME, "save_exit")
        save_btn.click()
        print(f"✅ Lot {lot_number} (id: {lot_id}) filled with €{estimated_price}")
      #  time.sleep(2.5)
    except NoSuchElementException:
        print(f"⚠️ Lot {lot_number}: Missing field or button, skipped.")

print("🎯 Finished checking and filling in missing prices.")
