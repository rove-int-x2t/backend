from serpapi import GoogleSearch
import json
from datetime import datetime
import math
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("SERPAPI_SECRET")

class FlightComparator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.results = {
            'direct_flights': [],
            'layover_flights': [],
            'comparison': {}
        }
        # Airport coordinates for distance calculation (lat, lon)
        self.airport_coords = {
            'CHS': (32.8986, -80.0405),  # Charleston
            'LGA': (40.7769, -73.8740),  # LaGuardia
            'ATL': (33.6407, -84.4277),  # Atlanta
            'CLT': (35.2144, -80.9473),  # Charlotte
            'DFW': (32.8998, -97.0403),  # Dallas
            'ORD': (41.9742, -87.9073),  # Chicago O'Hare
            'LAX': (33.9425, -118.4081), # Los Angeles
            'JFK': (40.6413, -73.7781),  # JFK
            'MIA': (25.7959, -80.2870),  # Miami
            'BOS': (42.3656, -71.0096),  # Boston
            # Add more airports as needed
        }
    
    def calculate_distance(self, airport1, airport2):
        """
        Calculate the great circle distance between two airports using Haversine formula
        Returns distance in miles
        """
        if airport1 not in self.airport_coords or airport2 not in self.airport_coords:
            return None
        
        lat1, lon1 = self.airport_coords[airport1]
        lat2, lon2 = self.airport_coords[airport2]
        
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in miles
        r = 3956
        
        return c * r
    
    def calculate_value_per_mile(self, price, distance):
        """
        Calculate the cost per mile for a flight
        """
        if distance and distance > 0 and isinstance(price, (int, float)):
            return price / distance
        return None
    
    def search_flights(self, departure_id, arrival_id, outbound_date, return_date=None, stops=None):
        """
        Search for flights with specified parameters
        """
        params = {
            "api_key": self.api_key,
            "engine": "google_flights",
            "departure_id": departure_id,
            "arrival_id": arrival_id,
            "hl": "en",
            "gl": "us",
            "currency": "USD",
            "outbound_date": outbound_date,
        }
        
        if return_date:
            params["return_date"] = return_date
        
        if stops is not None:
            params["stops"] = str(stops)
        
        print(f"🔍 Searching flights from {departure_id} to {arrival_id}")
        print(f"   Outbound: {outbound_date}")
        if return_date:
            print(f"   Return: {return_date}")
        print(f"   Stops: {'Direct flights only' if stops == 0 else f'Up to {stops} stops' if stops else 'Any number of stops'}")
        print("-" * 60)
        
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            return results
        except Exception as e:
            print(f"❌ Error searching flights: {e}")
            return None
    
    def extract_flight_info(self, flight, departure_id, arrival_id):
        """
        Extract relevant information from flight data including value per mile
        """
        flight_info = {
            'price': flight.get('price', 'N/A'),
            'airline': flight.get('flights', [{}])[0].get('airline', 'Unknown'),
            'duration': flight.get('total_duration', 'N/A'),
            'departure_time': flight.get('flights', [{}])[0].get('departure_airport', {}).get('time', 'N/A'),
            'arrival_time': flight.get('flights', [{}])[-1].get('arrival_airport', {}).get('time', 'N/A'),
            'layovers': len(flight.get('layovers', [])),
            'layover_details': [],
            'distance_miles': None,
            'cost_per_mile': None
        }
        
        # Calculate distance and cost per mile
        distance = self.calculate_distance(departure_id, arrival_id)
        if distance:
            flight_info['distance_miles'] = round(distance, 0)
            if isinstance(flight_info['price'], (int, float)):
                cost_per_mile = self.calculate_value_per_mile(flight_info['price'], distance)
                if cost_per_mile:
                    flight_info['cost_per_mile'] = round(cost_per_mile, 3)
        
        # Extract layover information
        if 'layovers' in flight:
            for layover in flight['layovers']:
                layover_info = {
                    'airport': layover.get('name', 'Unknown'),
                    'duration': layover.get('duration', 'N/A')
                }
                flight_info['layover_details'].append(layover_info)
        
        return flight_info
    
    def display_flight_details(self, flight_info, flight_type):
        """
        Display detailed flight information including value per mile
        """
        print(f"✈️  {flight_type.upper()} FLIGHT")
        print(f"   💰 Price: ${flight_info['price']}")
        print(f"   🏢 Airline: {flight_info['airline']}")
        print(f"   ⏱️  Duration: {flight_info['duration']}")
        print(f"   🛫 Departure: {flight_info['departure_time']}")
        print(f"   🛬 Arrival: {flight_info['arrival_time']}")
        print(f"   🔄 Layovers: {flight_info['layovers']}")
        
        # Display distance and cost per mile
        if flight_info['distance_miles']:
            print(f"   📏 Distance: {flight_info['distance_miles']:.0f} miles")
        if flight_info['cost_per_mile']:
            print(f"   💵 Cost per mile: ${flight_info['cost_per_mile']:.3f}")
        
        if flight_info['layover_details']:
            print("   📍 Layover Details:")
            for i, layover in enumerate(flight_info['layover_details'], 1):
                print(f"      {i}. {layover['airport']} ({layover['duration']})")
        
        print("*" * 60)
    
    def compare_routes(self, departure_id, arrival_id, outbound_date, return_date=None):
        """
        Compare direct flights vs flights with layovers for the same route
        """
        print("🚀 FLIGHT PRICE COMPARISON ALGORITHM")
        print("=" * 60)
        print(f"Route: {departure_id} → {arrival_id}")
        print(f"Travel Date(s): {outbound_date}" + (f" to {return_date}" if return_date else ""))
        print("=" * 60)
        
        # Search for direct flights (0 stops)
        print("\n📡 SEARCHING DIRECT FLIGHTS...")
        direct_results = self.search_flights(departure_id, arrival_id, outbound_date, return_date, stops=0)
        
        # Search for flights with layovers (up to 2 stops)
        print("\n📡 SEARCHING FLIGHTS WITH LAYOVERS...")
        layover_results = self.search_flights(departure_id, arrival_id, outbound_date, return_date, stops=2)
        
        # Process direct flights
        direct_count = 0
        if direct_results:
            # Count and process best direct flights
            for flight in direct_results.get('best_flights', []):
                if flight.get('layovers') is None or len(flight.get('layovers', [])) == 0:
                    flight_info = self.extract_flight_info(flight, departure_id, arrival_id)
                    self.results['direct_flights'].append(flight_info)
                    direct_count += 1
            
            # Count and process other direct flights
            for flight in direct_results.get('other_flights', []):
                if flight.get('layovers') is None or len(flight.get('layovers', [])) == 0:
                    flight_info = self.extract_flight_info(flight, departure_id, arrival_id)
                    self.results['direct_flights'].append(flight_info)
                    direct_count += 1
            
            if direct_count > 0:
                print(f"\n🎯 DIRECT FLIGHTS FOUND: {direct_count}")
                print("-" * 40)
                
                for flight_info in self.results['direct_flights']:
                    self.display_flight_details(flight_info, "DIRECT")
            else:
                print(f"\n🎯 NO DIRECT FLIGHTS FOUND")
                print("-" * 40)
        
        # Process flights with layovers
        layover_count = 0
        if layover_results:
            # Count and process best flights with layovers
            for flight in layover_results.get('best_flights', []):
                if 'layovers' in flight and len(flight['layovers']) > 0:
                    flight_info = self.extract_flight_info(flight, departure_id, arrival_id)
                    self.results['layover_flights'].append(flight_info)
                    layover_count += 1
            
            # Count and process other flights with layovers
            for flight in layover_results.get('other_flights', []):
                if 'layovers' in flight and len(flight['layovers']) > 0:
                    flight_info = self.extract_flight_info(flight, departure_id, arrival_id)
                    self.results['layover_flights'].append(flight_info)
                    layover_count += 1
            
            if layover_count > 0:
                print(f"\n🔄 FLIGHTS WITH LAYOVERS FOUND: {layover_count}")
                print("-" * 40)
                
                for flight_info in self.results['layover_flights']:
                    self.display_flight_details(flight_info, "LAYOVER")
            else:
                print(f"\n🔄 NO FLIGHTS WITH LAYOVERS FOUND")
                print("-" * 40)
        
        # Perform comparison analysis
        self.analyze_and_recommend()
    
    def analyze_and_recommend(self):
        """
        Analyze prices and provide recommendations
        """
        print("\n📊 PRICE ANALYSIS & RECOMMENDATIONS")
        print("=" * 60)
        
        if not self.results['direct_flights'] and not self.results['layover_flights']:
            print("❌ No flights found for comparison.")
            return
        
        # Find cheapest flights in each category
        cheapest_direct = None
        cheapest_layover = None
        
        if self.results['direct_flights']:
            cheapest_direct = min(self.results['direct_flights'], 
                                key=lambda x: float(x['price']) if isinstance(x['price'], (int, float, str)) and str(x['price']).replace('.','').isdigit() else float('inf'))
        
        if self.results['layover_flights']:
            cheapest_layover = min(self.results['layover_flights'], 
                                 key=lambda x: float(x['price']) if isinstance(x['price'], (int, float, str)) and str(x['price']).replace('.','').isdigit() else float('inf'))
        
        # Overall cheapest flight
        all_flights = self.results['direct_flights'] + self.results['layover_flights']
        if all_flights:
            overall_cheapest = min(all_flights, 
                                 key=lambda x: float(x['price']) if isinstance(x['price'], (int, float, str)) and str(x['price']).replace('.','').isdigit() else float('inf'))
        
        # Display analysis
        print(f"\n📈 DIRECT FLIGHTS: {len(self.results['direct_flights'])} found")
        if cheapest_direct:
            print(f"   💰 Cheapest Direct: ${cheapest_direct['price']} ({cheapest_direct['airline']})")
            print(f"   ⏱️  Duration: {cheapest_direct['duration']}")
            if cheapest_direct['cost_per_mile']:
                print(f"   💵 Cost per mile: ${cheapest_direct['cost_per_mile']:.3f}")
        
        print(f"\n📈 LAYOVER FLIGHTS: {len(self.results['layover_flights'])} found")
        if cheapest_layover:
            print(f"   💰 Cheapest Layover: ${cheapest_layover['price']} ({cheapest_layover['airline']})")
            print(f"   ⏱️  Duration: {cheapest_layover['duration']}")
            print(f"   🔄 Stops: {cheapest_layover['layovers']}")
            if cheapest_layover['cost_per_mile']:
                print(f"   💵 Cost per mile: ${cheapest_layover['cost_per_mile']:.3f}")
        
        # Find best value per mile
        all_flights_with_cost_per_mile = [f for f in all_flights if f['cost_per_mile'] is not None]
        if all_flights_with_cost_per_mile:
            best_value = min(all_flights_with_cost_per_mile, key=lambda x: x['cost_per_mile'])
            print(f"\n💎 BEST VALUE PER MILE:")
            print(f"   💵 ${best_value['cost_per_mile']:.3f}/mile - {best_value['airline']}")
            print(f"   💰 Total Price: ${best_value['price']}")
            print(f"   🔄 {'Direct' if best_value['layovers'] == 0 else str(best_value['layovers']) + ' stop(s)'}")
        
        # Comparison and recommendation
        print(f"\n🏆 RECOMMENDATION:")
        print("-" * 30)
        
        if cheapest_direct and cheapest_layover:
            direct_price = float(cheapest_direct['price'])
            layover_price = float(cheapest_layover['price'])
            savings = abs(direct_price - layover_price)
            
            if direct_price < layover_price:
                print(f"✅ CHOOSE DIRECT FLIGHT")
                print(f"   💰 Price: ${cheapest_direct['price']}")
                print(f"   💡 You save ${savings:.2f} and time with direct flight")
            elif layover_price < direct_price:
                print(f"✅ CHOOSE LAYOVER FLIGHT")
                print(f"   💰 Price: ${cheapest_layover['price']}")
                print(f"   💡 You save ${savings:.2f} (but spend more time traveling)")
                print(f"   ⚠️  Trade-off: {cheapest_layover['layovers']} stop(s)")
            else:
                print(f"⚖️  PRICES ARE EQUAL")
                print(f"   💡 Choose direct flight for convenience")
        
        elif cheapest_direct:
            print(f"✅ ONLY DIRECT FLIGHTS AVAILABLE")
            print(f"   💰 Price: ${cheapest_direct['price']}")
        
        elif cheapest_layover:
            print(f"✅ ONLY LAYOVER FLIGHTS AVAILABLE")
            print(f"   💰 Price: ${cheapest_layover['price']}")
        
        # Overall best deal
        if all_flights:
            print(f"\n🎯 ABSOLUTE BEST DEAL:")
            print(f"   💰 ${overall_cheapest['price']} - {overall_cheapest['airline']}")
            print(f"   🔄 {'Direct' if overall_cheapest['layovers'] == 0 else str(overall_cheapest['layovers']) + ' stop(s)'}")
            print(f"   ⏱️  {overall_cheapest['duration']}")

# Usage Example
if __name__ == "__main__":
    # Initialize the comparator with your API key
    API_KEY = api_key
    comparator = FlightComparator(API_KEY)
    
    # Compare flights for your route
    comparator.compare_routes(
        departure_id="CHS",  # Charleston
        arrival_id="LAX",    # LaGuardia
        outbound_date="2025-12-27",
        return_date="2026-01-03"
    )
    
    print(f"\n📋 SUMMARY STATISTICS:")
    print(f"   Direct flights analyzed: {len(comparator.results['direct_flights'])}")
    print(f"   Layover flights analyzed: {len(comparator.results['layover_flights'])}")
    print(f"   Total flights compared: {len(comparator.results['direct_flights']) + len(comparator.results['layover_flights'])}")