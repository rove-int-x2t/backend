from serpapi import GoogleSearch

params = {
  "api_key": "99e63b8f8f72ce29dfa168d7d8cf959f9014720e1818335bb7beed57dc968736",
  "engine": "google_flights",
  "departure_id": "CHS",
  "arrival_id": "LAX",
  "hl": "en",
  "gl": "us",
  "currency": "USD",
  "outbound_date": "2025-06-27",
  "return_date": "2025-07-03",
  "stops": "2"
}

search = GoogleSearch(params)
results = search.get_dict()

for flight in results['best_flights']:
    print("********************")
    if 'layovers' in flight:
        print(flight['layovers'])
    print("********************")

for flight in results['other_flights']:
    print("********************")
    if 'layovers' in flight:
        print(flight['layovers'])
    print("********************")