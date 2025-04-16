
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# --- Load Excel data ---
excel_path = "Marton AG1420251052.xlsx"
df = pd.read_excel(excel_path)
df["Lotnumber"] = df["Lotnumber"].astype(str)

lot_to_data = {
    row["Lotnumber"]: {
        "Title": str(row["Title"]).strip(),
        "Description": str(row["Description"]).strip(),
        "StartingBid": str(row["StartingBid"]).strip(),
    }
    for _, row in df.iterrows()
}

# --- Set up Selenium ---
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# --- Manual login ---
driver.get("https://dome-auctions.com/administration/auctions/1001/?page=1")
input("🔐 Please log in manually, then press ENTER to start automation...")

# --- Start crawling all pages ---
discrepancies = []
lot_links_visited = set()
page = 1

while True:
    print(f"🌐 Scanning page {page}...")
    driver.get(f"https://dome-auctions.com/administration/auctions/1001/?page={page}")
    time.sleep(2)

    # Get all clickable lot links on the current page
    lot_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/lots/') and contains(@href, '/update/')]")
    current_page_links = []

    for link in lot_links:
        href = link.get_attribute("href")
        if href and href not in lot_links_visited:
            lot_links_visited.add(href)
            current_page_links.append(href)

    if not current_page_links:
        print("✅ No more lots found. Finished scanning.")
        break

    for lot_url in current_page_links:
        driver.get(lot_url)
     #   time.sleep(1.5)

        try:
            lot_number = driver.find_element(By.ID, "id_number").get_attribute("value").strip()
            if lot_number not in lot_to_data:
                print(f"⚠️ Lot {lot_number} not in Excel, skipping...")
                continue

            expected = lot_to_data[lot_number]

            title = driver.find_element(By.ID, "id_title_en").get_attribute("value").strip()
            desc = driver.find_element(By.ID, "id_description_en").get_attribute("value").strip()
            bid = driver.find_element(By.ID, "id_starting_bid").get_attribute("value").strip()

            if title != expected["Title"]:
                discrepancies.append({
                    "Lotnumber": lot_number,
                    "Field": "Title",
                    "Expected": expected["Title"],
                    "Found": title
                })
            if desc != expected["Description"]:
                discrepancies.append({
                    "Lotnumber": lot_number,
                    "Field": "Description",
                    "Expected": expected["Description"],
                    "Found": desc
                })
            if bid != expected["StartingBid"]:
                discrepancies.append({
                    "Lotnumber": lot_number,
                    "Field": "StartingBid",
                    "Expected": expected["StartingBid"],
                    "Found": bid
                })

            print(f"✅ Checked Lot {lot_number}")

        except NoSuchElementException:
            print(f"⚠️ Lot URL {lot_url}: one or more elements not found")
            discrepancies.append({
                "Lotnumber": "UNKNOWN",
                "Field": "ERROR",
                "Expected": "N/A",
                "Found": f"Element missing at {lot_url}"
            })

    page += 1

# --- Save results ---
if discrepancies:
    result_df = pd.DataFrame(discrepancies)
    result_df.to_csv("title_description_bid_discrepancies.csv", index=False)
    print("🚨 Discrepancies saved to 'title_description_bid_discrepancies.csv'")
else:
    print("🎉 All fields matched!")

driver.quit()
