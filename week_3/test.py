import requests
from typing import List, Dict, Optional

SERPAPI_KEY = "99e63b8f8f72ce29dfa168d7d8cf959f9014720e1818335bb7beed57dc968736"
GOOGLE_FLIGHTS_ENDPOINT = "https://serpapi.com/search.json"

# --- 1. Value-per-mile calculator ---
def calculate_value_per_mile(cash_price: float, miles_required: int, fees: float = 0) -> float:
    net_cash = max(cash_price - fees, 0)
    if miles_required <= 0:
        return 0.0
    return round((net_cash / miles_required) * 100, 2)  # cents per mile

# --- 2. SerpApi Google Flights search ---
def search_flights(origin: str, destination: str, date: str) -> Optional[List[Dict]]:
    """
    Query SerpApi Google Flights API for flights on a given date.
    Returns list of flights or None.
    """
    params = {
        "engine": "google_flights",
        "q": f"{origin} to {destination} {date}",
        "api_key": SERPAPI_KEY,
        "no_cache": "true"
    }
    response = requests.get(GOOGLE_FLIGHTS_ENDPOINT, params=params)
    if response.status_code != 200:
        print(f"SerpApi request failed: {response.status_code}")
        return None
    data = response.json()
    if data.get("search_metadata", {}).get("status") != "Success":
        print("Flight search was not successful.")
        return None
    # Extract flight options from 'best_flights' or 'flights_results'
    flights = data.get("best_flights") or data.get("flights_results")
    return flights

# --- 3. Synthetic routing logic ---
def find_synthetic_routes(origin: str, destination: str, date: str, miles_available: int) -> List[Dict]:
    """
    Find synthetic routes by checking flights via popular layover airports.
    """
    # Step 1: Get direct flights
    direct_flights = search_flights(origin, destination, date)
    if not direct_flights:
        direct_min_price = float('inf')
    else:
        direct_min_price = min(flight.get("price", {}).get("raw", float('inf')) for flight in direct_flights)

    # Example layovers for demo (in real use, dynamically determine)
    layovers = ["AMS", "CDG", "FRA", "DXB", "ORD"]

    synthetic_options = []

    for layover in layovers:
        if layover in (origin, destination):
            continue
        flights_to_layover = search_flights(origin, layover, date)
        flights_from_layover = search_flights(layover, destination, date)
        if not flights_to_layover or not flights_from_layover:
            continue

        cheapest_to_layover = min(flights_to_layover, key=lambda f: f.get("price", {}).get("raw", float('inf')))
        cheapest_from_layover = min(flights_from_layover, key=lambda f: f.get("price", {}).get("raw", float('inf')))

        total_price = cheapest_to_layover.get("price", {}).get("raw", 0) + cheapest_from_layover.get("price", {}).get("raw", 0)

        # Estimate miles from distance or use a fixed approximation (SerpApi may not provide mileage directly)
        # Here we approximate miles as sum of flight distances if available, else None
        dist1 = cheapest_to_layover.get("distance_miles")
        dist2 = cheapest_from_layover.get("distance_miles")
        total_miles = (dist1 or 0) + (dist2 or 0)

        if total_price < direct_min_price:
            savings = direct_min_price - total_price
            value_per_mile = calculate_value_per_mile(total_price, int(total_miles))
            synthetic_options.append({
                "route": [origin, layover, destination],
                "total_price": total_price,
                "total_miles": int(total_miles),
                "savings": round(savings, 2),
                "value_per_mile": value_per_mile,
                "redemption_type": "flight"
            })

    synthetic_options.sort(key=lambda x: x["savings"], reverse=True)
    return synthetic_options

# --- 4. Redemption recommendations ---
def recommend_redemptions(origin: str, destination: str, date: str, miles_available: int,
                          redemption_rates: Dict[str, float], fees: Dict[str, float]) -> List[Dict]:
    # Flights synthetic routing options
    flight_options = find_synthetic_routes(origin, destination, date, miles_available)

    # Example hotel/gift card static options
    hotel_cash = 200
    hotel_miles = int(hotel_cash / redemption_rates.get("hotel", 0.8))
    hotel_value = calculate_value_per_mile(hotel_cash, hotel_miles, fees.get("hotel", 0))

    gift_card_cash = 100
    gift_card_miles = int(gift_card_cash / redemption_rates.get("gift_card", 0.5))
    gift_card_value = calculate_value_per_mile(gift_card_cash, gift_card_miles, fees.get("gift_card", 0))

    hotel_option = {
        "route": ["hotel booking"],
        "total_price": hotel_cash,
        "total_miles": hotel_miles,
        "value_per_mile": hotel_value,
        "redemption_type": "hotel"
    }
    gift_card_option = {
        "route": ["gift card"],
        "total_price": gift_card_cash,
        "total_miles": gift_card_miles,
        "value_per_mile": gift_card_value,
        "redemption_type": "gift_card"
    }

    all_options = flight_options + [hotel_option, gift_card_option]

    affordable = [opt for opt in all_options if opt["total_miles"] <= miles_available]
    affordable.sort(key=lambda x: x["value_per_mile"], reverse=True)
    return affordable

# --- 5. Example run ---
if __name__ == "__main__":
    origin = "LHR"
    destination = "JFK"
    travel_date = "2024-10-02"
    user_miles = 50000

    redemption_rates = {
        "flight": 1.2,
        "hotel": 0.8,
        "gift_card": 0.5
    }
    fees = {
        "flight": 50,
        "hotel": 20,
        "gift_card": 0
    }

    recs = recommend_redemptions(origin, destination, travel_date, user_miles, redemption_rates, fees)

    print(f"Top redemption recommendations for {user_miles} miles from {origin} to {destination} on {travel_date}:\n")
    for i, r in enumerate(recs[:5], 1):
        print(f"{i}. Type: {r['redemption_type'].capitalize()}")
        print(f"   Route: {' -> '.join(r['route'])}")
        print(f"   Price (USD): ${r['total_price']}")
        print(f"   Miles Required: {r['total_miles']}")
        print(f"   Value per Mile: {r['value_per_mile']} cents")
        if r.get("savings"):
            print(f"   Savings vs direct: ${r['savings']}")
        print()
