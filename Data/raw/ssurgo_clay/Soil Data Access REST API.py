import requests
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import box

def get_ssurgo_clay(bbox, area_name):
    """
    Query SSURGO clay content from SDA REST API
    
    Parameters:
    -----------
    bbox : tuple
        (min_x, min_y, max_x, max_y) in WGS84
    area_name : str
        Name of the study area
    """
    
    # SDA REST endpoint
    url = "https://sdmdataaccess.sc.egov.usda.gov/tabular/post.rest"
    
    # SQL query
    query = f"""
    SELECT 
        mu.mukey,
        mu.musym,
        mu.muname,
        co.compname,
        co.comppct_r,
        ch.hzdept_r,
        ch.claytotal_r
    FROM legend AS leg
    INNER JOIN mapunit AS mu ON mu.lkey = leg.lkey
    INNER JOIN component AS co ON co.mukey = mu.mukey
    LEFT JOIN chorizon AS ch ON ch.cokey = co.cokey
    WHERE leg.areasymbol IN ('AL003', 'AL097')  -- Baldwin and Mobile Counties
        AND co.majcompflag = 'Yes'
        AND ch.hzdept_r = 0  -- Surface horizon only
        AND ch.claytotal_r IS NOT NULL
    ORDER BY mu.mukey, co.comppct_r DESC
    """
    
    # Make request
    response = requests.post(
        url,
        data={"query": query, "format": "json"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data.get("Table", []))
        return df
    else:
        print(f"Error: {response.status_code}")
        return None

# Define bounding boxes for your reaches (approximate)
# Replace with your actual reach polygons
black_warrior_bbox = (-87.8, 32.5, -87.5, 33.0)
cahaba_bbox = (-87.1, 32.8, -86.8, 33.2)

# Query data
bw_clay_df = get_ssurgo_clay(black_warrior_bbox, "Black Warrior River")
cahaba_clay_df = get_ssurgo_clay(cahaba_bbox, "Cahaba River")

# Summarize
if bw_clay_df is not None:
    print("\n=== Black Warrior River Clay Content ===")
    print(bw_clay_df.groupby('compname')['claytotal_r'].describe())
