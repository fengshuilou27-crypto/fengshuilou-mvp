import requests
import os
import struct
import numpy as np
import rasterio
from rasterio.transform import from_bounds

# SRTM data from AWS Open Data (Mapzen / elevation-tiles-prod)
# Hong Kong spans two tiles: N22E113 and N22E114
# .hgt files are 3601x3601 16-bit signed integers, big-endian

tiles = [
    ("N22E113", 113.0, 22.0, 114.0, 23.0),  # west, south, east, north
    ("N22E114", 114.0, 22.0, 115.0, 23.0),
]

os.makedirs("data/dem", exist_ok=True)

# Download .hgt files
for tile_name, west, south, east, north in tiles:
    url = f"https://s3.amazonaws.com/elevation-tiles-prod/skadi/N22/{tile_name}.hgt"
    output_path = f"data/dem/{tile_name}.hgt"
    
    if os.path.exists(output_path) and os.path.getsize(output_path) == 3601 * 3601 * 2:
        print(f"{tile_name}.hgt already downloaded ({os.path.getsize(output_path)} bytes)")
        continue
    
    print(f"Downloading {tile_name} from {url}...")
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"  Saved: {len(response.content)} bytes")
        else:
            print(f"  ERROR: HTTP {response.status_code}")
    except Exception as e:
        print(f"  ERROR: {e}")

# Parse .hgt files and convert to GeoTIFF
hgt_files = []
for tile_name, west, south, east, north in tiles:
    hgt_path = f"data/dem/{tile_name}.hgt"
    if not os.path.exists(hgt_path):
        print(f"Missing {hgt_path}, skipping")
        continue
    
    file_size = os.path.getsize(hgt_path)
    expected_size = 3601 * 3601 * 2
    
    if file_size != expected_size:
        print(f"{tile_name}: unexpected size {file_size}, expected {expected_size}")
        continue
    
    with open(hgt_path, 'rb') as f:
        data = f.read()
    
    # Parse as 16-bit signed integers, big-endian
    elevations = np.array(struct.unpack('>' + 'h' * (3601 * 3601), data), dtype=np.int16)
    elevations = elevations.reshape((3601, 3601))
    
    # SRTM uses -32768 for voids, convert to NaN
    elevations = elevations.astype(np.float32)
    elevations[elevations == -32768] = np.nan
    
    # Create GeoTIFF for this tile
    tif_path = f"data/dem/{tile_name}.tif"
    transform = from_bounds(west, south, east, north, 3601, 3601)
    
    with rasterio.open(
        tif_path,
        'w',
        driver='GTiff',
        height=3601,
        width=3601,
        count=1,
        dtype=elevations.dtype,
        crs='EPSG:4326',
        transform=transform,
        compress='lzw',
    ) as dst:
        dst.write(elevations, 1)
    
    print(f"  Converted {tile_name} -> {tif_path}")
    hgt_files.append(tif_path)

if len(hgt_files) == 2:
    # Merge the two tiles and clip to Hong Kong bounds
    print("\nMerging tiles...")
    
    from rasterio.merge import merge
    from rasterio.mask import mask
    import shapely.geometry
    
    # Open both tiles
    src_files = [rasterio.open(f) for f in hgt_files]
    
    # Merge
    merged, merged_transform = merge(src_files)
    
    # Clip to Hong Kong approximate bounds
    hk_bounds = (113.80, 22.13, 114.45, 22.58)
    
    # Create a polygon for clipping
    geom = shapely.geometry.box(*hk_bounds)
    
    # Write merged full data first
    merged_path = "data/dem/hong_kong_srtm30m_raw.tif"
    with rasterio.open(
        merged_path,
        'w',
        driver='GTiff',
        height=merged.shape[1],
        width=merged.shape[2],
        count=1,
        dtype=merged.dtype,
        crs='EPSG:4326',
        transform=merged_transform,
        compress='lzw',
    ) as dst:
        dst.write(merged[0], 1)
    
    print(f"  Merged raw: {merged_path}")
    
    # Now clip to Hong Kong
    with rasterio.open(merged_path) as src:
        clipped, clipped_transform = mask(src, [shapely.mapping(geom)], crop=True)
    
    final_path = "data/dem/hong_kong_dem.tif"
    with rasterio.open(
        final_path,
        'w',
        driver='GTiff',
        height=clipped.shape[1],
        width=clipped.shape[2],
        count=1,
        dtype=clipped.dtype,
        crs='EPSG:4326',
        transform=clipped_transform,
        compress='lzw',
    ) as dst:
        dst.write(clipped[0], 1)
    
    print(f"  Final clipped: {final_path}")
    print(f"  Size: {os.path.getsize(final_path)} bytes")
    
    # Close sources
    for src in src_files:
        src.close()
    
    print("\nSUCCESS: DEM data ready!")
    
    # Print stats
    with rasterio.open(final_path) as src:
        data = src.read(1)
        valid = data[~np.isnan(data)]
        print(f"  Dimensions: {src.width} x {src.height}")
        print(f"  CRS: {src.crs}")
        print(f"  Bounds: {src.bounds}")
        print(f"  Resolution: {src.res}")
        print(f"  Valid pixels: {len(valid)}")
        print(f"  Elevation range: {valid.min():.1f}m - {valid.max():.1f}m")
        print(f"  Mean elevation: {valid.mean():.1f}m")
    
else:
    print(f"\nOnly {len(hgt_files)} tiles available, need 2 for merge")
