import re
import datetime

def format_iso8601_duration(duration_string: str) -> str:
    """
    Parses an ISO 8601 duration string (PTnHnMnS format) and returns a formatted string.

    Args:
        duration_string: The ISO 8601 duration string (e.g., "PT1H30M").

    Returns:
        A string representation of the duration (e.g., "1 hour 30 minutes"),
        or an error message if the format is invalid.
    """
    pattern = r"^P(?:(?P<days>\d+)D)?T?(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?$"
    match = re.match(pattern, duration_string)

    if not match:
        return "Invalid ISO 8601 duration format."

    parts = {k: int(v) if v else 0 for k, v in match.groupdict().items()}
    
    # Calculate total seconds
    total_seconds = parts["days"] * 86400 + parts["hours"] * 3600 + parts["minutes"] * 60 + parts["seconds"]

    # Create a timedelta object (optional, but convenient for calculations)
    duration_td = datetime.timedelta(seconds=total_seconds)

    # Format the timedelta as a string
    hours, remainder = divmod(duration_td.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    formatted_parts = []
    if int(hours) > 0:
        formatted_parts.append(f"{int(hours)} hour{'s' if int(hours) > 1 else ''}")
    if int(minutes) > 0:
        formatted_parts.append(f"{int(minutes)} minute{'s' if int(minutes) > 1 else ''}")
    if int(seconds) > 0:
         formatted_parts.append(f"{int(seconds)} second{'s' if int(seconds) > 1 else ''}")

    if formatted_parts:
        return " ".join(formatted_parts)
    else:
        return "0 seconds" # Handle the case of "PT0S" or empty duration