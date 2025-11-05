<!--
🎨 Color Theme: Inspired by Airbnb
Main color: #FF5A5F (coral red)
Accent: #FFB400 (gold)
Neutral: #484848 (charcoal)
-->

<h1 align="center">🏖️ Summer Travel Prediction Dashboard</h1>
<h3 align="center">A Data-Driven Approach to Recommending Affordable and Popular Summer Trips (SFO → Top 10 U.S. Cities)</h3>

---

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?logo=python">
  <img src="https://img.shields.io/badge/Framework-Streamlit-FF4B4B?logo=streamlit">
  <img src="https://img.shields.io/badge/Tool-Jupyter_Notebook-orange?logo=jupyter">
  <img src="https://img.shields.io/badge/Visualization-Plotly-0099C8?logo=plotly">
  <img src="https://img.shields.io/badge/Data-BTS%20|%20Airbnb%20|%20Reddit-lightgrey">
</p>

---

## Objectives  
This dashboard empowers **product teams** and **marketing teams** to design smarter summer campaigns by merging **flight prices**, **Airbnb listings**, and **traveler sentiment** into one analytical platform.  

The **Streamlit dashboard** identifies the **most affordable and popular** 4-day round trips from **San Francisco (SFO)** to **top 10 U.S. cities**, enabling:
- Data-driven **destination targeting**
- **Ad spend optimization**
- **Improved traveler satisfaction**

---

## Background  
Travel marketers face challenges due to:
- Constantly shifting **flight and accommodation prices**
- Fragmented **real-time data**
- Limited understanding of **traveler sentiment**

This analysis applies **predictive analytics** and **NLP-based sentiment analysis** to help answer:

> *“Where should we promote next summer’s trips — and when?”*

---

## Executive Summary  

| **Metric** | **Definition** | **Business Value** |
|-------------|----------------|--------------------|
| ✈️ **Flight Affordability Index (FAI)** | Predicted fare trendlines from BTS & Expedia data | Identifies cheapest travel windows |
| 🏡 **Airbnb Quality-Affordability Score (AQS)** | Combines price & rating | Suggests best-value lodging |
| 💬 **Sentiment Index (SI)** | Reddit-based traveler emotion scoring | Reveals real-time public perception |
| 🌆 **Overall Destination Score (ODS)** | Weighted blend of FAI + AQS + SI | Ranks best summer cities |

**Example Insight:**  
> 🌞 *San Diego* tops the list — strong positive sentiment *(0.694)* and balanced affordability.  
> 🌫️ *Boston* shows lower sentiment *(0.540)* but remains cost-competitive.

---

## 📈 Dataset Overview  

| **Dataset** | **Source** | **Variables** | **Purpose** |
|--------------|------------|----------------|--------------|
| ✈️ Flight Data | [BTS](https://www.transtats.bts.gov/), Expedia Scraper | `year`, `quarter`, `carrier`, `fare`, `distance` | Predict affordability |
| 🏠 Airbnb Listings | [InsideAirbnb](https://insideairbnb.com/) | `room_type`, `price`, `rating`, `bedrooms` | Rank accommodations |
| 💬 Reddit Sentiment | [Reddit API](https://www.reddit.com/dev/api/) | `comment`, `city`, `sentiment_score` | Measure popularity |

**ERD**


# summer-travel-dashboard
Interactive Streamlit dashboard analyzing top summer travel destinations using Airbnb and flight data. Combines pricing, sentiment, and demand analytics to uncover affordable, high-interest cities demonstrating data-driven travel insights.
