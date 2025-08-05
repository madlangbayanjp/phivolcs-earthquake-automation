# 🌋 PHIVOLCS Earthquake Data Automation

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automated%20Scraper-success?logo=githubactions)
![Tableau](https://img.shields.io/badge/Tableau-Live%20Dashboard-orange?logo=tableau)

This project automatically scrapes **real-time earthquake data** from the [PHIVOLCS website](https://earthquake.phivolcs.dost.gov.ph/) every **10 minutes**, stores it in a CSV file, and keeps the data ready for analysis in **Tableau**.

---

## 📌 Features
- 🔄 **Automated Scraping**: Runs every 10 minutes using GitHub Actions.
- 🗂 **Clean Historical Dataset**: Combines past months (January–July 2025) with new real-time data.
- 📊 **Live Tableau Dashboard**: Visualizes latest earthquake trends.
- 🚀 **Portfolio-Ready**: Demonstrates skills in Python, automation, and data visualization.

---

## ⚙️ How It Works
1. **GitHub Actions** runs the Python scraper (`scrape_github_actions.py`) every 10 minutes.
2. Scraper checks the **PHIVOLCS "Latest Month"** page for new earthquakes.
3. New records are appended to `phivolcs_earthquakes_master.csv`.
4. Tableau is connected to the CSV (or Google Sheets) for **live updates**.

---
