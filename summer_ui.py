import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import os

# ---------------------
# PAGE CONFIGURATION
# ---------------------
st.set_page_config(
    page_title="Top Summer Travel Destinations",
    layout="wide",
    page_icon="✈️"
)

# ---------------------
# LOAD DATA
# ---------------------
@st.cache_data
def load_data():
    df = pd.read_csv("top_ranking.csv")
    df["City"] = df["City"].str.title()

    # Full coordinates for all 11 cities
    city_coords = {
        "San Diego": (32.7157, -117.1611),
        "New Orleans": (29.9511, -90.0715),
        "New York": (40.7128, -74.0060),
        "San Francisco": (37.7749, -122.4194),
        "Washington, Dc": (38.9072, -77.0369),
        "Seattle": (47.6062, -122.3321),
        "Honolulu": (21.3069, -157.8583),
        "Chicago": (41.8781, -87.6298),
        "Nashville": (36.1627, -86.7816),
        "Boston": (42.3601, -71.0589),
        "Philadelphia": (39.9526, -75.1652)
    }

    df["Latitude"] = df["City"].map(lambda x: city_coords.get(x, (None, None))[0])
    df["Longitude"] = df["City"].map(lambda x: city_coords.get(x, (None, None))[1])

    return df

df = load_data()

# ---------------------
# LIGHT BLUE COLOR THEME
# ---------------------
st.markdown("""
    <style>
        body {
            background-color: #eaf6ff;
        }
        .main {
            background-color: #f0f8ff;
        }
        .stApp {
            background-image: linear-gradient(to bottom, #eaf6ff, #ffffff);
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------
# 5 TABS
# ---------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏖️ Top 10 Places for Summer Vacation",
    "✈️ Top Flight Choices",
    "🏡 Top Airbnb Choices",
    "💬 Comments",
    "🤖 Smart Predictions"
])

# ---------------------
# TAB 1: TOP 10 PLACES
# ---------------------
with tab1:
    st.markdown("<h2 style='text-align: center;'>Top 10 Summer Destinations from San Francisco</h2>", unsafe_allow_html=True)

    # Filter sliders
    st.sidebar.header("🔍 Filter Destinations")
    max_flight = st.sidebar.slider("Max Flight Price (USD)", 0, 700, 700)
    max_airbnb = st.sidebar.slider("Max Airbnb Cost (4 Days)", 0, 700, 700)
    min_sentiment = st.sidebar.slider("Minimum Sentiment Score", 0.0, 1.0, 0.0, 0.01)
    selected_cities = st.sidebar.multiselect("Select Cities to Display", df["City"].unique(), default=df["City"].unique())

    filtered_df = df[
        (df["FlightPrice"] <= max_flight) &
        (df["Airbnb_Cost_4_Days"] <= max_airbnb) &
        (df["Sentiment"] >= min_sentiment) &
        (df["City"].isin(selected_cities))
    ].sort_values("OverallScore", ascending=False)

    # --- 🌟 Highlight top destination
    city_emojis = {
        "Honolulu": "🌺",
        "New York": "🗽",
        "San Francisco": "🌉",
        "Seattle": "☕",
        "San Diego": "🌊",
        "Chicago": "🌆",
        "Nashville": "🎶",
        "Boston": "📚",
        "New Orleans": "🎷",
        "Washington, Dc": "🏛️",
        "Philadelphia": "🔔"
    }

    if not filtered_df.empty:
        top_city = filtered_df.iloc[0]["City"]
        emoji = city_emojis.get(top_city, "📍")
        st.markdown(f"""
            <div style='text-align: center; background-color: #dff6ff; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
                <h2 style='color: #0077b6;'>🌟 Let’s go to {emoji} <span style='color: #023e8a'>{top_city}</span>!</h2>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style='text-align: center; background-color: #fff3cd; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
                <h4 style='color: #856404;'>No destinations match your current filters. Try adjusting them!</h4>
            </div>
        """, unsafe_allow_html=True)

    # Map setup
    st.subheader("📍 Destination Map")
    map_df = filtered_df.dropna(subset=["Latitude", "Longitude"]).copy()
    map_df["color"] = [
        [255, 0, 0] if city == "San Francisco" else [0, 180, 0] for city in map_df["City"]
    ]

    map_df["icon_data"] = {
        "url": "https://cdn-icons-png.flaticon.com/512/684/684908.png",
        "width": 128,
        "height": 128,
        "anchorY": 128
    }

    st.pydeck_chart(pdk.Deck(
        initial_view_state=pdk.ViewState(
            latitude=map_df["Latitude"].mean(),
            longitude=map_df["Longitude"].mean(),
            zoom=3.5,
            pitch=30
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=map_df,
                get_position='[Longitude, Latitude]',
                get_radius=35000,
                get_fill_color='color',
                pickable=True
            ),
            pdk.Layer(
                type="IconLayer",
                data=map_df,
                get_icon="icon_data",
                get_size=4,
                size_scale=15,
                get_position='[Longitude, Latitude]',
                pickable=False
            )
        ],
        tooltip={"text": "{City}\nFlight: ${FlightPrice}\nAirbnb: ${Airbnb_Cost_4_Days}"}
    ))

    # Charts: Flight, Airbnb, Sentiment
    st.subheader("📊 Price & Sentiment Comparison")
    col1, col2, col3 = st.columns(3)

    with col1:
        fig1 = px.bar(filtered_df, x="City", y="FlightPrice", title="Flight Price (USD)", color="City")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(filtered_df, x="City", y="Airbnb_Cost_4_Days", title="Airbnb Cost (4 Days)", color="City")
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        fig3 = px.bar(filtered_df, x="City", y="Sentiment", title="Sentiment Score", color="City")
        st.plotly_chart(fig3, use_container_width=True)

    # Ranking Table
    st.subheader("\U0001F3C6 Ranked Destinations")
    styled_df = filtered_df[["Rank", "City", "FlightPrice", "Airbnb_Cost_4_Days", "Sentiment", "OverallScore"]].style.apply(
        lambda x: ['background-color: #d0f0ff' if i < 3 else '' for i in range(len(x))], axis=0
    )
    st.dataframe(styled_df, use_container_width=True)

    st.download_button("Download Filtered Results", data=filtered_df.to_csv(index=False), file_name="filtered_top_ranking.csv")
# ---------------------
# TAB 2: TOP FLIGHT CHOICES
# ---------------------
@st.cache_data
def load_flight_predictions():
    return pd.read_csv("final_cleaned_flight_data.csv")

flight_df = load_flight_predictions()

with tab2:
    st.markdown("<h2 style='text-align: center;'>✈️ Top Flight Choices</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        selected_season = st.selectbox("Select Season", sorted(flight_df["Season"].dropna().unique()))
    with col2:
        selected_airline = st.selectbox("Select Airline", sorted(flight_df["Airline"].dropna().unique()))

    col3, col4 = st.columns(2)
    with col3:
        selected_destination = st.selectbox("Select Destination City", sorted(flight_df["Destination City"].dropna().unique()))
    with col4:
        min_passenger = st.slider("Minimum Passengers", 0, int(flight_df["Passengers"].max()), 0)

    filtered_flight = flight_df[
        (flight_df["Season"] == selected_season) &
        (flight_df["Airline"] == selected_airline) &
        (flight_df["Destination City"] == selected_destination) &
        (flight_df["Passengers"] >= min_passenger)
    ]
    
    st.session_state["selected_city_airbnb"] = selected_destination

    if not filtered_flight.empty:
        estimated_price = filtered_flight.iloc[0]["Predicted Price Per Person (USD)"]
        st.markdown(f"""
            <div style='text-align: center; background-color: #d0f0e0; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
                <h3 style='color: #007a2f;'>💰 Your estimated price: <span style='color: #004b23;'>${estimated_price:.2f}</span></h3>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No results found for the current filter combination.")

    # Route map
    st.subheader("🗺️ Route from San Francisco")
    if not filtered_flight.empty:
        dest_lat = filtered_flight.iloc[0]["Latitude"]
        dest_lon = filtered_flight.iloc[0]["Longitude"]
        sfo_lat, sfo_lon = 37.7749, -122.4194

        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(
                latitude=(sfo_lat + dest_lat) / 2,
                longitude=(sfo_lon + dest_lon) / 2,
                zoom=3.5, pitch=30
            ),
            layers=[
                pdk.Layer("ScatterplotLayer",
                          data=pd.DataFrame([
                              {"lat": sfo_lat, "lon": sfo_lon, "label": "San Francisco"},
                              {"lat": dest_lat, "lon": dest_lon, "label": selected_destination}
                          ]),
                          get_position='[lon, lat]', get_radius=30000,
                          get_fill_color='[0, 150, 255, 160]', pickable=True),
                pdk.Layer("PathLayer",
                          data=[{"path": [[sfo_lon, sfo_lat], [dest_lon, dest_lat]]}],
                          get_path="path", get_width=4,
                          get_color='[0, 0, 255]', get_dash_array=[10, 10],
                          width_min_pixels=2)
            ],
            tooltip={"text": "{label}"}
        ))

    # Price comparisons
    if not filtered_flight.empty:
        st.subheader("📊 Price Comparison to Estimated Value")
        cheaper_df = flight_df[
            flight_df["Predicted Price Per Person (USD)"] < estimated_price
        ].sort_values("Predicted Price Per Person (USD)", ascending=False).head(5)

        pricier_df = flight_df[
            flight_df["Predicted Price Per Person (USD)"] > estimated_price
        ].sort_values("Predicted Price Per Person (USD)").head(5)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 💵 Top 5 Cheaper Options")
            st.dataframe(cheaper_df[[
                "Destination City", "Airline", "Season", "Predicted Price Per Person (USD)"
            ]].reset_index(drop=True))
        with col2:
            st.markdown("### 💸 Top 5 Pricier Options")
            st.dataframe(pricier_df[[
                "Destination City", "Airline", "Season", "Predicted Price Per Person (USD)"
            ]].reset_index(drop=True))

    # --- CTA: Call to Action ---
    st.markdown("""
        <div style='
            background-color: #f0fbff;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
            margin-top: 40px;
            margin-bottom: 20px;
        '>
            <h2 style='color: #0077b6;'>🏡 Ready to book your perfect stay?</h2>
            <p style='color: #023e8a; font-size: 18px; margin-bottom: 20px;'>Explore affordable and top-rated Airbnbs matched to your favorite destination.</p>
        </div>
    """, unsafe_allow_html=True)
    
