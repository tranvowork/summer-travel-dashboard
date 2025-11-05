import pandas as pd

# -----------------------
# STEP 1: Clean Flight Data
# -----------------------

flights = pd.read_csv("flight_price.csv")

flights_cleaned = flights[[
    "Year", "Quarter", "Destination City", "Route_Mean", "Predicted Price Per Person (USD)"
]].copy()

flights_cleaned.rename(columns={
    "Destination City": "City",
    "Route_Mean": "FlightPrice",
    "Predicted Price Per Person (USD)": "PredictedFlightPrice"
}, inplace=True)

flights_cleaned["City"] = flights_cleaned["City"].str.strip().str.lower()

# -----------------------
# STEP 2: Clean Airbnb Data
# -----------------------

airbnb = pd.read_csv("airbnb_price.csv")
airbnb["City"] = airbnb["City"].str.strip().str.lower()

airbnb["City"] = airbnb["City"].replace({
    "hawaii": "honolulu",
    "washington dc": "washington, dc"
})

def extract_avg_price(text):
    try:
        prices = [float(p.replace("$", "").strip()) for p in str(text).split() if p.replace("$", "").replace(".", "").isdigit()]
        return sum(prices) / len(prices) if prices else None
    except:
        return None

airbnb["Airbnb_Price_Night"] = airbnb["Airbnb_Price_Night"].apply(extract_avg_price)
airbnb["Airbnb_Cost_4_Days"] = airbnb["Airbnb_Cost_4_Days"].apply(extract_avg_price)

airbnb_cleaned = airbnb.groupby("City").agg({
    "Airbnb_Price_Night": "mean",
    "Airbnb_Score": "mean",
    "Airbnb_Cost_4_Days": "mean"
}).reset_index()

# -----------------------
# STEP 3: Clean Sentiment Data
# -----------------------

sentiment = pd.read_csv("sentiment_ranking_scores.csv")
sentiment.rename(columns={"search_city": "City", "compound": "Sentiment"}, inplace=True)
sentiment["City"] = sentiment["City"].str.strip().str.lower()

sentiment["City"] = sentiment["City"].replace({
    "new york city": "new york",
    "washington": "washington, dc"
})

# -----------------------
# STEP 4: Filter to Top 10 Cities
# -----------------------

top_cities = [
    "san diego", "new orleans", "new york", "san francisco", "washington, dc",
    "seattle", "honolulu", "chicago", "nashville", "boston"
]

flights_top = flights_cleaned[flights_cleaned["City"].isin(top_cities)]
airbnb_top = airbnb_cleaned[airbnb_cleaned["City"].isin(top_cities)]
sentiment_top = sentiment[sentiment["City"].isin(top_cities)]

# -----------------------
# STEP 5: Merge All Datasets
# -----------------------

merged = (
    airbnb_top
    .merge(flights_top, on="City", how="outer")
    .merge(sentiment_top, on="City", how="outer")
)

merged["Sentiment"] = merged["Sentiment"].fillna(0)
merged = merged.sort_values("City")

# ✅ Remove duplicated cities (keep the first occurrence)
merged = merged.drop_duplicates(subset="City", keep="first")

# --- Handle San Francisco local trip (free flight) ---
merged.loc[(merged["City"] == "san francisco") & (merged["FlightPrice"].isna()), "FlightPrice"] = 0.01

# --- Normalize and calculate scores ---
merged["Score_Flight"] = 1 / merged["FlightPrice"]
merged["Score_Airbnb"] = 1 / merged["Airbnb_Cost_4_Days"]
merged["Score_Sentiment"] = merged["Sentiment"]

# Avoid infinite values
merged["Score_Flight"].replace([float("inf"), -float("inf")], 0, inplace=True)
merged["Score_Airbnb"].replace([float("inf"), -float("inf")], 0, inplace=True)

# --- Compute weighted OverallScore ---
merged["OverallScore"] = (
    0.4 * merged["Score_Flight"].fillna(0) +
    0.3 * merged["Score_Airbnb"].fillna(0) +
    0.3 * merged["Score_Sentiment"].fillna(0)
)

# --- Rank cities ---
merged["Rank"] = merged["OverallScore"].rank(ascending=False).astype(int)

# --- Sort for output ---
merged = merged.sort_values("OverallScore", ascending=False)
# -----------------------
# STEP 6: Export Final File
# -----------------------

merged.to_csv("top_ranking.csv", index=False)
print("✅ Ranked top cities saved with OverallScore to top_ranking.csv")

