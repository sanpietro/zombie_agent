import os
import requests
import json

# Configuration - Azure Maps will be accessed through OpenAPI connection
AZURE_MAPS_SUBSCRIPTION_KEY = os.getenv("subscription-key")

# Azure Maps API Endpoints
GEOCODING_URL = "https://atlas.microsoft.com/search/address/json"
ROUTE_URL = "https://atlas.microsoft.com/route/directions/json"
API_VERSION = "1.0"

def get_coordinates_from_address(address: str) -> dict:
    """
    Converts a human-readable address into geographical coordinates (latitude, longitude).
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
        response.raise_for_status()
        data = response.json()

        if data and data.get("results") and len(data["results"]) > 0:
            position = data["results"][0].get("position")
            if position and "lat" in position and "lon" in position:
                return {
                    "latitude": position["lat"],
                    "longitude": position["lon"]
                }
        
        return {"error": f"Could not find coordinates for address: {address}"}
    except Exception as e:
        return {"error": f"Geocoding error for '{address}': {str(e)}"}


def calculate_route(start_latitude: float, start_longitude: float,
                    end_latitude: float, end_longitude: float) -> dict:
    """
    Calculates a driving route between two geographical points.
    """
    if not AZURE_MAPS_SUBSCRIPTION_KEY:
        return {"error": "Azure Maps Subscription Key is not configured."}

    route_query = f"{start_latitude},{start_longitude}:{end_latitude},{end_longitude}"
    params = {
        "routeType": "fastest",
        "subscription-key": AZURE_MAPS_SUBSCRIPTION_KEY,
        "api-version": API_VERSION
    }
    
    url = f"{ROUTE_URL}?query={route_query}"
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data and data.get("routes") and len(data["routes"]) > 0:
            summary = data["routes"][0].get("summary")
            if summary:
                return {
                    "travel_time_seconds": summary.get("travelTimeInSeconds", 0),
                    "length_in_meters": summary.get("lengthInMeters", 0),
                    "traffic_delay_seconds": summary.get("trafficDelayInSeconds", 0)
                }
        
        return {"error": "Could not calculate route."}
    except Exception as e:
        return {"error": f"Routing error: {str(e)}"}

def validate_address_input(address: str) -> dict:
    """Validates address input."""
    if not address or not isinstance(address, str):
        return {"valid": False, "error": "Address must be a non-empty string."}
    
    address = address.strip()
    if len(address) < 3:
        return {"valid": False, "error": "Address must be at least 3 characters long."}
    
    if len(address) > 200:
        return {"valid": False, "error": "Address must be less than 200 characters long."}
    
    return {"valid": True}


def plan_survival_route(start_address: str, end_address: str) -> dict:
    """
    Plans an evacuation route between a starting address and an ending address.
    This is the main function for Azure AI Foundry agent integration.
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

    # Geocode addresses
    start_coords = get_coordinates_from_address(start_address)
    if "error" in start_coords:
        return {"status": "error", "message": f"Failed to geocode start address: {start_coords['error']}"}

    end_coords = get_coordinates_from_address(end_address)
    if "error" in end_coords:
        return {"status": "error", "message": f"Failed to geocode end address: {end_coords['error']}"}

    # Calculate route
    route_details = calculate_route(
        start_coords["latitude"], start_coords["longitude"],
        end_coords["latitude"], end_coords["longitude"]
    )

    if "error" in route_details:
        return {"status": "error", "message": f"Failed to calculate route: {route_details['error']}"}

    # Format results
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
            f"Route from {start_address} to {end_address}: "
            f"{travel_time_minutes} minutes, {length_km} km, "
            f"{traffic_delay_minutes} minutes traffic delay."
        )
    }
