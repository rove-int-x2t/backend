from dotenv import load_dotenv
import os
import requests
load_dotenv()

api_key = os.getenv("AMADEUS_API_KEY")
api_secret = os.getenv("AMADEUS_API_SECRET")

print("API Key:", api_key)
print("API Secret:", api_secret)

def generate_access_token():
    base_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": api_secret
    }

    response = requests.post(base_url, headers=headers, data=data)

    if response.status_code == 200:
        access_token = response.json().get("access_token")
        print("Access Token:", access_token)
        return access_token
    else:
        print("Error generating access token:", response.text)
        return None

def contact_api(loopAmt): 
    finalResult = []
    index = 0

    base_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {
        "Authorization": f"Bearer {generate_access_token()}",
        "Content-Type": "application/json"
    }
    # do not change the search parameters except origin destination & depart!
    while index < loopAmt:
        search_params = {
        "originLocationCode": "NYC",
        "destinationLocationCode": "CHS",
        # 2025 x index thru loopAmt
        "departureDate": f"2025-10-{str(loopAmt).zfill(2)}",
        # these two are required.
        "adults": 1,
        "max": 3
        }

        response = requests.get(base_url, params=search_params, headers=headers)

        index += 1
        res = response.json()
        finalResult.append(res)
        print(f"Response {index}: {res['data'][0]['itineraries'][0]['segments'][0]['carrierCode']}")
#Code is able to return flight data for one day for x amount of results
contact_api(1)