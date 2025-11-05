import pandas as pd

# --- Load Airbnb data ---
airbnb = pd.read_csv("airbnb_price.csv")

# --- Rename cities to match flight file ---
airbnb["City"] = airbnb["City"].str.strip().str.lower()

# Fix inconsistent names
airbnb["City"] = airbnb["City"].replace({
    "hawaii": "honolulu",
    "washington dc": "washington, dc"
})

# --- Clean price fields (remove $, handle multiple values) ---
def extract_avg_price(text):
    try:
        prices = [float(p.replace("$", "").strip()) for p in str(text).split() if p.replace("$", "").replace(".", "").isdigit()]
        return sum(prices) / len(prices) if prices else None
    except:
        return None

airbnb["Airbnb_Price_Night"] = airbnb["Airbnb_Price_Night"].apply(extract_avg_price)
airbnb["Airbnb_Cost_4_Days"] = airbnb["Airbnb_Cost_4_Days"].apply(extract_avg_price)

# --- Group by City and aggregate ---
airbnb_cleaned = airbnb.groupby("City").agg({
    "Airbnb_Price_Night": "mean",
    "Airbnb_Score": "mean",
    "Airbnb_Cost_4_Days": "mean"
}).reset_index()

# --- Preview ---
pd.set_option("display.max_columns", None)
pd.set_option("display.expand_frame_repr", False)
pd.set_option("display.max_colwidth", None)
print(airbnb_cleaned.head())
