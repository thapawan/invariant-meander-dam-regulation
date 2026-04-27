import pandas as pd
import dataretrieval.nwis as nwis

site = "02466031"  # change to 02425000 for Cahaba

df = nwis.get_record(
    sites=site,
    service="dv",
    start="2000-01-01",
    end="2024-12-31",
    parameterCd="00060"
)

df = df.reset_index()
df["year"] = df["datetime"].dt.year

qcv = df["00060_Mean"].std() / df["00060_Mean"].mean()
print(f"Qcv = {qcv:.2f}")
