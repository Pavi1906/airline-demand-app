# app.py
import os
import io
import textwrap
import numpy as np
import pandas as pd
import requests
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
AVIATIONSTACK_KEY = os.getenv("AVIATIONSTACK_KEY")

# --- Streamlit config ---
st.set_page_config(page_title="Airline Demand Demo", layout="wide")

# --- Fetch OpenFlights dataset ---
@st.cache_data
def fetch_openflights():
    airports_url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
    routes_url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"

    airports_raw = requests.get(airports_url).text
    routes_raw = requests.get(routes_url).text

    airports = pd.read_csv(io.StringIO(airports_raw), header=None, dtype=str)
    airports.columns = [
        "AirportID","Name","City","Country","IATA","ICAO","Latitude","Longitude",
        "Altitude","Timezone","DST","TzDatabaseTimeZone","Type","Source"
    ]

    routes = pd.read_csv(io.StringIO(routes_raw), header=None, dtype=str)
    routes.columns = ["Airline","AirlineID","SourceIATA","SourceAirportID",
                      "DestIATA","DestAirportID","Codeshare","Stops","Equipment"]

    routes = routes.dropna(subset=["SourceIATA", "DestIATA"])

    return airports, routes

# --- Join airports + routes ---
@st.cache_data
def prepare_routes(airports, routes):
    a = airports[airports.IATA.notna()]
    a = a[a.IATA != "\\N"]

    r = routes.copy()
    r = r[(r.SourceIATA != "\\N") & (r.DestIATA != "\\N")]

    r = r.merge(a[["IATA","City","Country","Name","Latitude","Longitude"]],
                left_on="SourceIATA", right_on="IATA", how="left"
                ).rename(columns={
                    "City":"SourceCity","Country":"SourceCountry","Name":"SourceName",
                    "Latitude":"SourceLat","Longitude":"SourceLon"
                }).drop(columns=["IATA"])

    r = r.merge(a[["IATA","City","Country","Name","Latitude","Longitude"]],
                left_on="DestIATA", right_on="IATA", how="left"
                ).rename(columns={
                    "City":"DestCity","Country":"DestCountry","Name":"DestName",
                    "Latitude":"DestLat","Longitude":"DestLon"
                }).drop(columns=["IATA"])

    r["route"] = r["SourceIATA"] + "-" + r["DestIATA"]
    return r

# --- Simulated trends ---
def simulate_price_trend(route, months=24, seed=None):
    rng = np.random.default_rng(seed)
    t = np.arange(months)
    season = 15 * np.sin(2 * np.pi * t / 12)
    base = 100 + (hash(route) % 50)
    trend = 0.5 * t
    noise = rng.normal(0, 6, size=months)
    prices = base + season + trend + noise
    dates = pd.date_range(end=pd.Timestamp.today(), periods=months, freq="M")
    return pd.DataFrame({"month": dates, "price": prices})

def simulate_booking_counts(route, months=24, seed=None):
    rng = np.random.default_rng(seed)
    t = np.arange(months)
    season = 300 * (1 + 0.4 * np.sin(2 * np.pi * t / 12))
    base = 500 + (hash(route) % 200)
    noise = rng.normal(0, 40, size=months)
    counts = np.maximum(0, base + season + noise).astype(int)
    dates = pd.date_range(end=pd.Timestamp.today(), periods=months, freq="M")
    return pd.DataFrame({"month": dates, "bookings": counts})

# --- LIVE AviationStack API ---
def get_live_flights(origin, destination, limit=10):
    if not AVIATIONSTACK_KEY:
        return {"error": "AVIATIONSTACK_KEY missing. Add it to .env or Streamlit Secrets."}

    url = "http://api.aviationstack.com/v1/flights"
    params = {
        "access_key": AVIATIONSTACK_KEY,
        "dep_iata": origin,
        "arr_iata": destination,
        "limit": limit
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

# ======================= APP UI ============================

st.title("Airline Booking Market Demand — Demo")
st.write("This dashboard shows route popularity, simulated market trends, and live flight data using AviationStack.")

with st.spinner("Loading OpenFlights dataset..."):
    airports, routes_raw = fetch_openflights()
    routes = prepare_routes(airports, routes_raw)

# --- Sidebar filters ---
st.sidebar.header("Filters")
top_n = st.sidebar.number_input("Top N routes", 5, 200, 20)
country_filter = st.sidebar.selectbox("Origin Country Filter", ["All"] + sorted(routes.SourceCountry.dropna().unique()))

routes_filtered = routes if country_filter == "All" else routes[routes.SourceCountry == country_filter]

# --- Route ranking ---
route_counts = (
    routes_filtered.groupby("route")
    .size()
    .reset_index(name="count")
    .sort_values("count", ascending=False)
)

st.header("Top Flight Routes")
st.dataframe(route_counts.head(top_n))

fig = px.bar(route_counts.head(top_n), x="route", y="count")
st.plotly_chart(fig, use_container_width=True)

# --- Route details ---
st.subheader("Route Details & Simulated Trends")

route_selected = st.selectbox("Pick a route", route_counts.head(200)["route"])

price_df = simulate_price_trend(route_selected, months=36, seed=42)
book_df = simulate_booking_counts(route_selected, months=36, seed=42)

col1, col2 = st.columns(2)

with col1:
    st.write("### Simulated Price Trend (36 Months)")
    fig = px.line(price_df, x="month", y="price")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.write("### Simulated Booking Trend (36 Months)")
    fig = px.line(book_df, x="month", y="bookings")
    st.plotly_chart(fig, use_container_width=True)

# ===================== LIVE FLIGHTS SECTION ======================

st.header("Live Flight Data (AviationStack API)")

try:
    r = routes[routes.route == route_selected].iloc[0]
    origin = r.SourceIATA
    destination = r.DestIATA
    st.write(f"Selected route: **{origin} → {destination}**")
except:
    origin = None
    destination = None

if origin and destination:
    if st.button("Get Live Flights"):
        with st.spinner("Fetching live flight data..."):
            flights = get_live_flights(origin, destination)

            if "error" in flights:
                st.error(flights["error"])
            else:
                data = flights.get("data", [])
                if not data:
                    st.info("No live flights found for this route. Try a busier one like SYD–MEL or LHR–CDG.")
                else:
                    df = pd.json_normalize(data)
                    cols = [
                        "airline.name",
                        "flight.number",
                        "flight.iata",
                        "departure.iata",
                        "arrival.iata",
                        "departure.scheduled",
                        "arrival.scheduled",
                        "flight_status"
                    ]
                    df = df[[c for c in cols if c in df.columns]]
                    st.dataframe(df)

# Footer
st.markdown("---")
st.caption("Powered by OpenFlights + AviationStack API. Built with Streamlit.")