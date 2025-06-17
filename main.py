from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("AMADEUS_API_KEY")
api_secret = os.getenv("AMADEUS_API_SECRET")

print("API Key:", api_key)
print("API Secret:", api_secret)