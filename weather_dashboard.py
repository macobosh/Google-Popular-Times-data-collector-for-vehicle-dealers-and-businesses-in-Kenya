import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

class WeatherDashboard:
    """
    A comprehensive weather dashboard that fetches data from OpenWeatherMap API
    Provides current weather, forecasts, and weather alerts
    """
    
    # Free weather API - OpenWeatherMap
    CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
    FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
    AIR_QUALITY_URL = "https://api.openweathermap.org/data/2.5/air_quality"
    
    def __init__(self, api_key: str):
        """
        Initialize weather dashboard with API key
        
        Args:
            api_key: OpenWeatherMap API key (get free key at https://openweathermap.org/api)
        """
        self.api_key = api_key
        self.cache_file = 'weather_cache.json'
        self.cache_duration = 600  # 10 minutes in seconds
        self.current_weather_data = {}
        self.forecast_data = {}
    
    def _load_cache(self) -> Dict:
        """Load cached weather data"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                    # Check if cache is still valid
                    if cache.get('timestamp'):
                        cache_age = time.time() - cache['timestamp']
                        if cache_age < self.cache_duration:
                            return cache
            except:
                pass
        return {}
    
    def _save_cache(self, data: Dict):
        """Save weather data to cache"""
        data['timestamp'] = time.time()
        with open(self.cache_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_current_weather(self, city: str, units: str = "metric") -> Dict:
        """
        Fetch current weather for a specific city
        
        Args:
            city: City name (e.g., "Nairobi", "London")
            units: Temperature units - "metric" (Celsius), "imperial" (Fahrenheit)
        
        Returns:
            Dictionary with current weather data
        """
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': units
            }
            
            response = requests.get(self.CURRENT_WEATHER_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if response.status_code == 200:
                self.current_weather_data = self._parse_current_weather(data, units)
                print(f"✅ Current weather fetched for {city}")
                return self.current_weather_data
            else:
                print(f"❌ Error: {data.get('message', 'Unknown error')}")
                return {}
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching weather data: {e}")
            return {}
    
    def _parse_current_weather(self, data: Dict, units: str) -> Dict:
        """Parse and format current weather data"""
        temp_unit = "°C" if units == "metric" else "°F"
        speed_unit = "m/s" if units == "metric" else "mph"
        
        return {
            'city': data.get('name'),
            'country': data.get('sys', {}).get('country'),
            'temperature': f"{data.get('main', {}).get('temp')}{temp_unit}",
            'feels_like': f"{data.get('main', {}).get('feels_like')}{temp_unit}",
            'temp_min': f"{data.get('main', {}).get('temp_min')}{temp_unit}",
            'temp_max': f"{data.get('main', {}).get('temp_max')}{temp_unit}",
            'humidity': f"{data.get('main', {}).get('humidity')}%",
            'pressure': f"{data.get('main', {}).get('pressure')} hPa",
            'description': data.get('weather', [{}])[0].get('description', 'N/A').title(),
            'icon': data.get('weather', [{}])[0].get('icon', ''),
            'wind_speed': f"{data.get('wind', {}).get('speed')} {speed_unit}",
            'wind_direction': data.get('wind', {}).get('deg', 'N/A'),
            'cloudiness': f"{data.get('clouds', {}).get('all')}%",
            'visibility': f"{data.get('visibility', 0) / 1000:.1f} km",
            'sunrise': datetime.fromtimestamp(data.get('sys', {}).get('sunrise')).strftime('%H:%M:%S'),
            'sunset': datetime.fromtimestamp(data.get('sys', {}).get('sunset')).strftime('%H:%M:%S'),
            'timezone': data.get('timezone'),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_forecast(self, city: str, days: int = 5, units: str = "metric") -> List[Dict]:
        """
        Fetch weather forecast for upcoming days
        
        Args:
            city: City name
            days: Number of days to forecast (max 5 for free tier)
            units: Temperature units
        
        Returns:
            List of forecast data for each day
        """
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': units,
                'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
            }
            
            response = requests.get(self.FORECAST_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if response.status_code == 200:
                self.forecast_data = self._parse_forecast(data, units)
                print(f"✅ {days}-day forecast fetched for {city}")
                return self.forecast_data
            else:
                print(f"❌ Error: {data.get('message', 'Unknown error')}")
                return []
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching forecast data: {e}")
            return []
    
    def _parse_forecast(self, data: Dict, units: str) -> List[Dict]:
        """Parse and format forecast data"""
        temp_unit = "°C" if units == "metric" else "°F"
        forecasts = []
        
        for item in data.get('list', []):
            forecast = {
                'datetime': item.get('dt_txt'),
                'temperature': f"{item.get('main', {}).get('temp')}{temp_unit}",
                'temp_min': f"{item.get('main', {}).get('temp_min')}{temp_unit}",
                'temp_max': f"{item.get('main', {}).get('temp_max')}{temp_unit}",
                'humidity': f"{item.get('main', {}).get('humidity')}%",
                'description': item.get('weather', [{}])[0].get('description', 'N/A').title(),
                'icon': item.get('weather', [{}])[0].get('icon', ''),
                'wind_speed': f"{item.get('wind', {}).get('speed')} m/s",
                'rain_probability': f"{item.get('pop', 0) * 100:.0f}%",
                'pressure': f"{item.get('main', {}).get('pressure')} hPa"
            }
            forecasts.append(forecast)
        
        return forecasts
    
    def get_air_quality(self, city: str) -> Dict:
        """
        Fetch air quality data for a city
        
        Args:
            city: City name
        
        Returns:
            Air quality metrics
        """
        try:
            # First get coordinates for the city
            params = {
                'q': city,
                'appid': self.api_key
            }
            
            response = requests.get(self.CURRENT_WEATHER_URL, params=params, timeout=10)
            if response.status_code != 200:
                return {}
            
            city_data = response.json()
            lat = city_data.get('coord', {}).get('lat')
            lon = city_data.get('coord', {}).get('lon')
            
            # Get air quality data
            air_params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key
            }
            
            air_response = requests.get(self.AIR_QUALITY_URL, params=air_params, timeout=10)
            air_response.raise_for_status()
            
            air_data = air_response.json()
            
            if air_response.status_code == 200:
                return self._parse_air_quality(air_data)
            else:
                return {}
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching air quality data: {e}")
            return {}
    
    def _parse_air_quality(self, data: Dict) -> Dict:
        """Parse air quality data"""
        aqi_levels = {
            1: "Good",
            2: "Fair",
            3: "Moderate",
            4: "Poor",
            5: "Very Poor"
        }
        
        aqi = data.get('list', [{}])[0].get('main', {}).get('aqi', 0)
        components = data.get('list', [{}])[0].get('components', {})
        
        return {
            'aqi_index': aqi,
            'aqi_level': aqi_levels.get(aqi, 'Unknown'),
            'pm2_5': f"{components.get('pm2_5', 'N/A')} µg/m³",
            'pm10': f"{components.get('pm10', 'N/A')} µg/m³",
            'no2': f"{components.get('no2', 'N/A')} µg/m³",
            'o3': f"{components.get('o3', 'N/A')} µg/m³",
            'so2': f"{components.get('so2', 'N/A')} µg/m³",
            'co': f"{components.get('co', 'N/A')} µg/m³",
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def display_current_weather(self):
        """Display current weather in a formatted way"""
        if not self.current_weather_data:
            print("❌ No current weather data available")
            return
        
        data = self.current_weather_data
        
        print("\n" + "="*70)
        print("🌍 CURRENT WEATHER DASHBOARD")
        print("="*70)
        print(f"\n📍 Location: {data['city']}, {data['country']}")
        print(f"⏰ Updated: {data['timestamp']}")
        print("\n" + "-"*70)
        print(f"🌡️  Temperature: {data['temperature']} (feels like {data['feels_like']})")
        print(f"📊 Min/Max: {data['temp_min']} / {data['temp_max']}")
        print(f"💧 Humidity: {data['humidity']}")
        print(f"🌥️  Condition: {data['description']}")
        print(f"💨 Wind Speed: {data['wind_speed']} (Direction: {data['wind_direction']}°)")
        print(f"☁️  Cloudiness: {data['cloudiness']}")
        print(f"👁️  Visibility: {data['visibility']}")
        print(f"🔽 Pressure: {data['pressure']}")
        print("\n" + "-"*70)
        print(f"🌅 Sunrise: {data['sunrise']}")
        print(f"🌇 Sunset: {data['sunset']}")
        print("="*70 + "\n")
    
    def display_forecast(self):
        """Display weather forecast"""
        if not self.forecast_data:
            print("❌ No forecast data available")
            return
        
        print("\n" + "="*70)
        print("📅 5-DAY WEATHER FORECAST")
        print("="*70)
        
        for idx, forecast in enumerate(self.forecast_data):
            if idx % 8 == 0:  # Show one forecast per day
                print(f"\n📆 {forecast['datetime']}")
                print("-"*70)
            
            print(f"  ⏱️  {forecast['datetime']}")
            print(f"     🌡️  Temp: {forecast['temperature']} (Min: {forecast['temp_min']}, Max: {forecast['temp_max']})")
            print(f"     💧 Humidity: {forecast['humidity']}")
            print(f"     🌤️  Condition: {forecast['description']}")
            print(f"     💨 Wind: {forecast['wind_speed']}")
            print(f"     🌧️  Rain Probability: {forecast['rain_probability']}")
        
        print("\n" + "="*70 + "\n")
    
    def display_air_quality(self, air_quality: Dict):
        """Display air quality data"""
        if not air_quality:
            print("❌ No air quality data available")
            return
        
        print("\n" + "="*70)
        print("💨 AIR QUALITY REPORT")
        print("="*70)
        print(f"\n⏰ Updated: {air_quality['timestamp']}")
        print(f"\n📊 AQI Index: {air_quality['aqi_index']}/5")
        print(f"🎯 AQI Level: {air_quality['aqi_level']}")
        print("\n" + "-"*70)
        print("📈 Pollutants:")
        print(f"  • PM2.5 (Fine Particles): {air_quality['pm2_5']}")
        print(f"  • PM10 (Coarse Particles): {air_quality['pm10']}")
        print(f"  • NO₂ (Nitrogen Dioxide): {air_quality['no2']}")
        print(f"  • O₃ (Ozone): {air_quality['o3']}")
        print(f"  • SO₂ (Sulfur Dioxide): {air_quality['so2']}")
        print(f"  • CO (Carbon Monoxide): {air_quality['co']}")
        print("="*70 + "\n")
    
    def get_multiple_cities(self, cities: List[str], units: str = "metric") -> Dict:
        """
        Fetch weather for multiple cities
        
        Args:
            cities: List of city names
            units: Temperature units
        
        Returns:
            Dictionary with weather data for all cities
        """
        all_weather = {}
        
        print(f"\n🔄 Fetching weather for {len(cities)} cities...")
        
        for city in cities:
            weather = self.get_current_weather(city, units)
            if weather:
                all_weather[city] = weather
            time.sleep(1)  # Rate limiting
        
        return all_weather
    
    def compare_cities(self, cities: List[str], units: str = "metric"):
        """
        Compare weather across multiple cities
        
        Args:
            cities: List of city names to compare
            units: Temperature units
        """
        weather_data = self.get_multiple_cities(cities, units)
        
        if not weather_data:
            print("❌ No weather data to compare")
            return
        
        print("\n" + "="*70)
        print("🌍 CITIES WEATHER COMPARISON")
        print("="*70)
        
        print(f"\n{'City':<20} {'Temp':<15} {'Condition':<20} {'Wind':<15}")
        print("-"*70)
        
        for city, data in weather_data.items():
            print(f"{city:<20} {data['temperature']:<15} {data['description']:<20} {data['wind_speed']:<15}")
        
        print("="*70 + "\n")
    
    def export_to_json(self, filename: str = "weather_data.json"):
        """Export weather data to JSON file"""
        export_data = {
            'current_weather': self.current_weather_data,
            'forecast': self.forecast_data,
            'exported_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✅ Weather data exported to {filename}")
    
    def export_to_csv(self, filename: str = "weather_forecast.csv"):
        """Export forecast data to CSV"""
        if not self.forecast_data:
            print("❌ No forecast data to export")
            return
        
        import csv
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.forecast_data[0].keys())
            writer.writeheader()
            writer.writerows(self.forecast_data)
        
        print(f"✅ Forecast data exported to {filename}")


# Usage Examples
if __name__ == "__main__":
    # Get your free API key from: https://openweathermap.org/api
    API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"
    
    # Initialize dashboard
    dashboard = WeatherDashboard(API_KEY)
    
    # Example 1: Get current weather for a single city
    print("\n" + "="*70)
    print("🌤️  WEATHER DASHBOARD - SINGLE CITY")
    print("="*70)
    
    dashboard.get_current_weather("Nairobi", units="metric")
    dashboard.display_current_weather()
    
    # Example 2: Get 5-day forecast
    print("\n" + "="*70)
    print("📅 FETCHING FORECAST")
    print("="*70)
    
    dashboard.get_forecast("Nairobi", days=5, units="metric")
    dashboard.display_forecast()
    
    # Example 3: Get air quality
    print("\n" + "="*70)
    print("💨 FETCHING AIR QUALITY")
    print("="*70)
    
    air_quality = dashboard.get_air_quality("Nairobi")
    dashboard.display_air_quality(air_quality)
    
    # Example 4: Compare multiple cities
    print("\n" + "="*70)
    print("🌍 COMPARING MULTIPLE CITIES")
    print("="*70)
    
    cities = ["Nairobi", "London", "New York", "Tokyo", "Sydney"]
    dashboard.compare_cities(cities, units="metric")
    
    # Example 5: Export data
    dashboard.export_to_json("weather_data.json")
    dashboard.export_to_csv("weather_forecast.csv")
