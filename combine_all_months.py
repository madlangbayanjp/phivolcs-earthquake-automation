#!/usr/bin/env python3
"""
Script to combine all PHIVOLCS earthquake datasets from January to August 2025
"""

import pandas as pd
import glob
import os
from datetime import datetime
import re

def clean_location(location):
    """Clean location data by removing extra whitespace and newlines"""
    if pd.isna(location):
        return ""
    cleaned = re.sub(r'\s+', ' ', str(location).strip())
    return cleaned

def parse_datetime(date_time_str):
    """Parse datetime string to standard format"""
    try:
        if pd.isna(date_time_str):
            return None
        
        date_time_str = str(date_time_str).strip()
        
        try:
            parsed = pd.to_datetime(date_time_str, format="%d %B %Y - %I:%M %p")
            return parsed
        except:
            try:
                parsed = pd.to_datetime(date_time_str)
                return parsed
            except:
                print(f"Warning: Could not parse datetime: {date_time_str}")
                return None
    except Exception as e:
        print(f"Error parsing datetime {date_time_str}: {e}")
        return None

def combine_all_months():
    """Combine all monthly datasets from January to August 2025"""
    
    print("🌋 PHIVOLCS Complete Dataset Combiner (Jan-Aug 2025)")
    print("=" * 60)
    
    # Define the files to combine (in chronological order)
    monthly_files = [
        "phivolcs_earthquakes_2025_01.csv",  # January
        "phivolcs_earthquakes_2025_02.csv",  # February
        "phivolcs_earthquakes_2025_03.csv",  # March
        "phivolcs_earthquakes_2025_04.csv",  # April
        "phivolcs_earthquakes_may.csv",      # May
        "phivolcs_earthquakes_june.csv",     # June
        "phivolcs_earthquakes_july.csv",     # July
        "phivolcs_earthquakes_aug.csv"       # August
    ]
    
    print("📁 Files to combine:")
    for file in monthly_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (not found)")
    
    # Read and combine all datasets
    all_data = []
    
    for file in monthly_files:
        if not os.path.exists(file):
            print(f"\n⚠️  Skipping {file} - file not found")
            continue
            
        try:
            print(f"\n📖 Reading {file}...")
            
            # Read CSV file with robust handling
            try:
                df = pd.read_csv(file)
            except Exception as e:
                print(f"  ⚠️  Standard CSV reading failed: {e}")
                df = pd.read_csv(file, encoding='utf-8', on_bad_lines='skip')
            
            # Clean the data
            df['Location'] = df['Location'].apply(clean_location)
            
            # Parse datetime
            df['Date-Time'] = df['Date-Time'].apply(parse_datetime)
            
            # Convert numeric columns with error handling
            df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
            df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
            df['Depth'] = pd.to_numeric(df['Depth'], errors='coerce')
            df['Magnitude'] = pd.to_numeric(df['Magnitude'], errors='coerce')
            
            # Remove rows with invalid coordinates
            initial_count = len(df)
            df = df.dropna(subset=['Latitude', 'Longitude', 'Magnitude'])
            removed_count = initial_count - len(df)
            
            if removed_count > 0:
                print(f"  ⚠️  Removed {removed_count} rows with invalid coordinates")
            
            # Add source file information
            df['Source_File'] = file
            
            all_data.append(df)
            print(f"  ✅ Added {len(df)} valid records from {file}")
            
        except Exception as e:
            print(f"  ❌ Error processing {file}: {e}")
    
    if not all_data:
        print("❌ No data could be loaded!")
        return
    
    # Combine all dataframes
    print(f"\n🔗 Combining {len(all_data)} datasets...")
    combined_df = pd.concat(all_data, ignore_index=True)
    
    print(f"📊 Total records before deduplication: {len(combined_df)}")
    
    # Remove duplicates based on key fields
    print("🧹 Removing duplicates...")
    initial_count = len(combined_df)
    
    # Remove exact duplicates
    combined_df = combined_df.drop_duplicates()
    
    # Remove duplicates based on Date-Time, Latitude, Longitude, and Magnitude
    combined_df = combined_df.drop_duplicates(
        subset=['Date-Time', 'Latitude', 'Longitude', 'Magnitude'],
        keep='first'
    )
    
    final_count = len(combined_df)
    duplicates_removed = initial_count - final_count
    
    print(f"  ✅ Removed {duplicates_removed} duplicate records")
    print(f"  📊 Final dataset has {final_count} unique records")
    
    # Sort by date-time
    combined_df = combined_df.sort_values('Date-Time', ascending=False)
    
    # Save combined dataset
    output_filename = f"phivolcs_earthquakes_complete_2025_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    combined_df.to_csv(output_filename, index=False)
    
    print(f"\n✅ Complete dataset saved to: {output_filename}")
    
    # Print summary statistics
    print(f"\n📈 Complete Dataset Summary:")
    print(f"  - Total unique records: {len(combined_df)}")
    print(f"  - Date range: {combined_df['Date-Time'].min()} to {combined_df['Date-Time'].max()}")
    print(f"  - Magnitude range: {combined_df['Magnitude'].min():.1f} to {combined_df['Magnitude'].max():.1f}")
    print(f"  - Depth range: {combined_df['Depth'].min():.0f} to {combined_df['Depth'].max():.0f} km")
    
    # Show records by source file
    print(f"\n📁 Records by source file:")
    source_counts = combined_df['Source_File'].value_counts()
    for source, count in source_counts.items():
        month_name = source.replace('phivolcs_earthquakes_', '').replace('.csv', '')
        print(f"  - {month_name}: {count} records")
    
    return combined_df

def analyze_complete_data(df):
    """Analyze the complete dataset"""
    print(f"\n🔍 Complete Data Analysis:")
    
    # Check for missing values
    missing_data = df.isnull().sum()
    if missing_data.sum() > 0:
        print(f"  ⚠️  Missing values:")
        for column, count in missing_data.items():
            if count > 0:
                print(f"    - {column}: {count} missing values")
    else:
        print(f"  ✅ No missing values found")
    
    # Show magnitude distribution
    print(f"\n🌋 Magnitude distribution:")
    magnitude_ranges = [
        (0, 1, "Micro (0-1)"),
        (1, 3, "Minor (1-3)"),
        (3, 5, "Light (3-5)"),
        (5, 7, "Moderate (5-7)"),
        (7, float('inf'), "Strong (7+)")
    ]
    
    for min_mag, max_mag, label in magnitude_ranges:
        if max_mag == float('inf'):
            count = len(df[df['Magnitude'] >= min_mag])
        else:
            count = len(df[(df['Magnitude'] >= min_mag) & (df['Magnitude'] < max_mag)])
        percentage = (count / len(df)) * 100
        print(f"  - {label}: {count} earthquakes ({percentage:.1f}%)")
    
    # Show monthly distribution
    print(f"\n📅 Monthly distribution:")
    df['Month'] = df['Date-Time'].dt.month
    monthly_counts = df['Month'].value_counts().sort_index()
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug']
    for month_num, count in monthly_counts.items():
        month_name = month_names[month_num - 1]
        print(f"  - {month_name}: {count} earthquakes")

if __name__ == "__main__":
    print("🌋 PHIVOLCS Complete Dataset Combiner")
    print("=" * 60)
    
    # Combine all monthly datasets
    combined_df = combine_all_months()
    
    if combined_df is not None:
        # Analyze the complete data
        analyze_complete_data(combined_df)
        
        print(f"\n🎉 Complete dataset combination successful!")
        print(f"📊 You now have comprehensive earthquake data from January to August 2025!")
    else:
        print(f"\n❌ Failed to combine datasets!") 