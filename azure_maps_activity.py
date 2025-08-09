# requirements.txt
# This file lists the Python libraries required by your Azure Maps activity.
# It should be uploaded to the 'Assets' section of your Azure AI Foundry project
# along with your Python code.

# requests
# 
# azure_maps_activity.py
# This file contains the Python functions for your Azure Maps agent activity.
# It should be uploaded to the 'Assets' section of your Azure AI Foundry project.

import os
import requests
import json

# --- Configuration ---
# IMPORTANT: This code now works with Azure AI Foundry Connected Resources
# The Azure Maps API key will be accessed through the connection you created
# in the Management Center -> Connected Resources

# Try to get the key from Connected Resources context (when running in AI Foundry)
# If not available, fall back to environment variable (for local testing)
try:
    # This will be available when running through Azure AI Foundry Connected Resources
    # The exact variable name may vary based on your connection name
    AZURE_MAPS_SUBSCRIPTION_KEY = os.getenv("AZURE_MAPS_API_KEY") or os.getenv("AZURE_MAPS_SUBSCRIPTION_KEY")
except:
    AZURE_MAPS_SUBSCRIPTION_KEY = None

# For local testing only - uncomment and add your key temporarily:
# AZURE_MAPS_SUBSCRIPTION_KEY = "your-key-here"

# Azure Maps API Endpoints
GEOCODING_URL = "https://atlas.microsoft.com/search/address/json"
ROUTE_URL = "https://atlas.microsoft.com/route/directions/json"

# API Version for Azure Maps
API_VERSION = "1.0"

# --- Helper Functions ---

