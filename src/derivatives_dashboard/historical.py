"""Public FRED oil/gas SPOT reference prices, not forwards or TTF prices."""
from io import StringIO
import pandas as pd
import requests

SERIES={"oil_wti_spot_usd_bbl":"DCOILWTICO", "us_henry_hub_spot_usd_mmbtu":"DHHNGSP"}

def fetch_spot_reference(which="oil_wti_spot_usd_bbl",start="2022-01-01"):
    if which not in SERIES: raise ValueError("Unsupported reference")
    sid=SERIES[which]
    r=requests.get("https://fred.stlouisfed.org/graph/fredgraph.csv",params={"id":sid,"cosd":start},timeout=30)
    r.raise_for_status()
    data=pd.read_csv(StringIO(r.text))
    date_col="observation_date" if "observation_date" in data else "DATE"
    if date_col not in data or sid not in data: raise ValueError("Unexpected FRED CSV structure")
    out=data.rename(columns={date_col:"date",sid:"spot_reference"})[["date","spot_reference"]]
    out["date"]=pd.to_datetime(out.date)
    out["spot_reference"]=pd.to_numeric(out.spot_reference,errors="coerce")
    return out.dropna().reset_index(drop=True)
