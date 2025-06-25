import requests
from auth import generate_access_token

access_token = generate_access_token()

def get_airline_name(iata_code):
    """
    Looks up the airline name for a given IATA code using Amadeus API.
    """
    url = "https://test.api.amadeus.com/v1/reference-data/airlines"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "airlineCodes": iata_code
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json().get("data", [])
        if data:
            return data[0].get("businessName") or data[0].get("commonName") or data[0].get("name")
        else:
            return None
    else:
        print("Error:", response.text)
        return None
