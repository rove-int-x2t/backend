from auth import generate_access_token
from db_utils import init_db, append_flight_data
from iso_convert import format_iso8601_duration
from concurrent.futures import ThreadPoolExecutor
import requests
from airlineUtils import get_airline_name


def contact_api(loopAmt, origin, destination):
    finalResult = []
    index = 0

    base_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {
        "Authorization": f"Bearer {generate_access_token()}",
        "Content-Type": "application/json"
    }

    while index < loopAmt:
        day = str(index + 1).zfill(2)
        search_params = {
            "originLocationCode": f"{origin}",
            "destinationLocationCode": f"{destination}",
            "departureDate": f"2025-10-{day}",
            "currencyCode": "USD",
            "adults": 1,
            "max": 3
        }

        response = requests.get(base_url, params=search_params, headers=headers)
        res = response.json()
        data = res.get("data", [])

        flights_to_insert = []
        for offer in data:
            # Get the first segment of the first itinerary
            segment = offer['itineraries'][0]['segments'][0]

            flight_data = {
                "flight_number": f"{segment['carrierCode']}{segment['number']}",
                "departure": f"{origin}",
                "arrival": f"{destination}",
                "date": segment['departure']['at'][:10],
                "raw_data": str(offer),  # optional: store full offer for reference
                "price": offer['price']['total'] + offer['price']['currency'],
                "airline": segment['carrierCode'],
                "flight_time": format_iso8601_duration(segment['duration'])
            }

            flights_to_insert.append({
                "flight_number": flight_data["flight_number"],
                "departure": flight_data["departure"],
                "arrival": flight_data["arrival"],
                "date": flight_data["date"],
                "data": flight_data["raw_data"],
                "price": flight_data["price"],
                "airline": flight_data["airline"],
                "flight_time": flight_data["flight_time"]
            })

        append_flight_data(flights_to_insert)  # 🔥 insert into DB
        finalResult.append(data)

        print(f"Inserted {len(flights_to_insert)} flights for 2025-10-{day}")
        index += 1

jobs = [
    (31, "JFK", "LAX"),
    (31, "JFK", "LHR"),
    (31, "LAX", "NRT"),
    (31, "YYZ", "FRA"),
    (31, "ORD", "DOH"),
]

# Use ThreadPoolExecutor to run them in parallel
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(contact_api, *job) for job in jobs]

    # Wait for all to finish (optional, but good for logging or catching errors)
    for future in futures:
        try:
            result = future.result()
        except Exception as e:
            print(f"Error in thread: {e}")
            
