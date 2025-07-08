import streamlit as st
import sqlite3
import re
import datetime

st.set_page_config(page_title="Rewards Redemption Optimizer", layout="centered")
st.title("✈️ Rewards Redemption Optimizer")
st.write("Find the best value for your airline miles or points!")

# --- Helper functions ---
def parse_price(price_str):
    match = re.match(r"([0-9.]+)", price_str)
    return float(match.group(1)) if match else None

def get_flights(departure, arrival, start_date, end_date):
    conn = sqlite3.connect("../week_2/database.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT flight_number, departure, arrival, date, price, airline, flight_time, airline_full_name
        FROM flights
        WHERE departure = ? AND arrival = ? AND date BETWEEN ? AND ?
        ORDER BY date ASC
        """,
        (departure, arrival, start_date, end_date)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- UI Inputs ---
st.header("1. Enter Your Travel Details")
col1, col2 = st.columns(2)
with col1:
    departure = st.text_input("Departure Airport Code", "JFK")
    arrival = st.text_input("Destination Airport Code", "LAX")
    miles = st.number_input("Miles/Points to Redeem", min_value=1, value=25000, step=1000)
with col2:
    start_date = st.date_input("Start Date", datetime.date(2025, 10, 1))
    end_date = st.date_input("End Date", datetime.date(2025, 10, 7))

# --- Filters ---
st.header("2. Preferences & Filters")
col3, col4 = st.columns(2)
with col3:
    maximize_value = st.checkbox("Maximize Value (¢/mile)", value=True)
    minimize_fees = st.checkbox("Minimize Fees", value=False)
with col4:
    direct_flights = st.checkbox("Direct Flights Only", value=False)
    show_chart = st.checkbox("Show Comparison Chart", value=True)

# --- Results ---
st.header("3. Best Redemption Options")
if st.button("Find Redemptions"):
    flights = get_flights(departure.upper(), arrival.upper(), str(start_date), str(end_date))
    if not flights:
        st.warning("No flights found for your criteria.")
    else:
        results = []
        for f in flights:
            price = parse_price(f[4])
            vpm = round((price * 100) / miles, 2)  # cents per mile
            results.append({
                "flight_number": f[0],
                "departure": f[1],
                "arrival": f[2],
                "date": f[3],
                "price": price,
                "airline": f[5],
                "flight_time": f[6],
                "airline_full_name": f[7],
                "value_per_mile": vpm
            })
        # Apply filters
        if maximize_value:
            results = sorted(results, key=lambda x: -x["value_per_mile"])
        else:
            results = sorted(results, key=lambda x: x["price"])
        # Display
        st.write(f"Showing {len(results)} options:")
        for r in results[:10]:
            st.markdown(f"**{r['flight_number']}** | {r['airline_full_name']} | {r['date']} | {r['flight_time']}")
            st.write(f"Price: ${r['price']:.2f} | Value: {r['value_per_mile']}¢/mile | From {r['departure']} to {r['arrival']}")
            st.write("---")
        if show_chart:
            st.subheader("Comparison Chart (¢/mile)")
            st.bar_chart({r['flight_number']: r['value_per_mile'] for r in results[:10]})
        st.success("Done! Adjust your filters or dates for more options.")

st.caption("Built for travelers who want to get the most out of their points and miles.")
