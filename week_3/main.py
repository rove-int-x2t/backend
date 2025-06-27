import csv

def value_per_mile(cash_price, miles_cost):
    """
    Calculate value per mile for a redemption.
    Returns value in cents per mile.
    """
    if miles_cost == 0:
        return 0
    value = ((cash_price -(0.85 * cash_price) ) / miles_cost) * 100
    return round(value, 2)

def load_flights(csv_path):
    """
    Load flights from a CSV file.
    Returns a list of dicts.
    """
    flights = []
    with open(csv_path, newline='', encoding='utf8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            flights.append(row)
    return flights

def find_synthetic_routes(flights, origin, destination, date):
    """
    Find synthetic (layover) routes between origin and destination.
    Returns a list of route options (direct and layover).
    """
    # Direct flights
    direct = [f for f in flights if f['departure'] == origin and f['arrival'] == destination and f['date'] == date]
    # Layover flights
    layovers = []
    for f1 in flights:
        if f1['departure'] == origin and f1['date'] == date:
            for f2 in flights:
                if (f2['departure'] == f1['arrival'] and
                    f2['arrival'] == destination and
                    f2['date'] == date):
                    layovers.append((f1, f2))
    return direct, layovers

def recommend_routes(origin, destination, date, miles_balance, flights):
    """
    Recommend optimal redemptions.
    """
    direct, layovers = find_synthetic_routes(flights, origin, destination, date)
    recommendations = []

    # Example: Assume 1 mile = 1 cent for now, and no taxes/fees
    for f in direct:
        price = float(f['price'].replace('USD',''))
        miles = price * 100  # Example: 1 cent per mile
        vpm = value_per_mile(price, miles)
        recommendations.append({
            'type': 'direct',
            'flights': [f],
            'total_price': price,
            'total_miles': miles,
            'value_per_mile': vpm
        })

    for f1, f2 in layovers:
        price = float(f1['price'].replace('USD','')) + float(f2['price'].replace('USD',''))
        miles = price * 100
        vpm = value_per_mile(price, miles)
        recommendations.append({
            'type': 'layover',
            'flights': [f1, f2],
            'total_price': price,
            'total_miles': miles,
            'value_per_mile': vpm
        })

    # Sort by value per mile, descending
    recommendations.sort(key=lambda x: x['value_per_mile'], reverse=True)
    return recommendations

if __name__ == "__main__":
    flights = load_flights("../week_2/flights.csv")
    origin = "JFK"
    destination = "LAX"
    date = "2025-10-01"
    miles_balance = 50000

    recs = recommend_routes(origin, destination, date, miles_balance, flights)
    for rec in recs[:5]:
        print(f"Type: {rec['type']}, Value per mile: {rec['value_per_mile']} cpm, Price: {rec['total_price']}, Flights: {[f['flight_number'] for f in rec['flights']]}")