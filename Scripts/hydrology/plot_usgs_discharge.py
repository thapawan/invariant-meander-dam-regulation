import pandas as pd
import matplotlib.pyplot as plt
import dataretrieval.nwis as nwis

# -----------------------------
# USGS gauge IDs
# -----------------------------
gauges = {
    "Black Warrior (Regulated)": "02466031",  # Selden L&D tailwater
    "Cahaba (Unregulated)": "02425000"        # Centreville
}

# Study period
start_date = "2000-01-01"
end_date = "2024-12-31"

fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

for ax, (label, site) in zip(axes, gauges.items()):
    df = nwis.get_record(
        sites=site,
        service="dv",
        start=start_date,
        end=end_date,
        parameterCd="00060"  # discharge (cfs)
    )

    df = df.reset_index()
    df["datetime"] = pd.to_datetime(df["datetime"])

    ax.plot(df["datetime"], df["00060_Mean"], linewidth=0.4)
    ax.set_yscale("log")
    ax.set_ylabel("Discharge (cfs)")
    ax.set_title(label)

axes[-1].set_xlabel("Year")

plt.tight_layout()
plt.savefig("daily_discharge_timeseries.png", dpi=300)
plt.show()
