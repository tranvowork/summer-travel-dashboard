import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report

# --- FLIGHT CLASSIFICATION ---
flight_df = pd.read_csv("flight_price.csv")
flight_df.columns = [col.strip() for col in flight_df.columns]
flight_df = flight_df.dropna(subset=["Predicted Price Per Person (USD)", "Route_Mean"])
flight_df = flight_df.sample(n=5000, random_state=42)

# Convert Quarter to Season
flight_df["Season"] = flight_df["Quarter"].map({2: "Early Summer", 3: "Late Summer"})

# Collapse airline code columns
airline_cols = [col for col in flight_df.columns if col.startswith("Airline Code_")]
flight_df["Airline_Code"] = flight_df[airline_cols].idxmax(axis=1).str.replace("Airline Code_", "")
airline_map = {
    "AS": "Alaska Airlines", "AA": "American Airlines", "DL": "Delta",
    "F9": "Frontier Airlines", "B6": "JetBlue Airways", "WN": "Southwest Airlines", "UA": "United"
}
flight_df["Airline"] = flight_df["Airline_Code"].map(airline_map)
flight_df.drop(columns=airline_cols + ["Airline_Code"], inplace=True)

# Save original values for output
flight_df["Season_Label"] = flight_df["Season"]
flight_df["Origin_Label"] = flight_df["Origin City"]
flight_df["Dest_Label"] = flight_df["Destination City"]
flight_df["Airline_Label"] = flight_df["Airline"]

# Label creation
median_price = flight_df["Predicted Price Per Person (USD)"].median()
flight_df["label_flight"] = (flight_df["Predicted Price Per Person (USD)"] < median_price).astype(int)

# Encode features
for col in ["Season", "Origin City", "Destination City", "Airline"]:
    flight_df[col] = LabelEncoder().fit_transform(flight_df[col].astype(str))

Xf = flight_df[["Season", "Origin City", "Destination City", "Passengers", "Airline", "Route_Mean"]]
yf = flight_df["label_flight"]
Xf_train, Xf_test, yf_train, yf_test = train_test_split(Xf, yf, test_size=0.3, stratify=yf, random_state=42)

clf_flight = LogisticRegression(max_iter=1000)
clf_flight.fit(Xf_train, yf_train)
print("\n✈️ Flight Price Classification Report:")
print(classification_report(yf_test, clf_flight.predict(Xf_test)))

# Predict and export
flight_df["prediction"] = clf_flight.predict(Xf)
flight_df["Label"] = flight_df["prediction"].map({1: "Affordable", 0: "Not Affordable"})

flight_output = flight_df[[
    "Season_Label", "Origin_Label", "Dest_Label", "Passengers", "Airline_Label",
    "Route_Mean", "Predicted Price Per Person (USD)", "Label"
]].rename(columns={
    "Season_Label": "Season", "Origin_Label": "Origin City",
    "Dest_Label": "Destination City", "Airline_Label": "Airline"
})
flight_output.to_csv("flight_predictions.csv", index=False)

# --- AIRBNB CLASSIFICATION ---
airbnb_df = pd.read_csv("airbnb_price.csv")
airbnb_df.columns = [col.strip() for col in airbnb_df.columns]

def extract_price(text):
    try:
        prices = [float(p.replace("$", "").strip()) for p in str(text).split() if p.replace("$", "").replace(".", "").isdigit()]
        return sum(prices)/len(prices) if prices else None
    except:
        return None

airbnb_df["Airbnb_Price_Night"] = airbnb_df["Airbnb_Price_Night"].apply(extract_price)
airbnb_df = airbnb_df.dropna(subset=["Airbnb_Price_Night"]).sample(n=5000, random_state=42)

# Save original values
airbnb_df["City_Label"] = airbnb_df["City"]
airbnb_df["Neighborhood_Label"] = airbnb_df["Neighborhood"]
airbnb_df["Room_Label"] = airbnb_df["Room_Type"]
airbnb_df["Property_Label"] = airbnb_df["Property_Type"]

median_airbnb_price = airbnb_df["Airbnb_Price_Night"].median()
airbnb_df["label_airbnb"] = (airbnb_df["Airbnb_Price_Night"] < median_airbnb_price).astype(int)

for col in ["City", "Neighborhood", "Room_Type", "Property_Type"]:
    airbnb_df[col] = LabelEncoder().fit_transform(airbnb_df[col].astype(str))

Xa = airbnb_df[["City", "Neighborhood", "Room_Type", "Property_Type", "Bedrooms", "Bathrooms", "Beds", "Accomodates"]]
ya = airbnb_df["label_airbnb"]
Xa_train, Xa_test, ya_train, ya_test = train_test_split(Xa, ya, test_size=0.3, stratify=ya, random_state=42)

clf_airbnb = LogisticRegression(max_iter=1000)
clf_airbnb.fit(Xa_train, ya_train)
print("\n🏡 Airbnb Price Classification Report:")
print(classification_report(ya_test, clf_airbnb.predict(Xa_test)))

# Predict and export
airbnb_df["prediction"] = clf_airbnb.predict(Xa)
airbnb_df["Label"] = airbnb_df["prediction"].map({1: "Best Value", 0: "Not Best Value"})

airbnb_output = airbnb_df[[
    "City_Label", "Neighborhood_Label", "Room_Label", "Property_Label",
    "Bedrooms", "Bathrooms", "Beds", "Accomodates",
    "Airbnb_Price_Night", "Label"
]].rename(columns={
    "City_Label": "City", "Neighborhood_Label": "Neighborhood",
    "Room_Label": "Room_Type", "Property_Label": "Property_Type"
})
airbnb_output.to_csv("airbnb_predictions.csv", index=False)

