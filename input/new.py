import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("top_ranking.csv")
    df["City"] = df["City"].str.title()  # Capitalize for display
    return df

df = load_data()

st.title("✈️ Top 10 Summer Destinations from San Francisco")

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")
max_flight = st.sidebar.slider("Max Flight Price (USD)", 0, int(df["FlightPrice"].max()), int(df["FlightPrice"].max()))
max_airbnb = st.sidebar.slider("Max Airbnb Cost (4 Days)", 0, int(df["Airbnb_Cost_4_Days"].max()), int(df["Airbnb_Cost_4_Days"].max()))
min_sentiment = st.sidebar.slider("Minimum Sentiment Score", float(df["Sentiment"].min()), float(df["Sentiment"].max()), 0.0)

# --- Filter Data ---
filtered_df = df[
    (df["FlightPrice"] <= max_flight) &
    (df["Airbnb_Cost_4_Days"] <= max_airbnb) &
    (df["Sentiment"] >= min_sentiment)
].sort_values("OverallScore", ascending=False)

# --- Highlight Best Pick ---
if not filtered_df.empty:
    top_city = filtered_df.iloc[0]
    st.markdown(f"### 🎯 Best Pick: **{top_city['City']}**")

# --- Ranking Table ---
st.subheader("🏆 Ranked Destinations")
st.dataframe(filtered_df[["Rank", "City", "FlightPrice", "Airbnb_Cost_4_Days", "Sentiment", "OverallScore"]])

# --- Download Button ---
st.download_button("📥 Download Filtered Results", data=filtered_df.to_csv(index=False), file_name="filtered_top_ranking.csv")

# --- City Map ---
st.subheader("🗺️ City Locations")
if "Latitude" in df.columns and "Longitude" in df.columns:
    map_df = filtered_df.dropna(subset=["Latitude", "Longitude"])
    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=map_df["Latitude"].mean(),
            longitude=map_df["Longitude"].mean(),
            zoom=4, pitch=40
        ),
        layers=[pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position='[Longitude, Latitude]',
            get_radius=30000,
            get_fill_color='[255*(1-Sentiment), 255*Sentiment, 100]',
            pickable=True
        )],
        tooltip={"text": "{City}\nFlight: ${FlightPrice}\nAirbnb: ${Airbnb_Cost_4_Days}"}
    ))

# --- Comparison Charts ---
st.subheader("📊 Price & Sentiment Comparison")

col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(filtered_df, x="City", y="FlightPrice", title="Flight Price (USD)", color="City")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.bar(filtered_df, x="City", y="Airbnb_Cost_4_Days", title="Airbnb Cost (4 Days)", color="City")
    st.plotly_chart(fig2, use_container_width=True)

fig3 = px.bar(filtered_df, x="City", y="Sentiment", title="Sentiment Score", color="City")
st.plotly_chart(fig3, use_container_width=True)

# --- City Dropdown Comparison ---
st.subheader("🔍 Detailed View by City")
selected_city = st.selectbox("Select a city to view details", df["City"].unique())

if selected_city:
    city_info = df[df["City"] == selected_city].iloc[0]
    st.markdown(f"""
    **City**: {selected_city}  
    **Flight Price**: ${city_info['FlightPrice']:.2f}  
    **Airbnb Cost (4 Days)**: ${city_info['Airbnb_Cost_4_Days']:.2f}  
    **Sentiment**: {city_info['Sentiment']:.2f}  
    **Overall Score**: {city_info['OverallScore']:.4f}  
    **Rank**: #{city_info['Rank']}
    """)