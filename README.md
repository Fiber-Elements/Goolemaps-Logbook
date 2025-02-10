# Google Maps Timeline to Travel Logbook

This script processes Google Maps Timeline JSON files and creates a chronological travel logbook in CSV format. It converts GPS coordinates to readable city/location names and calculates distances between points.

## Features

- Processes multiple JSON files (one per month)
- Converts coordinates to readable location names using reverse geocoding
- Calculates travel distances using the haversine formula
- Orders trips chronologically by month
- Caches location lookups for better performance
- Outputs a CSV file with: month, from location, to location, distance, start time, and end time

## Setup

1. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your Google Maps Timeline JSON files in the same directory as the script
   - Files should be named like: `2024_JANUARY.json`, `2024_FEBRUARY.json`, etc.

2. Run the script:
```bash
python process_timeline.py
```

3. The script will create `travel_logbook.csv` with all your trips organized by month

## Output Format

The generated CSV file contains the following columns:
- month: Numeric month (1-12)
- from: Starting location name
- to: Destination location name
- distance_km: Distance traveled in kilometers
- start_time: Trip start timestamp
- end_time: Trip end timestamp

## Notes

- The script uses OpenStreetMap's Nominatim service for reverse geocoding
- Location names are cached to improve performance and reduce API calls
- If a location name cannot be found, coordinates will be used as fallback
