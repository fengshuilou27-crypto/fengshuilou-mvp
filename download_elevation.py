import elevation
import os

# Hong Kong bounding box
# West, South, East, North
bounds = (113.80, 22.13, 114.45, 22.58)
output_file = "data/dem/hong_kong_srtm30m.tif"

# Ensure directory exists
os.makedirs("data/dem", exist_ok=True)

print("Downloading SRTM 30m data for Hong Kong...")
print(f"Bounds: {bounds}")
print(f"Output: {output_file}")

try:
    elevation.clip(
        bounds=bounds,
        output=output_file,
        product='SRTM1'  # SRTM 1 arc-second (~30m)
    )
    print(f"SUCCESS: Downloaded to {output_file}")
    print(f"File size: {os.path.getsize(output_file)} bytes")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
