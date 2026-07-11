import requests
import time

# Hong Kong bounding box (approximate)
# West: 113.833, East: 114.406, South: 22.153, North: 22.563
# Using slightly larger box to ensure coverage
bbox = {
    "west": 113.80,
    "east": 114.45,
    "south": 22.13,
    "north": 22.58
}

# Try SRTM GL1 (30m) first
dem_types = ["SRTMGL1", "COP30"]
output_file = "data/dem/hong_kong_dem.tif"

for dem_type in dem_types:
    print(f"\nTrying to download {dem_type}...")
    
    url = "https://portal.opentopography.org/API/globaldem"
    params = {
        "demtype": dem_type,
        "west": bbox["west"],
        "east": bbox["east"],
        "south": bbox["south"],
        "north": bbox["north"],
        "outputFormat": "GTiff",
        "API_Key": "demo"  # Try demo key
    }
    
    try:
        response = requests.get(url, params=params, timeout=120)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
        print(f"Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            # Check if it's actually a TIFF or an error message
            content_type = response.headers.get('Content-Type', '')
            if 'tiff' in content_type.lower() or 'geotiff' in content_type.lower():
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                print(f"SUCCESS: Saved to {output_file}")
                break
            else:
                # Might be an error message
                print(f"Response (first 500 chars): {response.text[:500]}")
        else:
            print(f"Error response: {response.text[:500]}")
            
    except Exception as e:
        print(f"Exception: {e}")
    
    time.sleep(2)  # Be polite

print("\nDone.")
