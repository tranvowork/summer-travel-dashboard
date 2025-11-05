import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to avoid Tkinter issues

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
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

# Save original labels
flight_df["Season_Label"] = flight_df["Season"]
flight_df["Origin_Label"] = flight_df["Origin City"]
flight_df["Dest_Label"] = flight_df["Destination City"]
flight_df["Airline_Label"] = flight_df["Airline"]

# Label encoding
median_price = flight_df["Predicted Price Per Person (USD)"].median()
flight_df["label_flight"] = (flight_df["Predicted Price Per Person (USD)"] < median_price).astype(int)

for col in ["Season", "Origin City", "Destination City", "Airline"]:
    flight_df[col] = LabelEncoder().fit_transform(flight_df[col].astype(str))

Xf = flight_df[["Season", "Origin City", "Destination City", "Passengers", "Airline", "Route_Mean"]]
yf = flight_df["label_flight"]
Xf_train, Xf_test, yf_train, yf_test = train_test_split(Xf, yf, test_size=0.3, stratify=yf, random_state=42)

clf_flight = LogisticRegression(max_iter=1000)
clf_flight.fit(Xf_train, yf_train)
print("\n✈️ Flight Price Classification Report:")
print(classification_report(yf_test, clf_flight.predict(Xf_test)))

flight_df["prediction"] = clf_flight.predict(Xf)
flight_df["Label"] = flight_df["prediction"].map({1: "Affordable", 0: "Not Affordable"})

from matplotlib.colors import ListedColormap

# Use 2 continuous features for plotting
plot_df = flight_df.copy()
X_plot = plot_df[["Route_Mean", "Predicted Price Per Person (USD)"]].values
y_plot = plot_df["label_flight"].values

# Train logistic model on 2D data
clf_boundary = LogisticRegression()
clf_boundary.fit(X_plot, y_plot)

# Create grid to evaluate model
x_min, x_max = X_plot[:, 0].min() - 1, X_plot[:, 0].max() + 1
y_min, y_max = X_plot[:, 1].min() - 10, X_plot[:, 1].max() + 10
xx, yy = np.meshgrid(np.linspace(x_min, x_max, 300), np.linspace(y_min, y_max, 300))
Z = clf_boundary.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)

# Plotting
plt.figure(figsize=(10, 6))
plt.contourf(xx, yy, Z, cmap=ListedColormap(["red", "green"]), alpha=0.2)

# Plot original points
for result in colors:
    subset = plot_df[plot_df["Result"] == result]
    plt.scatter(
        subset["Route_Mean"],
        subset["Predicted Price Per Person (USD)"],
        label=result,
        alpha=0.6,
        c=colors[result]
    )

plt.xlabel("Route Mean")
plt.ylabel("Predicted Price Per Person (USD)")
plt.title("Flight Classification with Decision Boundary")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("flight_decision_boundary.png")
plt.close()

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

# Save original labels
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

airbnb_df["prediction"] = clf_airbnb.predict(Xa)
airbnb_df["Label"] = airbnb_df["prediction"].map({1: "Best Value", 0: "Not Best Value"})

# Determine classification outcome
airbnb_df["Actual"] = airbnb_df["label_airbnb"]
airbnb_df["Predicted"] = airbnb_df["prediction"]

def classify_airbnb(row):
    if row["Actual"] == 1 and row["Predicted"] == 1:
        return "True Positive"
    elif row["Actual"] == 0 and row["Predicted"] == 1:
        return "False Positive"
    elif row["Actual"] == 0 and row["Predicted"] == 0:
        return "True Negative"
    elif row["Actual"] == 1 and row["Predicted"] == 0:
        return "False Negative"

airbnb_df["Result"] = airbnb_df.apply(classify_airbnb, axis=1)

# Scatter plot of Airbnb price vs accommodates, colored by result
plt.figure(figsize=(10, 6))
for result in colors:
    subset = airbnb_df[airbnb_df["Result"] == result]
    plt.scatter(
        subset["Airbnb_Price_Night"],
        subset["Accomodates"],
        label=result,
        color=colors[result],
        alpha=0.5
    )

plt.title("Airbnb Classification Outcomes")
plt.xlabel("Airbnb Price per Night")
plt.ylabel("Accommodates")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("airbnb_classification_outcomes.png")
plt.close()
