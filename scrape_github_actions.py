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
# We now write per-month CSV files, e.g., phivolcs_earthquakes_2025_08.csv
# to avoid a single ever-growing master file.
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

def load_existing_records_for_file(csv_path: str) -> set:
    """Load existing Date-Time entries for a specific CSV file to avoid duplicates"""
    if not os.path.exists(csv_path):
        log_message(f"No existing file found for {csv_path}, starting fresh")
        return set()

    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            existing_records = {row["Date-Time"] for row in reader}
        log_message(f"Loaded {len(existing_records)} existing records from {os.path.basename(csv_path)}")
        return existing_records
    except Exception as e:
        log_message(f"Error loading existing records from {csv_path}: {e}")
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

def month_filename_from_datetime_str(dt_str: str) -> str:
    """Return the monthly CSV filename for a given Date-Time string.

    Supports multiple formats observed on PHIVOLCS pages, including:
    - YYYY-MM-DD HH:MM:SS
    - YYYY-MM-DD HH:MM
    - DD Month YYYY - HH:MM AM/PM  (e.g., '11 August 2025 - 12:07 PM')
    - DD Mon YYYY - HH:MM AM/PM    (e.g., '11 Aug 2025 - 12:07 PM')
    - a few common ISO-like variations
    """

    s = str(dt_str).replace("\u00A0", " ")  # NBSP -> space
    s = re.sub(r"\s+", " ", s.strip())
    # Normalize different dash characters
    s = s.replace("–", "-").replace("—", "-")
    # Trim after AM/PM (some pages append timezone, e.g., 'AM PST')
    m = re.match(r"^(.*?\b(?:AM|PM)\b)", s, flags=re.IGNORECASE)
    if m:
        s = m.group(1)
    # Normalize am/pm casing
    s = re.sub(r"\b(am|pm)\b", lambda m: m.group(1).upper(), s, flags=re.IGNORECASE)

    candidates = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d %B %Y - %I:%M %p",
        "%d %b %Y - %I:%M %p",
        "%d %B %Y %I:%M %p",
        "%d %b %Y %I:%M %p",
        "%d %B %Y, %I:%M %p",
        "%d %b %Y, %I:%M %p",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
    ]

    dt = None
    for fmt in candidates:
        try:
            dt = datetime.strptime(s, fmt)
            break
        except ValueError:
            continue

    if dt is None:
        # Last-resort cleaning for ISO-like strings
        try:
            dt = datetime.fromisoformat(s.replace("/", "-").replace("T", " "))
        except Exception as e:
            raise ValueError(f"Unrecognized date format for '{dt_str}'") from e

    return f"phivolcs_earthquakes_{dt.year}_{dt.month:02d}.csv"

def append_new_data_partitioned(latest_data) -> int:
    """Append only new events, partitioned by month file. Returns total records added."""
    # Group rows by target month file
    rows_by_file = {}
    for row in latest_data:
        if not row or len(row) < 1:
            continue
        dt_str = row[0]
        target_file = month_filename_from_datetime_str(dt_str)
        rows_by_file.setdefault(target_file, []).append(row)

    total_added = 0

    for csv_path, rows in rows_by_file.items():
        existing = load_existing_records_for_file(csv_path)
        new_rows = [r for r in rows if r[0] not in existing]

        if not new_rows:
            log_message(f"ℹ️ No new earthquakes for {os.path.basename(csv_path)}.")
            continue

        file_exists = os.path.exists(csv_path)
        mode = "a" if file_exists else "w"
        try:
            with open(csv_path, mode, newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Date-Time", "Latitude", "Longitude", "Depth", "Magnitude", "Location"])
                writer.writerows(new_rows)
            log_message(f"💾 Added {len(new_rows)} records to {os.path.basename(csv_path)}")
            total_added += len(new_rows)
        except Exception as e:
            log_message(f"❌ Error writing to {csv_path}: {e}")

    return total_added

def get_current_month_stats():
    """Get statistics about the current month's CSV file."""
    month_file = month_filename_from_datetime_str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    if not os.path.exists(month_file):
        return f"No file yet for current month ({month_file})"

    try:
        with open(month_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if not rows:
            return f"{month_file}: empty file"

        dates = [row["Date-Time"] for row in rows]
        return f"{month_file}: total {len(rows)} records, range {min(dates)} to {max(dates)}"
    except Exception as e:
        return f"Error reading {month_file}: {e}"

def main():
    """Main scraping function"""
    log_message("🌋 PHIVOLCS Incremental Scraper Started")
    log_message("=" * 50)
    
    # Scrape latest data
    latest_data = scrape_latest_month()
    
    if not latest_data:
        log_message("❌ No data scraped, exiting")
        return
    
    # Append new data to monthly files
    new_count = append_new_data_partitioned(latest_data)
    
    # Log final statistics
    stats = get_current_month_stats()
    log_message(f"📊 Final stats: {stats}")
    
    if new_count > 0:
        log_message(f"🎉 Successfully added {new_count} new records!")
    else:
        log_message("ℹ️ No new records added")
    
    log_message("🏁 Scraping run complete!")

if __name__ == "__main__":
    main() 