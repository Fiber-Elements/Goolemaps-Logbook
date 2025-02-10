import json
import csv
from datetime import datetime
import math
import sys
import os
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

# Cache for location names
location_cache = {}

def get_location_name(lat, lon, geolocator):
    # Round coordinates to 4 decimal places for caching (roughly 11m precision)
    cache_key = (round(lat, 4), round(lon, 4))
    
    if cache_key in location_cache:
        return location_cache[cache_key]
    
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            location = geolocator.reverse(f"{lat}, {lon}", language='en')
            if location and location.raw.get('address'):
                address = location.raw['address']
                # Try to get the most relevant name (city, town, village, or suburb)
                for key in ['city', 'town', 'village', 'suburb', 'county']:
                    if key in address:
                        location_cache[cache_key] = address[key]
                        return address[key]
                location_cache[cache_key] = location.address.split(',')[0]
                return location_cache[cache_key]
            return f"{lat:.6f}, {lon:.6f}"
        except GeocoderTimedOut:
            if attempt == max_attempts - 1:
                return f"{lat:.6f}, {lon:.6f}"
            time.sleep(0.5)  # Reduced wait time
        except Exception as e:
            print(f"Error getting location name: {e}")
            return f"{lat:.6f}, {lon:.6f}"

def get_month_from_filename(filename):
    # Extract month from filename (e.g., "2024_JANUARY.json" -> 1)
    months = {
        'JANUARY': 1, 'FEBRUARY': 2, 'MARCH': 3, 'APRIL': 4,
        'MAY': 5, 'JUNE': 6, 'JULY': 7, 'AUGUST': 8,
        'SEPTEMBER': 9, 'OCTOBER': 10, 'NOVEMBER': 11, 'DECEMBER': 12
    }
    for month, num in months.items():
        if month in filename.upper():
            return num
    return 0

def process_json_file(filename, geolocator):
    trips = []
    month = get_month_from_filename(filename)
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            if 'timelineObjects' not in data:
                return []
                
            for item in data['timelineObjects']:
                if 'activitySegment' in item:
                    segment = item['activitySegment']
                    
                    if 'startLocation' in segment and 'endLocation' in segment:
                        start = segment['startLocation']
                        end = segment['endLocation']
                        
                        # Get coordinates
                        start_lat = start['latitudeE7'] / 1e7
                        start_lon = start['longitudeE7'] / 1e7
                        end_lat = end['latitudeE7'] / 1e7
                        end_lon = end['longitudeE7'] / 1e7
                        
                        # Calculate distance
                        distance = haversine_distance(start_lat, start_lon, end_lat, end_lon)
                        
                        # Get location names (with reduced delay)
                        start_place = get_location_name(start_lat, start_lon, geolocator)
                        time.sleep(0.2)  # Reduced delay
                        end_place = get_location_name(end_lat, end_lon, geolocator)
                        time.sleep(0.2)  # Reduced delay
                        
                        # Get timestamps
                        start_time = segment.get('duration', {}).get('startTimestamp', '')
                        end_time = segment.get('duration', {}).get('endTimestamp', '')
                        
                        trips.append({
                            'month': month,
                            'from': start_place,
                            'to': end_place,
                            'distance_km': round(distance, 2),
                            'start_time': start_time,
                            'end_time': end_time
                        })
                        
                        print(f"Processed trip: {start_place} → {end_place}")
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")
    
    return trips

def main():
    # Initialize geolocator
    geolocator = Nominatim(user_agent="travel_logbook_generator")
    
    # Get all JSON files and sort them by month
    json_files = [f for f in os.listdir('.') if f.endswith('.json')]
    json_files.sort(key=get_month_from_filename)
    
    # Prepare CSV output
    with open('travel_logbook.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['month', 'from', 'to', 'distance_km', 'start_time', 'end_time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Process each JSON file
        for json_file in json_files:
            print(f"\nProcessing {json_file}...")
            trips = process_json_file(json_file, geolocator)
            for trip in trips:
                writer.writerow(trip)

if __name__ == "__main__":
    main()
    print("\nDone! Check travel_logbook.csv for results.")
