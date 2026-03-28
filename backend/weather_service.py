"""
Weather Service - NOAA Aviation Weather Integration
Fetches real wind and temperature data for route optimization
"""

import requests
import numpy as np
from typing import Dict, Optional
from datetime import datetime
import json

class WeatherService:
    """
    Interface to NOAA Aviation Weather API
    Provides wind and temperature data at altitude
    """
    
    def __init__(self):
        self.base_url = "https://aviationweather.gov/api/data"
        self.cache = {}  # Simple cache for hackathon
        
    def get_wind_along_route(self, lat1: float, lon1: float,
                            lat2: float, lon2: float) -> Dict:
        """
        Get weather data along a route
        
        Returns:
            - average_headwind: knots (positive = headwind, negative = tailwind)
            - wind_speed: knots
            - wind_direction: degrees true
            - temperature_dev: ISA deviation (degrees C)
        """
        try:
            # For hackathon: return realistic synthetic data
            # In production: call NOAA WIFS API
            return self._generate_realistic_wind(lat1, lon1, lat2, lon2)
        except Exception as e:
            # Fallback to generic data
            return self._default_wind_data()
    
    def _generate_realistic_wind(self, lat1: float, lon1: float,
                                 lat2: float, lon2: float) -> Dict:
        """
        Generate realistic wind patterns based on route characteristics
        
        Simulates:
        - Jet stream (west to east, 30,000-40,000 ft)
        - Prevailing westerlies
        - Regional variations
        """
        # Route midpoint
        mid_lat = (lat1 + lat2) / 2
        mid_lon = (lon1 + lon2) / 2
        
        # Route bearing
        bearing = self._calculate_bearing(lat1, lon1, lat2, lon2)
        
        # Mid-latitude jet cores: NAT, North Pacific, CONUS, East Asia (west-to-east flow)
        abs_lat = abs(mid_lat)
        ml = mid_lon
        in_jet_stream = False
        jet_strength = 1.0
        if 32 <= abs_lat <= 62:
            nat = -75 <= ml <= 20
            npac = ml >= 125 or ml <= -118
            conus = -128 <= ml <= -65
            easia = 100 <= ml <= 150
            in_jet_stream = nat or npac or conus or easia
            if nat or npac:
                jet_strength = 1.15
            elif easia:
                jet_strength = 1.0
            elif conus:
                jet_strength = 0.95
            # Southern hemisphere polar jet (weaker, still westerly)
            if mid_lat < -32 and 40 <= abs_lat <= 58:
                in_jet_stream = True
                jet_strength = 0.55

        if in_jet_stream:
            base = 88 * jet_strength
            wind_speed = np.random.normal(base, 22 + 8 * (1 - min(jet_strength, 1)))
            wind_direction = np.random.normal(265, 22)

            wind_angle = abs(wind_direction - bearing)
            headwind = wind_speed * np.cos(np.radians(wind_angle))

            temperature_dev = np.random.normal(-5, 3)
        else:
            wind_speed = np.random.normal(25, 15)
            wind_direction = np.random.normal(240, 35)

            wind_angle = abs(wind_direction - bearing)
            headwind = wind_speed * np.cos(np.radians(wind_angle))

            temperature_dev = np.random.normal(0, 2)
        
        return {
            "average_headwind": round(headwind, 1),
            "wind_speed": round(wind_speed, 1),
            "wind_direction": round(wind_direction, 1),
            "temperature_dev": round(temperature_dev, 1),
            "source": "simulated_noaa",
            "jet_stream_present": in_jet_stream,
            "timestamp": datetime.now().isoformat()
        }
    
    def _default_wind_data(self) -> Dict:
        """Default weather conditions"""
        return {
            "average_headwind": 10.0,
            "wind_speed": 25.0,
            "wind_direction": 270.0,
            "temperature_dev": 0.0,
            "source": "default",
            "jet_stream_present": False,
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_bearing(self, lat1: float, lon1: float,
                          lat2: float, lon2: float) -> float:
        """Calculate bearing between two points"""
        import math
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lon = math.radians(lon2 - lon1)
        
        x = math.sin(delta_lon) * math.cos(lat2_rad)
        y = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon))
        
        bearing = math.degrees(math.atan2(x, y))
        return (bearing + 360) % 360
    
    def fetch_noaa_winds_aloft(self, airport_code: str) -> Optional[Dict]:
        """
        Fetch actual NOAA winds aloft data for an airport
        
        Reference implementation for production use
        """
        # NOAA API endpoint (for production)
        # url = f"{self.base_url}/winds?ids={airport_code}&format=json"
        
        # Returns wind data at standard levels: 3000, 6000, 9000, 12000, 18000,
        # 24000, 30000, 34000, 39000 feet
        
        # For hackathon: return simulated data
        return self._default_wind_data()
    
    def get_sigmet_data(self, bounds: str) -> list:
        """
        Fetch SIGMETs (significant weather) for a region
        
        Used to avoid turbulence, thunderstorms, icing
        """
        # Production: call NOAA API
        # url = f"{self.base_url}/sigmet?format=json&bounds={bounds}"
        
        # For hackathon: return empty (no significant weather)
        return []
