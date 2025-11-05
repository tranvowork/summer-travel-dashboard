import pandas as pd

# --- Load raw flight data ---
flights = pd.read_csv("flight_price.csv")

# --- Select and rename columns ---
flights_cleaned = flights[[
    "Year", "Quarter", "Destination City", "Route_Mean", "Predicted Price Per Person (USD)"
]].copy()

# --- Rename Destination City to City ---
flights_cleaned.rename(columns={
    "Destination City": "City",
    "Route_Mean": "FlightPrice",
    "Predicted Price Per Person (USD)": "PredictedFlightPrice"
}, inplace=True)

# --- Standardize city names ---
flights_cleaned["City"] = flights_cleaned["City"].str.strip().str.lower()

# --- Preview 5 rows ---
# Show all columns in full width for review
pd.set_option("display.max_columns", None)
pd.set_option("display.expand_frame_repr", False)
pd.set_option("display.max_colwidth", None)

# Display the first 5 rows in full
print(flights_cleaned.head(5))

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

# --- Load Reddit sentiment data ---
sentiment = pd.read_csv("sentiment_ranking_scores.csv")

# --- Rename and clean city names ---
sentiment.rename(columns={"search_city": "City", "compound": "Sentiment"}, inplace=True)
sentiment["City"] = sentiment["City"].str.strip().str.lower()

# --- Fix city name inconsistencies ---
sentiment["City"] = sentiment["City"].replace({
    "new york city": "new york",
    "washington": "washington, dc"
})

# --- Preview ---
pd.set_option("display.max_columns", None)
pd.set_option("display.expand_frame_repr", False)
pd.set_option("display.max_colwidth", None)
print(sentiment.head())
