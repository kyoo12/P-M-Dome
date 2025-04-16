Dome Auctions Automation Scripts 🏗️💻
This repository contains a collection of Python scripts developed for Dome Auctions B.V. to streamline and automate daily operational tasks. Each folder contains a modular script designed to work independently or in sequence with others to assist with auction setup, data cleanup, and timing logic for lot closings.

📁 Folder Overview
Auction1003_ClosingScript
Smart closing time assignment for Auction ID 1003.
Automatically assigns randomized closing times to lots based on predefined rules (e.g., subcategory, price, combination lots). Supports dry run mode for testing.

dome_lot_checker_v2
Validates lot data for completeness and consistency.
Flags missing or suspicious information like empty titles, missing categories, or prices.

dome_lot_time_updater
Updates or rewrites the closing times of lots.
Useful for applying manual overrides or syncing closing times with new auction strategies.

dome_scraper_starting_bid
Scrapes and fills in starting bid data from internal or external sources.
Reduces manual input during auction setup.

dome_subcat_checker
Cross-checks lot descriptions and titles with subcategories.
Detects miscategorized items and suggests corrections.

fill_estimated_price
Populates missing estimated price fields using heuristics or scraped data.
Improves auction transparency and ensures all lots have proper valuations.

SmartClosingScript
General version of the smart closing time logic.
Assigns randomized time slots to lots based on rules (time ranges, value thresholds, etc.).

SmartClosingScript_Updated
Updated version with bug fixes or new logic (e.g., combination lots, stricter rules).
More dynamic and rule-based than the original SmartClosingScript.
