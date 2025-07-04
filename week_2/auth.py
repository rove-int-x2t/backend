import requests
import os
from dotenv import load_dotenv

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