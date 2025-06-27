import requests
import json
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import re
import math
from typing import List, Dict, Tuple, Optional
import itertools

class RewardsOptimizer:
    def __init__(self, serp_api_key: str):
        """
        Initialize the Rewards Optimizer with SerpApi key
        
        Args:
            serp_api_key (str): SerpApi API key for flight search
        """
        self.serp_api_key = serp_api_key
        self.base_url = "https://serpapi.com/search"
        
        # Miles valuations (cents per mile) - from The Points Guy and Upgraded Points
        self.miles_valuations = {
            'american_airlines': 1.7,  # AAdvantage
            'united_airlines': 1.2,    # MileagePlus
            'delta_airlines': 1.2,     # SkyMiles
            'southwest_airlines': 1.4,  # Rapid Rewards
            'jetblue': 1.3,            # TrueBlue
            'alaska_airlines': 1.6,    # Mileage Plan
            'british_airways': 1.4,    # Executive Club
            'air_canada': 1.3,         # Aeroplan
            'lufthansa': 1.2,          # Miles & More
            'emirates': 1.5,           # Skywards
            'qatar_airways': 1.4,      # Privilege Club
            'etihad_airways': 1.3,     # Etihad Guest
            'japan_airlines': 1.4,     # JAL Mileage Bank
            'ana': 1.3,                # ANA Mileage Club
            'default': 1.2             # Default valuation
        }
        
        # Award chart rates (miles required for different routes)
        self.award_charts = {
            'domestic_economy': {
                'short_haul': 7500,    # < 500 miles
                'medium_haul': 12500,  # 500-1150 miles
                'long_haul': 25000     # > 1150 miles
            },
            'international_economy': {
                'north_america': 25000,
                'europe': 30000,
                'asia': 35000,
                'south_america': 30000,
                'africa': 40000,
                'australia': 40000
            }
        }
        
        # Hotel redemption rates (points per dollar)
        self.hotel_redemption_rates = {
            'marriott': 0.8,   # 0.8 cents per point
            'hilton': 0.5,     # 0.5 cents per point
            'hyatt': 1.7,      # 1.7 cents per point
            'ihg': 0.6,        # 0.6 cents per point
            'default': 0.7     # Default hotel rate
        }
        
        # Gift card redemption rates (cents per point)
        self.gift_card_rates = {
            'amazon': 0.8,
            'target': 0.8,
            'walmart': 0.8,
            'starbucks': 0.8,
            'default': 0.8
        }

    def search_flights_serpapi(self, origin: str, destination: str, date: str, 
                              return_date: str = None, passengers: int = 1) -> List[Dict]:
        """
        Search for flights using SerpApi
        
        Args:
            origin (str): Origin airport code
            destination (str): Destination airport code
            date (str): Departure date (YYYY-MM-DD)
            return_date (str): Return date (YYYY-MM-DD)
            passengers (int): Number of passengers
            
        Returns:
            List[Dict]: List of flight options
        """
        params = {
            'api_key': self.serp_api_key,
            'engine': 'google_flights',
            'departure_id': origin,
            'arrival_id': destination,
            'outbound_date': date,
            'adults': passengers,
            'currency': 'USD',
            'hl': 'en'
        }
        
        if return_date:
            params['return_date'] = return_date
            
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            flights = []
            if 'flight_results' in data:
                for flight in data['flight_results']:
                    flight_info = {
                        'airline': flight.get('airline', 'Unknown'),
                        'departure_time': flight.get('departure_time', ''),
                        'arrival_time': flight.get('arrival_time', ''),
                        'duration': flight.get('duration', ''),
                        'price': flight.get('price', 0),
                        'stops': flight.get('stops', 0),
                        'flight_number': flight.get('flight_number', ''),
                        'origin': origin,
                        'destination': destination,
                        'date': date
                    }
                    flights.append(flight_info)
            
            return flights
            
        except Exception as e:
            print(f"Error searching flights: {e}")
            return []

    def calculate_distance(self, origin: str, destination: str) -> float:
        """
        Calculate approximate distance between airports using coordinates
        
        Args:
            origin (str): Origin airport code
            destination (str): Destination airport code
            
        Returns:
            float: Distance in miles
        """
        # Major airport coordinates (simplified)
        airport_coords = {
            'JFK': (40.6413, -73.7781),
            'LAX': (33.9416, -118.4085),
            'LHR': (51.4700, -0.4543),
            'NRT': (35.6762, 139.6503),
            'FRA': (50.0379, 8.5622),
            'DOH': (25.2730, 51.6081),
            'YYZ': (43.6777, -79.6248),
            'ORD': (41.9786, -87.9048),
            'SFO': (37.6213, -122.3790),
            'MIA': (25.7932, -80.2906),
            'ATL': (33.6407, -84.4277),
            'DFW': (32.8968, -97.0380),
            'DEN': (39.8561, -104.6737),
            'SEA': (47.4502, -122.3088),
            'BOS': (42.3656, -71.0096)
        }
        
        if origin in airport_coords and destination in airport_coords:
            lat1, lon1 = airport_coords[origin]
            lat2, lon2 = airport_coords[destination]
            
            # Haversine formula
            R = 3959  # Earth's radius in miles
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = (math.sin(dlat/2)**2 + 
                 math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
                 math.sin(dlon/2)**2)
            c = 2 * math.asin(math.sqrt(a))
            distance = R * c
            return distance
        
        return 1000  # Default distance if coordinates not found

    def calculate_flight_value_per_mile(self, flight: Dict, miles_required: int, 
                                      airline: str = 'default') -> Dict:
        """
        Calculate value per mile for a flight redemption
        
        Args:
            flight (Dict): Flight information
            miles_required (int): Miles required for redemption
            airline (str): Airline program
            
        Returns:
            Dict: Value calculation results
        """
        cash_price = float(flight.get('price', 0))
        taxes_fees = cash_price * 0.05  # Estimate 5% taxes and fees
        
        # Calculate value per mile
        value_per_mile = (cash_price - taxes_fees) / miles_required if miles_required > 0 else 0
        
        # Compare to published valuation
        published_valuation = self.miles_valuations.get(airline, self.miles_valuations['default'])
        
        # Calculate savings percentage
        savings_percentage = ((value_per_mile - published_valuation) / published_valuation) * 100
        
        return {
            'cash_price': cash_price,
            'taxes_fees': taxes_fees,
            'miles_required': miles_required,
            'value_per_mile': value_per_mile,
            'published_valuation': published_valuation,
            'savings_percentage': savings_percentage,
            'is_good_value': value_per_mile > published_valuation
        }

    def calculate_hotel_value_per_point(self, hotel_price: float, points_required: int, 
                                      hotel_program: str = 'default') -> Dict:
        """
        Calculate value per point for hotel redemption
        
        Args:
            hotel_price (float): Cash price of hotel
            points_required (int): Points required for redemption
            hotel_program (str): Hotel loyalty program
            
        Returns:
            Dict: Value calculation results
        """
        redemption_rate = self.hotel_redemption_rates.get(hotel_program, 
                                                         self.hotel_redemption_rates['default'])
        
        value_per_point = hotel_price / points_required if points_required > 0 else 0
        
        savings_percentage = ((value_per_point - redemption_rate) / redemption_rate) * 100
        
        return {
            'hotel_price': hotel_price,
            'points_required': points_required,
            'value_per_point': value_per_point,
            'redemption_rate': redemption_rate,
            'savings_percentage': savings_percentage,
            'is_good_value': value_per_point > redemption_rate
        }

    def calculate_gift_card_value(self, gift_card_value: float, points_required: int, 
                                gift_card_type: str = 'default') -> Dict:
        """
        Calculate value for gift card redemption
        
        Args:
            gift_card_value (float): Value of gift card
            points_required (int): Points required for redemption
            gift_card_type (str): Type of gift card
            
        Returns:
            Dict: Value calculation results
        """
        redemption_rate = self.gift_card_rates.get(gift_card_type, 
                                                  self.gift_card_rates['default'])
        
        value_per_point = gift_card_value / points_required if points_required > 0 else 0
        
        savings_percentage = ((value_per_point - redemption_rate) / redemption_rate) * 100
        
        return {
            'gift_card_value': gift_card_value,
            'points_required': points_required,
            'value_per_point': value_per_point,
            'redemption_rate': redemption_rate,
            'savings_percentage': savings_percentage,
            'is_good_value': value_per_point > redemption_rate
        }

    def find_synthetic_routes(self, origin: str, destination: str, date: str, 
                            max_layover_hours: int = 24) -> List[Dict]:
        """
        Find synthetic routing options (artificial layovers)
        
        Args:
            origin (str): Origin airport code
            destination (str): Destination airport code
            date (str): Departure date
            max_layover_hours (int): Maximum layover time in hours
            
        Returns:
            List[Dict]: List of synthetic routing options
        """
        # Major hub airports for layovers
        hub_airports = ['JFK', 'LAX', 'LHR', 'FRA', 'DOH', 'NRT', 'YYZ', 'ORD', 'SFO', 'MIA', 'ATL', 'DFW']
        
        synthetic_routes = []
        
        for hub in hub_airports:
            if hub != origin and hub != destination:
                # Search for first leg: origin to hub
                leg1_flights = self.search_flights_serpapi(origin, hub, date)
                
                # Search for second leg: hub to destination (next day)
                next_date = (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
                leg2_flights = self.search_flights_serpapi(hub, destination, next_date)
                
                if leg1_flights and leg2_flights:
                    for flight1 in leg1_flights[:3]:  # Top 3 options for first leg
                        for flight2 in leg2_flights[:3]:  # Top 3 options for second leg
                            total_price = float(flight1.get('price', 0)) + float(flight2.get('price', 0))
                            
                            # Calculate layover time
                            arrival1 = flight1.get('arrival_time', '')
                            departure2 = flight2.get('departure_time', '')
                            
                            if arrival1 and departure2:
                                try:
                                    # Simplified time calculation
                                    layover_hours = 12  # Default layover time
                                    
                                    if layover_hours <= max_layover_hours:
                                        route = {
                                            'origin': origin,
                                            'destination': destination,
                                            'layover_hub': hub,
                                            'leg1': flight1,
                                            'leg2': flight2,
                                            'total_price': total_price,
                                            'layover_hours': layover_hours,
                                            'total_duration': f"{flight1.get('duration', '')} + {flight2.get('duration', '')}",
                                            'total_stops': flight1.get('stops', 0) + flight2.get('stops', 0)
                                        }
                                        synthetic_routes.append(route)
                                except:
                                    continue
        
        # Sort by total price
        synthetic_routes.sort(key=lambda x: x['total_price'])
        return synthetic_routes

    def compare_redemption_options(self, origin: str, destination: str, date: str, 
                                 available_miles: int, available_points: int = 0) -> Dict:
        """
        Compare different redemption options and rank by value
        
        Args:
            origin (str): Origin airport code
            destination (str): Destination airport code
            date (str): Departure date
            available_miles (int): Available airline miles
            available_points (int): Available hotel points
            
        Returns:
            Dict: Comparison results with rankings
        """
        # Get direct flight options
        direct_flights = self.search_flights_serpapi(origin, destination, date)
        
        # Get synthetic routing options
        synthetic_routes = self.find_synthetic_routes(origin, destination, date)
        
        # Calculate distance for award chart lookup
        distance = self.calculate_distance(origin, destination)
        
        # Determine award chart category
        if distance < 500:
            award_category = 'short_haul'
        elif distance < 1150:
            award_category = 'medium_haul'
        else:
            award_category = 'long_haul'
        
        miles_required = self.award_charts['domestic_economy'][award_category]
        
        comparison_results = {
            'direct_flights': [],
            'synthetic_routes': [],
            'hotel_options': [],
            'gift_card_options': [],
            'recommendations': []
        }
        
        # Analyze direct flights
        for flight in direct_flights[:5]:  # Top 5 options
            if available_miles >= miles_required:
                value_calc = self.calculate_flight_value_per_mile(flight, miles_required)
                flight_analysis = {
                    'flight': flight,
                    'miles_required': miles_required,
                    'value_calculation': value_calc,
                    'redemption_type': 'direct_flight'
                }
                comparison_results['direct_flights'].append(flight_analysis)
        
        # Analyze synthetic routes
        for route in synthetic_routes[:5]:  # Top 5 options
            total_miles_required = miles_required * 2  # Two separate awards
            if available_miles >= total_miles_required:
                value_calc = self.calculate_flight_value_per_mile(
                    {'price': route['total_price']}, total_miles_required
                )
                route_analysis = {
                    'route': route,
                    'miles_required': total_miles_required,
                    'value_calculation': value_calc,
                    'redemption_type': 'synthetic_route'
                }
                comparison_results['synthetic_routes'].append(route_analysis)
        
        # Analyze hotel options (if points available)
        if available_points > 0:
            # Example hotel options
            hotel_options = [
                {'name': 'Marriott Hotel', 'price': 200, 'points_required': 25000},
                {'name': 'Hilton Hotel', 'price': 180, 'points_required': 36000},
                {'name': 'Hyatt Hotel', 'price': 220, 'points_required': 13000}
            ]
            
            for hotel in hotel_options:
                if available_points >= hotel['points_required']:
                    value_calc = self.calculate_hotel_value_per_point(
                        hotel['price'], hotel['points_required']
                    )
                    hotel_analysis = {
                        'hotel': hotel,
                        'value_calculation': value_calc,
                        'redemption_type': 'hotel'
                    }
                    comparison_results['hotel_options'].append(hotel_analysis)
        
        # Analyze gift card options
        gift_card_options = [
            {'name': 'Amazon Gift Card', 'value': 100, 'points_required': 12500},
            {'name': 'Target Gift Card', 'value': 100, 'points_required': 12500},
            {'name': 'Starbucks Gift Card', 'value': 50, 'points_required': 6250}
        ]
        
        for gift_card in gift_card_options:
            if available_miles >= gift_card['points_required']:
                value_calc = self.calculate_gift_card_value(
                    gift_card['value'], gift_card['points_required']
                )
                gift_card_analysis = {
                    'gift_card': gift_card,
                    'value_calculation': value_calc,
                    'redemption_type': 'gift_card'
                }
                comparison_results['gift_card_options'].append(gift_card_analysis)
        
        # Generate recommendations
        all_options = []
        all_options.extend(comparison_results['direct_flights'])
        all_options.extend(comparison_results['synthetic_routes'])
        all_options.extend(comparison_results['hotel_options'])
        all_options.extend(comparison_results['gift_card_options'])
        
        # Sort by value per mile/point
        all_options.sort(key=lambda x: x['value_calculation']['value_per_mile'], reverse=True)
        
        comparison_results['recommendations'] = all_options[:10]  # Top 10 recommendations
        
        return comparison_results

    def get_optimal_redemption(self, origin: str, destination: str, date: str, 
                             available_miles: int, available_points: int = 0, 
                             preference: str = 'maximize_value') -> Dict:
        """
        Get the optimal redemption recommendation
        
        Args:
            origin (str): Origin airport code
            destination (str): Destination airport code
            date (str): Departure date
            available_miles (int): Available airline miles
            available_points (int): Available hotel points
            preference (str): User preference ('maximize_value', 'minimize_fees', 'direct_only')
            
        Returns:
            Dict: Optimal redemption recommendation
        """
        comparison = self.compare_redemption_options(origin, destination, date, 
                                                   available_miles, available_points)
        
        if not comparison['recommendations']:
            return {
                'error': 'No suitable redemption options found',
                'suggestion': 'Consider saving miles for a better opportunity'
            }
        
        if preference == 'maximize_value':
            # Return the option with highest value per mile/point
            optimal = comparison['recommendations'][0]
        elif preference == 'minimize_fees':
            # Filter by lowest taxes/fees
            options_with_fees = [opt for opt in comparison['recommendations'] 
                               if 'value_calculation' in opt and 'taxes_fees' in opt['value_calculation']]
            if options_with_fees:
                optimal = min(options_with_fees, key=lambda x: x['value_calculation']['taxes_fees'])
            else:
                optimal = comparison['recommendations'][0]
        elif preference == 'direct_only':
            # Only consider direct flights
            direct_options = [opt for opt in comparison['recommendations'] 
                            if opt['redemption_type'] == 'direct_flight']
            optimal = direct_options[0] if direct_options else comparison['recommendations'][0]
        else:
            optimal = comparison['recommendations'][0]
        
        return {
            'optimal_redemption': optimal,
            'all_options': comparison['recommendations'],
            'summary': {
                'total_options_analyzed': len(comparison['recommendations']),
                'best_value_per_mile': optimal['value_calculation']['value_per_mile'],
                'savings_percentage': optimal['value_calculation']['savings_percentage'],
                'is_good_value': optimal['value_calculation']['is_good_value']
            }
        } 