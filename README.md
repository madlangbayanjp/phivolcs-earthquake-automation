# PHIVOLCS Earthquake Data Automation

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automated%20Scraper-success?logo=githubactions)

This project automatically scrapes **earthquake data** from the [PHIVOLCS website](https://earthquake.phivolcs.dost.gov.ph/) **monthly**, stores it in monthly CSV files, and keeps the data ready for analysis

---

## Features
- **Automated Scraping**: Runs monthly on the 1st of each month using GitHub Actions.
- **Monthly Data Organization**: Each month gets its own CSV file for clean data management.
---

## ⚙ How It Works
1. **GitHub Actions** runs the Python scraper monthly on the 1st of each month.
2. Scraper checks the **PHIVOLCS "Latest Month"** page for new earthquakes.
3. New records are appended to the current month's CSV file.
4. At the start of each month, the scraper automatically creates a new CSV file for that month.
