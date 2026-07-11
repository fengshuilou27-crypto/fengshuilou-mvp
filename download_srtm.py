import requests
import gzip
import os
import struct
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from rasterio.merge import merge
import shapely.geometry

os.makedirs("data/dem", exist_ok=True)

# SRTM tiles needed for Hong Kong
tiles = [
    ("N22E113", 113.0, 22.0, 114.0, 23.0),  # west, south, east, north
    ("N22E114", 114.0, 22.0, 115.0, 23.0),
]

tif_files = []

for tile_name, west, south, east, north in tiles:
    url = f"https://s3.amazonaws.com/elevation-tiles-prod/skadi/N22/{tile_name}.hgt.gz"
    gz_path = f"data/dem/{tile_name}.hgt.gz"
    hgt_path = f"data/dem/{tile_name}.hgt"
    tif_path = f"data/dem/{tile_name}.tif"
    
    # Download
    if not os.path.exists(gz_path):
        print(f"Downloading {tile_name}...")
        try:
            response = requests.get(url, timeout=120)
            response.raise_for_status()
            with open(gz_path, 'wb') as f:
                f.write(response.content)
            print(f"  Downloaded: {len(response.content)} bytes")
        except Exception as e:
            print(f"  ERROR downloading: {e}")
            continue
    else:
        print(f"{tile_name}.hgt.gz already exists ({os.path.getsize(gz_path)} bytes)")
    
    # Decompress
    if not os.path.exists(hgt_path):
        print(f"  Decompressing...")
        with gzip.open(gz_path, 'rb') as f_in:
            with open(hgt_path, 'wb') as f_out:
                f_out.write(f_in.read())
        print(f"  Decompressed: {os.path.getsize(hgt_path)} bytes")
    
    # Parse .hgt file (3601x3601, 16-bit signed big-endian)
    expected_size = 3601 * 3601 * 2
    actual_size = os.path.getsize(hgt_path)
    if actual_size != expected_size:
        print(f"  WARNING: size mismatch {actual_size} vs {expected_size}")
        continue
    
    with open(hgt_path, 'rb') as f:
        raw = f.read()
    
    elevations = np.array(struct.unpack('>' + 'h' * (3601 * 3601), raw), dtype=np.int16)
    elevations = elevations.reshape((3601, 3601))
    
    # Convert void values (-32768) to NaN
    elevations = elevations.astype(np.float32)
    elevations[elevations == -32768] = np.nan
    
    # Write GeoTIFF
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
        nodata=np.nan,
    ) as dst:
        dst.write(elevations, 1)
    
    print(f"  Converted to GeoTIFF: {tif_path}")
    tif_files.append(tif_path)

# Merge and clip to Hong Kong
if len(tif_files) == 2:
    print("\nMerging tiles...")
    src_files = [rasterio.open(f) for f in tif_files]
    merged, merged_transform = merge(src_files)
    
    # Save merged (full two tiles)
    merged_path = "data/dem/hong_kong_srtm30m_merged.tif"
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
        nodata=np.nan,
    ) as dst:
        dst.write(merged[0], 1)
    
    print(f"  Merged: {merged_path}")
    
    # Clip to Hong Kong approximate bounds
    hk_bounds = (113.80, 22.13, 114.45, 22.58)
    geom = shapely.geometry.box(*hk_bounds)
    
    from rasterio.mask import mask
    from shapely.geometry import mapping
    with rasterio.open(merged_path) as src:
        clipped, clipped_transform = mask(src, [mapping(geom)], crop=True)
    
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
        nodata=np.nan,
    ) as dst:
        dst.write(clipped[0], 1)
    
    print(f"  Clipped: {final_path}")
    
    for src in src_files:
        src.close()
    
    # Print stats
    print("\n=== DEM Statistics ===")
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
        print(f"  Median elevation: {np.median(valid):.1f}m")
    
    print(f"\nFile size: {os.path.getsize(final_path) / 1024 / 1024:.2f} MB")
    print("SUCCESS!")
else:
    print(f"Only {len(tif_files)} tiles, expected 2")
