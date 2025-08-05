#!/usr/bin/env python3
"""
PHIVOLCS Earthquake Scraper for GitHub Actions
Optimized for automated scraping every 10 minutes
"""

import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import os
import re
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === Config ===
OUTPUT_FILE = "phivolcs_earthquakes_master.csv"
LATEST_URL = "https://earthquake.phivolcs.dost.gov.ph/"
LOG_FILE = "scrape_log.txt"

def log_message(message):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    
    # Also write to log file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

def clean_location(location):
    """Clean location text"""
    if not location:
        return ""
    return re.sub(r'\s+', ' ', str(location).strip())

def load_existing_records():
    """Load all existing Date-Time entries to avoid duplicates"""
    if not os.path.exists(OUTPUT_FILE):
        log_message("No existing file found, starting fresh")
        return set()
    
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            existing_records = {row["Date-Time"] for row in reader}
        log_message(f"Loaded {len(existing_records)} existing records")
        return existing_records
    except Exception as e:
        log_message(f"Error loading existing records: {e}")
        return set()

def scrape_latest_month():
    """Scrape earthquake data from Latest Month page"""
    log_message(f"🌍 Scraping latest month from: {LATEST_URL}")
    
    try:
        response = requests.get(LATEST_URL, timeout=15, verify=False)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find earthquake table
        tables = soup.find_all("table")
        
        earthquake_table = None
        for table in tables:
            table_text = table.get_text().lower()
            if any(keyword in table_text for keyword in ['magnitude', 'depth', 'latitude', 'longitude', 'location']):
                earthquake_table = table
                break
        
        if not earthquake_table:
            log_message("⚠️ No earthquake table found on latest month page.")
            return []

        rows = earthquake_table.find_all("tr")[1:]  # Skip header
        data = []
        
        for row in rows:
            cols = [col.text.strip() for col in row.find_all("td")]
            if len(cols) >= 6:
                cols[5] = clean_location(cols[5])  # Clean location
                data.append(cols[:6])

        log_message(f"✅ Found {len(data)} records on Latest page")
        return data

    except requests.exceptions.RequestException as e:
        log_message(f"❌ Network error scraping latest month: {e}")
        return []
    except Exception as e:
        log_message(f"❌ Error scraping latest month: {e}")
        return []

def append_new_data(latest_data, existing_records):
    """Append only new earthquake events to CSV"""
    new_rows = [row for row in latest_data if row[0] not in existing_records]

    if not new_rows:
        log_message("ℹ️ No new earthquakes found.")
        return 0

    # Determine file mode and headers
    file_exists = os.path.exists(OUTPUT_FILE)
    mode = "a" if file_exists else "w"
    
    try:
        with open(OUTPUT_FILE, mode, newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Date-Time", "Latitude", "Longitude", "Depth", "Magnitude", "Location"])
            writer.writerows(new_rows)

        log_message(f"💾 Added {len(new_rows)} new earthquake records.")
        return len(new_rows)
        
    except Exception as e:
        log_message(f"❌ Error writing to CSV: {e}")
        return 0

def get_file_stats():
    """Get statistics about the current data file"""
    if not os.path.exists(OUTPUT_FILE):
        return "File does not exist"
    
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        if not rows:
            return "File is empty"
            
        # Get date range
        dates = [row["Date-Time"] for row in rows]
        return f"Total records: {len(rows)}, Date range: {min(dates)} to {max(dates)}"
        
    except Exception as e:
        return f"Error reading file: {e}"

def main():
    """Main scraping function"""
    log_message("🌋 PHIVOLCS Incremental Scraper Started")
    log_message("=" * 50)
    
    # Load existing records
    existing_records = load_existing_records()
    
    # Scrape latest data
    latest_data = scrape_latest_month()
    
    if not latest_data:
        log_message("❌ No data scraped, exiting")
        return
    
    # Append new data
    new_count = append_new_data(latest_data, existing_records)
    
    # Log final statistics
    stats = get_file_stats()
    log_message(f"📊 Final stats: {stats}")
    
    if new_count > 0:
        log_message(f"🎉 Successfully added {new_count} new records!")
    else:
        log_message("ℹ️ No new records added")
    
    log_message("🏁 Scraping run complete!")

if __name__ == "__main__":
    main() 