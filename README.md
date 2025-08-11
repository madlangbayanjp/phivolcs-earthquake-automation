# 🌋 PHIVOLCS Earthquake Data Automation

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automated%20Scraper-success?logo=githubactions)
![Tableau](https://img.shields.io/badge/Tableau-Live%20Dashboard-orange?logo=tableau)

This project automatically scrapes **earthquake data** from the [PHIVOLCS website](https://earthquake.phivolcs.dost.gov.ph/) **monthly**, stores it in monthly CSV files, and keeps the data ready for analysis in **Tableau**.

---

## 📌 Features
- 🔄 **Automated Scraping**: Runs monthly on the 1st of each month using GitHub Actions.
- 📅 **Monthly Data Organization**: Each month gets its own CSV file for clean data management.
- 📊 **Live Tableau Dashboard**: Visualizes latest earthquake trends.
- 🚀 **Portfolio-Ready**: Demonstrates skills in Python, automation, and data visualization.

---

## ⚙️ How It Works
1. **GitHub Actions** runs the Python scraper (`scrape_github_actions.py`) monthly on the 1st of each month.
2. Scraper checks the **PHIVOLCS "Latest Month"** page for new earthquakes.
3. New records are appended to the current month's CSV file.
4. At the start of each month, the scraper automatically creates a new CSV file for that month.
5. Tableau can be connected to any monthly CSV for **live updates**.

---

## 📁 Repository Structure
```
├── .github/workflows/
│   └── scrape_earthquakes.yml    # GitHub Actions automation
├── scrape_github_actions.py      # Main scraping script
├── requirements.txt               # Python dependencies
├── README.md                     # This file
├── .gitignore                    # Git ignore rules
└── phivolcs_earthquakes_2025_*.csv  # Monthly earthquake data files
```

## 📊 Current Data
- **January 2025**: `phivolcs_earthquakes_2025_01.csv`
- **February 2025**: `phivolcs_earthquakes_2025_02.csv`
- **March 2025**: `phivolcs_earthquakes_2025_03.csv`
- **April 2025**: `phivolcs_earthquakes_2025_04.csv`
- **May 2025**: `phivolcs_earthquakes_2025_05.csv`
- **June 2025**: `phivolcs_earthquakes_2025_06.csv`
- **July 2025**: `phivolcs_earthquakes_2025_07.csv`
- **August 2025**: `phivolcs_earthquakes_2025_08.csv`

## 🚀 Getting Started
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. The automation runs automatically via GitHub Actions monthly on the 1st of each month
4. Connect your Tableau dashboard to any monthly CSV file for live data

---

## 📈 Data Schema
Each CSV file contains earthquake records with columns:
- Date and Time
- Magnitude
- Depth
- Location
- Coordinates
- And other PHIVOLCS data fields