def get_coordinates_from_address(address: str) -> dict:
    """
    Converts a human-readable address into geographical coordinates (latitude, longitude).

    Args:
        address (str): The address string to geocode.

    Returns:
        dict: A dictionary containing 'latitude' and 'longitude' if successful,
              otherwise an 'error' message.
    """
    if not AZURE_MAPS_SUBSCRIPTION_KEY:
        return {"error": "Azure Maps Subscription Key is not configured."}

    params = {
        "query": address,
        "subscription-key": AZURE_MAPS_SUBSCRIPTION_KEY,
        "api-version": API_VERSION
    }
    try:
        response = requests.get(GEOCODING_URL, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if data and data.get("results") and len(data["results"]) > 0:
            position = data["results"][0].get("position")
            if position and "lat" in position and "lon" in position:
                return {
                    "latitude": position["lat"],
                    "longitude": position["lon"]
                }
            else:
                return {"error": f"Invalid position data in response for address: {address}"}
        else:
            return {"error": f"Could not find coordinates for address: {address}. No results found."}
    except KeyError as e:
        return {"error": f"Missing expected data in geocoding response for '{address}': {e}"}
    except IndexError as e:
        return {"error": f"Unexpected response structure from geocoding API for '{address}': {e}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Error during geocoding API call for '{address}': {e}"}
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON response from geocoding API for '{address}'."}
    except Exception as e:
        return {"error": f"An unexpected error occurred during geocoding for '{address}': {e}"}


def calculate_route(start_latitude: float, start_longitude: float,
                    end_latitude: float, end_longitude: float) -> dict:
    """
    Calculates a driving route between two geographical points.

    Args:
        start_latitude (float): Latitude of the starting point.
        start_longitude (float): Longitude of the starting point.
        end_latitude (float): Latitude of the destination point.
        end_longitude (float): Longitude of the destination point.

    Returns:
        dict: A dictionary containing route details (e.g., travel time, distance)
              if successful, otherwise an 'error' message.
    """
    if not AZURE_MAPS_SUBSCRIPTION_KEY:
        return {"error": "Azure Maps Subscription Key is not configured."}

    # Azure Maps route format: {latitude},{longitude}:{latitude},{longitude}
    route_query = f"{start_latitude},{start_longitude}:{end_latitude},{end_longitude}"
    params = {
        "routeType": "fastest",
        "subscription-key": AZURE_MAPS_SUBSCRIPTION_KEY,
        "api-version": API_VERSION
    }
    
    # Construct the full URL with coordinates
    url = f"{ROUTE_URL}?query={route_query}"
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data and data.get("routes") and len(data["routes"]) > 0:
            # Extract relevant route information
            summary = data["routes"][0].get("summary")
            if summary:
                return {
                    "travel_time_seconds": summary.get("travelTimeInSeconds", 0),
                    "length_in_meters": summary.get("lengthInMeters", 0),
                    "traffic_delay_seconds": summary.get("trafficDelayInSeconds", 0)
                }
            else:
                return {"error": "Invalid route summary in API response."}
        else:
            return {"error": "Could not calculate route. No routes found."}
    except KeyError as e:
        return {"error": f"Missing expected data in routing response: {e}"}
    except IndexError as e:
        return {"error": f"Unexpected response structure from routing API: {e}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Error during routing API call: {e}"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from routing API."}
    except Exception as e:
        return {"error": f"An unexpected error occurred during routing: {e}"}

# --- Input Validation ---

def validate_address_input(address: str) -> dict:
    """
    Validates address input for the multi-agent scenario.
    
    Args:
        address (str): The address to validate.
        
    Returns:
        dict: Validation result with 'valid' boolean and optional 'error' message.
    """
    if not address or not isinstance(address, str):
        return {"valid": False, "error": "Address must be a non-empty string."}
    
    address = address.strip()
    if len(address) < 3:
        return {"valid": False, "error": "Address must be at least 3 characters long."}
    
    if len(address) > 200:
        return {"valid": False, "error": "Address must be less than 200 characters long."}
    
    return {"valid": True}

# --- Main Activity Function ---

def plan_survival_route(start_address: str, end_address: str) -> dict:
    """
    Plans an evacuation route between a starting address and an ending address
    using Azure Maps geocoding and routing services.

    This is the main function that your Azure AI Foundry agent will call.
    Designed for use in Code Interpreter within a multi-agent solution.

    Args:
        start_address (str): The starting address for the route.
        end_address (str): The destination address for the route.

    Returns:
        dict: A dictionary containing the route details or an error message.
              Always includes 'status' field ('success' or 'error') and 'message' field.
    """
    # Validate inputs
    start_validation = validate_address_input(start_address)
    if not start_validation["valid"]:
        return {
            "status": "error", 
            "message": f"Invalid start address: {start_validation['error']}"
        }
    
    end_validation = validate_address_input(end_address)
    if not end_validation["valid"]:
        return {
            "status": "error", 
            "message": f"Invalid end address: {end_validation['error']}"
        }
    # Step 1: Geocode the start address
    start_coords = get_coordinates_from_address(start_address)
    if "error" in start_coords:
        return {"status": "error", "message": f"Failed to geocode start address: {start_coords['error']}"}

    # Step 2: Geocode the end address
    end_coords = get_coordinates_from_address(end_address)
    if "error" in end_coords:
        return {"status": "error", "message": f"Failed to geocode end address: {end_coords['error']}"}

    # Step 3: Calculate the route using the obtained coordinates
    route_details = calculate_route(
        start_coords["latitude"], start_coords["longitude"],
        end_coords["latitude"], end_coords["longitude"]
    )

    if "error" in route_details:
        return {"status": "error", "message": f"Failed to calculate route: {route_details['error']}"}
    else:
        # Convert seconds to minutes for better readability
        travel_time_minutes = round(route_details["travel_time_seconds"] / 60)
        length_km = round(route_details["length_in_meters"] / 1000, 2)
        traffic_delay_minutes = round(route_details["traffic_delay_seconds"] / 60)

        return {
            "status": "success",
            "start_address": start_address,
            "end_address": end_address,
            "route_summary": {
                "estimated_travel_time_minutes": travel_time_minutes,
                "distance_km": length_km,
                "traffic_delay_minutes": traffic_delay_minutes
            },
            "message": (
                f"Successfully planned a route from {start_address} to {end_address}. "
                f"Estimated travel time: {travel_time_minutes} minutes. "
                f"Distance: {length_km} km. "
                f"Traffic delay: {traffic_delay_minutes} minutes."
            )
        }

# Example of how you might test this locally (will not run in Azure AI Foundry directly)
if __name__ == "__main__":
    # Set your Azure Maps Subscription Key as an environment variable for local testing
    # os.environ["AZURE_MAPS_SUBSCRIPTION_KEY"] = "YOUR_AZURE_MAPS_SUBSCRIPTION_KEY"

    # Example usage:
    start = "1 Microsoft Way, Redmond, WA"
    end = "Space Needle, Seattle, WA"
    result = plan_survival_route(start, end)
    print(json.dumps(result, indent=2))

    start_invalid = "Invalid Address XYZ"
    end_valid = "Eiffel Tower, Paris"
    result_error = plan_survival_route(start_invalid, end_valid)
    print(json.dumps(result_error, indent=2))
