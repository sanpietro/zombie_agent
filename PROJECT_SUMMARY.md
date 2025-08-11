# Zombie Survival Agent - Azure Maps Integration

## Project Overview
A zombie-themed survival route planning agent that integrates with Azure Maps API through Azure AI Foundry using OpenAPI 3.0 specifications and custom authentication.

## 🚀 Key Features
- **Real-time Route Planning**: Uses Azure Maps REST API for geocoding and routing
- **Custom Authentication**: Implements custom keys with subscription-key for Azure Maps
- **OpenAPI 3.0 Integration**: Comprehensive specification for Azure AI Foundry
- **Zombie-themed Interface**: Survival-focused UI with emergency route planning
- **Production Ready**: Clean, streamlined codebase with proper error handling

## 📁 Project Structure

### Core Application Files
- **`app.py`** - Main Streamlit application with zombie-themed UI
- **`azure_maps_activity.py`** - Cleaned Azure Maps integration (85 lines, down from 336)
- **`azure_maps_openapi.json`** - Final OpenAPI 3.0 specification with proper defaults

### Configuration & Deployment
- **`DEPLOYMENT_UPDATED.md`** - Complete Azure AI Foundry deployment guide
- **`DEPLOYMENT.md`** - Original deployment documentation
- **`.env.template`** - Environment variables template
- **`requirements.txt`** - Python dependencies

### Additional Resources
- **`openweathermap_openapi_schema.json`** - Weather API schema (for future features)
- **`zombie_icon.png`** - Custom zombie avatar
- **`README.md`** - Project documentation

## 🔑 Azure Integration Details

### OpenAPI 3.0 Specification (`azure_maps_openapi.json`)
- **Geocoding Endpoint**: `/search/address/json` with `geocode_address` operationId
- **Routing Endpoint**: `/route/directions/json` with `calculate_route_directions` operationId
- **Authentication**: `subscription-key` security scheme for custom keys
- **Parameter Defaults**: `api-version: "1.0"` defaults to resolve query parameter issues

### Custom Keys Configuration
- **Connection Name**: Azure Maps API connection
- **Key Name**: `subscription-key`
- **Key Value**: Your Azure Maps subscription key
- **Base URL**: `https://atlas.microsoft.com`

## 🛠️ Technical Achievements

### Problems Solved
1. **Rate Limiting**: Created minimal OpenAPI spec to reduce token consumption
2. **Parameter Configuration**: Added default values for required `api-version` parameter
3. **Authentication**: Implemented proper custom keys setup with subscription-key
4. **Code Quality**: Streamlined from 336 to 85 lines with better error handling

### Integration Success
- ✅ Real-time Azure Maps API calls (confirmed via agent responses)
- ✅ Successful geocoding of addresses to coordinates
- ✅ Detailed route calculations with turn-by-turn directions
- ✅ Proper error handling and parameter passing
- ✅ Custom authentication working with Azure AI Foundry

## 🧟‍♂️ Agent Capabilities
The zombie survival agent can:
- Plan evacuation routes between any two addresses
- Provide detailed turn-by-turn directions
- Calculate distance and estimated travel time
- Offer survival tips (gas, supplies, shelter, group travel)
- Present information in emergency-themed format

## 🔄 Deployment Status
- **Local Development**: ✅ Complete and tested
- **Azure AI Foundry**: ✅ Integrated with custom OpenAPI tool
- **Repository**: ✅ Clean codebase committed and ready for push

## 📝 Usage Example
```
User: "I need to get from Atlanta to New York City"
Agent: Provides detailed route with survival tips, approximately 800 miles, 14h 45m
```

## 🚀 Next Steps
1. Complete git push to repository (authentication may be required)
2. Optional: Add weather integration using the OpenWeatherMap schema
3. Optional: Deploy to Azure Container Apps or Streamlit Cloud
4. Optional: Add more survival-themed features (supply locations, safe zones)

---
**Created**: August 10, 2025  
**Status**: Production Ready 🎉
