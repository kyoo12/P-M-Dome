
# Dome Auctions Starting Bid Scraper

This script logs into the admin interface, visits each lot, and extracts the Lotnumber and Starting Bid into a CSV.

## ▶️ How to Use:

1. Install requirements:
```
pip install selenium pandas webdriver-manager
```

2. Run the script:
```
python scrape_starting_bids.py
```

3. Log in manually when prompted.
4. It will scrape all pages and save the output to `starting_bids_export.csv`.