# ---------------------
# TAB 3: TOP AIRBNB CHOICES
# ---------------------
with tab3:
    # Load Airbnb dataset
    @st.cache_data
    def load_airbnb_data():
        df = pd.read_csv("airbnb_price.csv")
        # Clean price columns
        df["Airbnb_Price_Night"] = pd.to_numeric(df["Airbnb_Price_Night"].replace('[\$,]', '', regex=True), errors='coerce')
        df["Airbnb_Cost_4_Days"] = pd.to_numeric(df["Airbnb_Cost_4_Days"].replace('[\$,]', '', regex=True), errors='coerce')
        return df

    st.markdown("<h2 style='text-align: center;'>🏘️ Find Your Stay</h2>", unsafe_allow_html=True)

    airbnb_df = load_airbnb_data()

    # Auto-select city from Tab 2
    default_city = st.session_state.get("selected_city_airbnb", airbnb_df["City"].iloc[0])
    selected_city = st.selectbox(
        "Select City",
        sorted(airbnb_df["City"].dropna().unique()),
        index=sorted(airbnb_df["City"].dropna().unique()).index(default_city)
    )

    city_df = airbnb_df[airbnb_df["City"] == selected_city]

    # 💡 Suggested Stats
    if not city_df.empty:
        avg_price_night = city_df["Airbnb_Price_Night"].mean()
        avg_price_trip = city_df["Airbnb_Cost_4_Days"].mean()

        st.markdown(f"""
            <div style='
                background-color: #e6f7ff;
                padding: 25px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.06);
                margin-top: 20px;
                margin-bottom: 20px;
            '>
                <h3 style='color: #0077b6;'>💰 Avg. Price Per Night: <strong>${avg_price_night:.2f}</strong></h3>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style='
                background-color: #d9f3ff;
                padding: 25px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.06);
                margin-bottom: 30px;
            '>
                <h4 style='color: #0077b6;'>🛏️ Estimated 4-Day Trip Cost: <strong>${avg_price_trip:.2f}</strong></h4>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No listings available for the selected city.")

    # 🧭 Filter Airbnb Listings (after stat box)
    st.subheader("🔍 Refine Your Preferences")
    col1, col2 = st.columns(2)
    with col1:
        selected_neighborhood = st.selectbox("Neighborhood", sorted(city_df["Neighborhood"].dropna().unique()))
    with col2:
        selected_room_type = st.selectbox("Room Type", sorted(city_df["Room_Type"].dropna().unique()))
    col3, col4 = st.columns(2)
    with col3:
        min_bath = st.slider("Min Bathrooms", 0.0, float(city_df["Bathrooms"].max()), 0.0, 0.5)
    with col4:
        min_bedroom = st.slider("Min Bedrooms", 0, int(city_df["Bedrooms"].max()), 0)

    # Apply filters for listing display
    filtered_airbnb = city_df[
        (city_df["Neighborhood"] == selected_neighborhood) &
        (city_df["Room_Type"] == selected_room_type) &
        (city_df["Bathrooms"] >= min_bath) &
        (city_df["Bedrooms"] >= min_bedroom)
    ]

    # 📊 Visualization
    if not filtered_airbnb.empty:
        import plotly.express as px

            # 📊 Visualization: Scatter Plot - Price vs Bedrooms colored by Score
    st.subheader("📊 Airbnb Price Scatter Plot")

    if not filtered_airbnb.empty:
        import plotly.express as px

        fig = px.scatter(
            filtered_airbnb,
            x="Bedrooms",
            y="Airbnb_Price_Night",
            color="Airbnb_Score",  # color by score
            size="Bathrooms",
            hover_data=["Neighborhood", "Room_Type"],
            labels={
                "Bedrooms": "Number of Bedrooms",
                "Airbnb_Price_Night": "Price per Night (USD)",
                "Airbnb_Score": "Airbnb Score"
            },
            title="Airbnb Price vs. Bedrooms (Color = Score, Size = Bathrooms)",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data to visualize. Try adjusting your filters.")

    # 🗂️ Table
    st.subheader("📋 Matching Airbnb Listings")
    if not filtered_airbnb.empty:
        st.dataframe(filtered_airbnb[[
            "City", "Neighborhood", "Room_Type",
            "Bedrooms", "Bathrooms", "Airbnb_Price_Night", "Airbnb_Score", "Airbnb_Cost_4_Days"
        ]], use_container_width=True)
    else:
        st.warning("No listings match your refined filters.")

# ---------------------
# TAB 4: SENTIMENT
# ---------------------
with tab4:
    st.markdown("<h2 style='text-align: center;'>💬 What Travelers Are Saying</h2>", unsafe_allow_html=True)

    import re
    from collections import Counter
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt

    # --- Define your keyword lists
    positive_keywords = [
        "love", "amazing", "great", "awesome", "fun", "beautiful", "magical", "enjoy", "stunning",
        "relaxing", "safe", "recommend", "gorgeous", "worth", "favorite", "memorable", "excellent", "cool"
    ]
    negative_keywords = [
        "hate", "boring", "expensive", "dangerous", "unsafe", "disappointing", "avoid", "problem", "issue",
        "overrated", "horrible", "dirty", "terrible", "traffic", "smog", "waste", "crowded", "difficult"
    ]

    # --- Helper: Load and clean data
    @st.cache_data
    def load_reddit_data():
        df = pd.read_csv("reddit_comments.csv")
        df["body"] = df["body"].astype(str).str.lower().str.replace(r"\n", " ", regex=True)
        df["body"] = df["body"].str.replace(r"http\S+", "", regex=True)
        df["body"] = df["body"].str.replace(r"[^a-z\s]", "", regex=True)
        return df

    # --- Helper: Count selected keywords in comment bodies
    def get_keyword_frequencies(texts, keyword_list):
        words = []
        for text in texts:
            words.extend(re.findall(r'\b\w+\b', text))
        filtered = [w for w in words if w in keyword_list]
        return dict(Counter(filtered))

    # --- Helper: Generate and render word cloud
    def plot_wordcloud(frequencies, title, colormap="Greens"):
        if not frequencies:
            st.info(f"No {title.lower()} found for this city.")
            return
        wc = WordCloud(width=800, height=400, background_color="white", colormap=colormap).generate_from_frequencies(frequencies)
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        ax.set_title(title, fontsize=16)
        st.pyplot(fig)

    # --- Load data
    reddit_df = load_reddit_data()

    # --- City dropdown
    cities = sorted(reddit_df["matched_city"].dropna().unique())
    selected_city = st.selectbox("Select a City", cities, index=cities.index(st.session_state.get("selected_city_airbnb", cities[0])))

    # --- Filter comments by city
    city_comments = reddit_df[reddit_df["matched_city"] == selected_city]["body"].dropna().tolist()

    # --- Compute frequencies
    pos_freq = get_keyword_frequencies(city_comments, positive_keywords)
    neg_freq = get_keyword_frequencies(city_comments, negative_keywords)

    # --- Visualize both word clouds
    col1, col2 = st.columns(2)
    with col1:
        plot_wordcloud(pos_freq, f"Positive Travel Terms - {selected_city}", colormap="Greens")
    with col2:
        plot_wordcloud(neg_freq, f"Negative Travel Terms - {selected_city}", colormap="Reds")
    # --- CTA: Summer Planning Box ---
st.markdown("""
    <div style='
        background-color: #fff8e1;
        padding: 30px 40px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.06);
        margin-top: 40px;
        margin-bottom: 30px;
    '>
        <h2 style='color: #e65100;'>🌞 Ready to plan your summer vacation?</h2>
        <p style='color: #4e342e; font-size: 18px; margin-top: 10px; margin-bottom: 25px;'>
            You’ve gathered the inspiration from real travelers — now it’s time to <strong>turn that into action</strong>. Explore flights, compare stays, and map your next adventure.
        </p>
        <form action="" method="post">
            <button name="go_to_tab1" style='
                background-color: #ffb74d;
                color: white;
                font-size: 18px;
                padding: 12px 30px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                transition: background-color 0.3s;
            ' onmouseover="this.style.backgroundColor='#ffa726'" onmouseout="this.style.backgroundColor='#ffb74d'">
                ✈️ Explore Destinations
            </button>
        </form>
    </div>
