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