
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select #, Input


# --- Load Excel data ---
excel_path = "Marton AG_Final -2 (1).xlsx"
df = pd.read_excel(excel_path)
df["Lotnumber"] = df["Lotnumber"].astype(str)
lot_to_subcat = dict(zip(df["Lotnumber"], df["Subcatgory"].astype(str).str.strip()))

# --- Set up Selenium ---
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# --- Manual login ---
driver.get("https://dome-auctions.com/administration/auctions/1001/?page=1")
input("🔐 Please log in manually, then press ENTER to start automation...")

# --- Prepare for logging mismatches ---
discrepancies = []
lot_links_visited = set()
page = 1

while True:
    print(f"🌐 Scanning page {page}...")
    driver.get(f"https://dome-auctions.com/administration/auctions/1001/?page={page}")
    time.sleep(2)

    # Get all clickable lot links on the current page
    lot_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/update/')]")
    current_page_links = []

    for link in lot_links:
        href = link.get_attribute("href")
        if href and "/lots/" in href and "/update/" in href and href not in lot_links_visited:
            lot_links_visited.add(href)
            current_page_links.append(href)

    if not current_page_links:
        print("✅ No more lots found. Finished scanning.")
        break

    for lot_url in current_page_links:
        try:
            lot_id = lot_url.split("/lots/")[1].split("/")[0]
        except IndexError:
            continue

        driver.get(lot_url)
        # time.sleep(1.5)
# #id_subcategory
# document.querySelector("#id_subcategory")
# //*[@id="id_subcategory"]
# /html/body/div[1]/div/div/main/form/div[1]/div[1]/div[1]/input
        try:
            input_elem = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/main/form/div[1]/div[1]/div[1]/input")
            lot_id = input_elem.get_attribute("value")  # Input(input_elem).value
            print(f"input_val: {lot_id}")
            
            # subcat_elem = driver.find_element(By.XPATH, "//label[contains(text(), 'Subcategory')]/following-sibling::div")
            subcat_elem = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/main/form/div[1]/div[2]/div[3]/select")
            select = Select(subcat_elem)
            # dropdown_value = select.first_selected_option.get_attribute('option')
            # dropdown_value = subcat_elem.get_attribute("label")
            # dropdown_value = subcat_elem.get_attribute("option")
            dropdown_value = select.first_selected_option.text

            actual_subcat = dropdown_value
            # actual_subcat = subcat_elem.text.strip()
            print(f"actual_subcat: {actual_subcat}")

            expected_subcat = lot_to_subcat.get(lot_id)
            print(f"expected_subcat: {expected_subcat}")

            if expected_subcat is None:
                print(f"⚠️ Lot {lot_id} not found in Excel.")
                continue

            if actual_subcat != expected_subcat:
                print(f"❌ Lot {lot_id}: expected '{expected_subcat}', found '{actual_subcat}'")
                discrepancies.append({
                    "Lotnumber": lot_id,
                    "Expected Subcategory": expected_subcat,
                    "Found Subcategory": actual_subcat
                })
            else:
                print(f"✅ Lot {lot_id}: subcategory matches")

        except NoSuchElementException:
            print(f"⚠️ Lot {lot_id}: Subcategory element not found")
            discrepancies.append({
                "Lotnumber": lot_id,
                "Expected Subcategory": lot_to_subcat.get(lot_id, "Unknown"),
                "Found Subcategory": "Not found"
            })

    page += 1

# --- Save results ---
if discrepancies:
    result_df = pd.DataFrame(discrepancies)
    result_df.to_csv("subcategory_discrepancies.csv", index=False)
    print("🚨 Discrepancies saved to 'subcategory_discrepancies.csv'")
else:
    print("🎉 All subcategories matched!")

driver.quit()