""", unsafe_allow_html=True)
    

# ---------------------
# TAB 5: ML PREDICTIONS
# ---------------------    
with tab5:
    st.markdown("<h2 style='text-align: center;'>🤖 Smart ML Predictions</h2>", unsafe_allow_html=True)

    @st.cache_data
    def load_predictions():
        flight_pred = pd.read_csv("flight_predictions.csv")
        airbnb_pred = pd.read_csv("airbnb_predictions.csv")
        return flight_pred, airbnb_pred

    flight_pred, airbnb_pred = load_predictions()

    # --- ✈️ Flight Prediction Filters ---
    st.subheader("✈️ Flight Price Predictions")

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_season = st.selectbox("Season", ["All"] + sorted(flight_pred["Season"].dropna().unique()))
    with col2:
        selected_city = st.selectbox("Destination City", ["All"] + sorted(flight_pred["Destination City"].dropna().unique()))
    with col3:
        selected_airline = st.selectbox("Airline", ["All"] + sorted(flight_pred["Airline"].dropna().unique()))

    min_price = float(flight_pred["Predicted Price Per Person (USD)"].min())
    max_price = float(flight_pred["Predicted Price Per Person (USD)"].max())
    price_range = st.slider("Filter by Predicted Price", min_value=min_price, max_value=max_price, value=(min_price, max_price))

    selected_label = st.selectbox("Prediction Label", ["All", "Affordable", "Not Affordable"])

    filtered_flight = flight_pred[
        (flight_pred["Predicted Price Per Person (USD)"] >= price_range[0]) &
        (flight_pred["Predicted Price Per Person (USD)"] <= price_range[1])
    ]

    if selected_season != "All":
        filtered_flight = filtered_flight[filtered_flight["Season"] == selected_season]
    if selected_city != "All":
        filtered_flight = filtered_flight[filtered_flight["Destination City"] == selected_city]
    if selected_airline != "All":
        filtered_flight = filtered_flight[filtered_flight["Airline"] == selected_airline]
    if selected_label != "All":
        filtered_flight = filtered_flight[filtered_flight["Label"] == selected_label]

    # 📋 Show Filtered Table
    st.dataframe(filtered_flight[[
        "Season", "Destination City", "Airline", "Predicted Price Per Person (USD)", "Label"
    ]], use_container_width=True)

    # 📊 Price Visualization
    import plotly.express as px
    st.subheader("📊 Flight Prediction Summary by Airline & Label")

    if not filtered_flight.empty:
        fig = px.histogram(
            filtered_flight,
            x="Airline",
            color="Label",
            hover_data=["Destination City", "Predicted Price Per Person (USD)"],
            barmode="group",
            title="Flight Classification by Airline",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No flight data matches the current filters.")


    # --- Airbnb Predictions ---
      # --- 🏡 Airbnb Predictions ---
    st.subheader("🏡 Airbnb Value Predictions")

    col1, col2 = st.columns(2)
    with col1:
        selected_city = st.selectbox("City", ["All"] + sorted(airbnb_pred["City"].dropna().unique()))
    with col2:
        selected_neighborhood = st.selectbox("Neighborhood", ["All"] + sorted(airbnb_pred["Neighborhood"].dropna().unique()))

    col3, col4 = st.columns(2)
    with col3:
        min_bedroom = st.slider("Min Bedrooms", 0, int(airbnb_pred["Bedrooms"].max()), 0)
    with col4:
        min_bathroom = st.slider("Min Bathrooms", 0.0, float(airbnb_pred["Bathrooms"].max()), 0.0, step=0.5)

    price_min = float(airbnb_pred["Airbnb_Price_Night"].min())
    price_max = float(airbnb_pred["Airbnb_Price_Night"].max())
    price_range = st.slider("Filter by Price per Night", min_value=price_min, max_value=price_max, value=(price_min, price_max))

    selected_airbnb_label = st.selectbox("Prediction Label", ["All", "Best Value", "Not Best Value"])

    # Apply filters
    filtered_airbnb = airbnb_pred[
        (airbnb_pred["Bedrooms"] >= min_bedroom) &
        (airbnb_pred["Bathrooms"] >= min_bathroom) &
        (airbnb_pred["Airbnb_Price_Night"] >= price_range[0]) &
        (airbnb_pred["Airbnb_Price_Night"] <= price_range[1])
    ]
    if selected_city != "All":
        filtered_airbnb = filtered_airbnb[filtered_airbnb["City"] == selected_city]
    if selected_neighborhood != "All":
        filtered_airbnb = filtered_airbnb[filtered_airbnb["Neighborhood"] == selected_neighborhood]
    if selected_airbnb_label != "All":
        filtered_airbnb = filtered_airbnb[filtered_airbnb["Label"] == selected_airbnb_label]

    # Show filtered table
    st.dataframe(filtered_airbnb[[
        "City", "Neighborhood", "Bedrooms", "Bathrooms", "Airbnb_Price_Night", "Label"
    ]], use_container_width=True)

    # Bar chart visualization
    st.subheader("📊 Airbnb Classification by City")

    if not filtered_airbnb.empty:
        fig2 = px.histogram(
            filtered_airbnb,
            x="Neighborhood",
            color="Label",
            hover_data=["Neighborhood", "Bedrooms", "Bathrooms", "Airbnb_Price_Night"],
            barmode="group",
            title="Airbnb Predictions Grouped by Label"
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No Airbnb listings match the current filters.")
        
# ------------------------------------
    # 📣 CTA – Collect User Feedback
    # ------------------------------------
    st.markdown("""
        <div style='
            background-color: #e0f7fa;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            margin-top: 40px;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
        '>
            <h3 style='color: #00796b;'>🌟 Help Us Improve!</h3>
            <p style='color: #004d40;'>Was the prediction helpful in planning your trip?</p>
        </div>
    """, unsafe_allow_html=True)

    user_feedback = st.radio("Your feedback on the prediction:", ["👍 Yes", "👎 No"], horizontal=True)
    feedback_button = st.button("✅ Submit Feedback")

    if feedback_button:
        feedback_data = {
            "feedback": user_feedback,
            "page": "Tab 5 - ML Prediction"
        }
        feedback_df = pd.DataFrame([feedback_data])
        feedback_df.to_csv("user_feedback_log.csv", mode="a", header=not os.path.exists("user_feedback_log.csv"), index=False)
        st.success("✅ Thanks! Your feedback has been recorded.")

