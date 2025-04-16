
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# --- Set up Selenium ---
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# --- Manual login ---
driver.get("https://dome-auctions.com/administration/auctions/1001/?page=1")
input("🔐 Please log in manually, then press ENTER to start scraping...")

# --- Start scraping ---
results = []
visited = set()
page = 1

while True:
    print(f"🌍 Scanning page {page}...")
    driver.get(f"https://dome-auctions.com/administration/auctions/1001/?page={page}")
    time.sleep(2)

    links = driver.find_elements(By.XPATH, "//a[contains(@href, '/lots/') and contains(@href, '/update/')]")
    urls = []

    for link in links:
        href = link.get_attribute("href")
        if href and href not in visited:
            visited.add(href)
            urls.append(href)

    if not urls:
        print("✅ No more lots found.")
        break

    for url in urls:
        driver.get(url)
      #  time.sleep(1.2)

        try:
            lot_number = driver.find_element(By.ID, "id_number").get_attribute("value").strip()
            starting_bid = driver.find_element(By.ID, "id_starting_bid").get_attribute("value").strip()
            results.append({"Lotnumber": lot_number, "StartingBid": starting_bid})
            print(f"📦 Lot {lot_number}: {starting_bid}")

        except NoSuchElementException:
            print(f"⚠️ Elements not found at {url}")

    page += 1

# --- Save output ---
df = pd.DataFrame(results)
df.to_csv("starting_bids_export.csv", index=False)
print("📄 Export complete: starting_bids_export.csv")

driver.quit()
