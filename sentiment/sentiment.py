import pandas as pd

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
