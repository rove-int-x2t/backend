# Rewards Redemption Optimizer

A Streamlit web application that helps travelers find the best value for their airline miles or points by analyzing flight data and calculating redemption values.

## Overview

The Rewards Redemption Optimizer is designed to help travelers maximize the value of their airline miles and points. It analyzes available flights from a SQLite database and calculates the cents-per-mile value for each redemption option, allowing users to make informed decisions about their travel bookings.

## Features

### Core Functionality

- **Flight Search**: Search for flights between departure and arrival airports within specified date ranges
- **Value Calculation**: Automatically calculates cents-per-mile value for each flight option
- **Smart Filtering**: Multiple filtering options to customize search results
- **Visual Comparison**: Interactive charts to compare redemption values

### Search & Filter Options

- **Airport Codes**: Enter departure and destination airport codes (e.g., JFK, LAX)
- **Date Range**: Flexible date selection for travel planning
- **Miles/Points**: Specify the amount of miles or points you want to redeem
- **Value Maximization**: Option to prioritize flights with the highest cents-per-mile value
- **Direct Flights**: Filter for non-stop flights only
- **Fee Minimization**: Option to prioritize flights with lower fees

### Results Display

- **Ranked Results**: Flights sorted by value or price based on preferences
- **Detailed Information**: Flight number, airline, date, time, price, and value metrics
- **Comparison Charts**: Visual bar charts showing cents-per-mile values
- **Top 10 Options**: Displays the best redemption opportunities

## Technical Stack

- **Frontend**: Streamlit (Python web framework)
- **Database**: SQLite (flight data storage)
- **Data Processing**: Python with regex parsing
- **Visualization**: Streamlit's built-in charting capabilities

## Prerequisites

Before running the application, ensure you have:

1. **Python 3.7+** installed on your system
2. **Flight Database**: The application expects a SQLite database at `../week_2/database.db` containing flight information
3. **Required Python Packages**: Install the dependencies listed below

## Installation & Setup

### 1. Install Dependencies

```bash
pip install streamlit
```

### 2. Database Setup

Ensure you have the flight database file at `../week_2/database.db` with the following schema:

```sql
CREATE TABLE flights (
    flight_number TEXT,
    departure TEXT,
    arrival TEXT,
    date TEXT,
    price TEXT,
    airline TEXT,
    flight_time TEXT,
    airline_full_name TEXT
);
```

### 3. Run the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

## Usage Guide

### Step 1: Enter Travel Details

- **Departure Airport Code**: Enter the 3-letter airport code (e.g., JFK, LAX, ORD)
- **Destination Airport Code**: Enter the 3-letter airport code for your destination
- **Miles/Points to Redeem**: Specify how many miles or points you want to use
- **Date Range**: Select your preferred travel dates

### Step 2: Set Preferences & Filters

- **Maximize Value**: Check this to sort results by highest cents-per-mile value
- **Minimize Fees**: Check this to prioritize flights with lower fees
- **Direct Flights Only**: Check this to show only non-stop flights
- **Show Comparison Chart**: Check this to display a visual comparison of values

### Step 3: Find Redemptions

Click the "Find Redemptions" button to search for available flights and see the best redemption options.

## Understanding the Results

### Value Calculation

The application calculates **cents-per-mile** value using the formula:

```
Value (¢/mile) = (Flight Price × 100) ÷ Miles Used
```

### Result Interpretation

- **Higher cents-per-mile values** indicate better redemption deals
- **Typical good values** range from 1.0¢ to 2.0¢ per mile
- **Exceptional values** can exceed 3.0¢ per mile

### Sample Output

```
AA123 | American Airlines | 2025-10-01 | 10:30 AM
Price: $450.00 | Value: 1.80¢/mile | From JFK to LAX
```

## Code Structure

### Main Components

1. **Helper Functions**

   - `parse_price()`: Extracts numeric price from string format
   - `get_flights()`: Queries database for available flights

2. **User Interface**

   - Input sections for travel details and preferences
   - Filter options for customizing search results
   - Results display with ranking and visualization

3. **Data Processing**
   - SQLite database queries
   - Value calculations and sorting
   - Chart generation for comparisons

### Key Functions

```python
def parse_price(price_str):
    # Extracts numeric price from string using regex
    # Returns float value or None if parsing fails

def get_flights(departure, arrival, start_date, end_date):
    # Queries SQLite database for matching flights
    # Returns list of flight tuples with all details
```

## Database Schema

The application expects a SQLite database with the following table structure:

| Column            | Type | Description                  |
| ----------------- | ---- | ---------------------------- |
| flight_number     | TEXT | Unique flight identifier     |
| departure         | TEXT | Departure airport code       |
| arrival           | TEXT | Arrival airport code         |
| date              | TEXT | Flight date (YYYY-MM-DD)     |
| price             | TEXT | Flight price (string format) |
| airline           | TEXT | Airline code                 |
| flight_time       | TEXT | Departure time               |
| airline_full_name | TEXT | Full airline name            |

## Troubleshooting

### Common Issues

1. **Database Connection Error**

   - Ensure `../week_2/database.db` exists
   - Check file permissions
   - Verify database schema matches expected format

2. **No Flights Found**

   - Verify airport codes are correct (3-letter format)
   - Check date range for available flights
   - Ensure database contains data for specified routes

3. **Value Calculation Errors**
   - Check that price data is in expected format
   - Verify miles input is a positive number

### Error Messages

- **"No flights found for your criteria"**: No matching flights in database
- **Database connection errors**: Check file path and permissions
- **Parsing errors**: Price data format issues

## Future Enhancements

Potential improvements for the application:

- **Multi-airline Support**: Compare across different airline loyalty programs
- **Advanced Filtering**: Filter by airline, time preferences, cabin class
- **Historical Data**: Track redemption values over time
- **Email Alerts**: Notify users of high-value redemption opportunities
- **Mobile Optimization**: Improve mobile device experience
- **API Integration**: Real-time flight data from external sources
