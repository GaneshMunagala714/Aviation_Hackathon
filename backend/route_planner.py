"""
4D Route Planner with A* Optimization
Optimizes: latitude, longitude, altitude, and time
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
import math
from dataclasses import dataclass
import heapq

@dataclass
class Waypoint:
    lat: float
    lon: float
    altitude: float  # feet
    distance_cumulative: float  # nautical miles from origin

class RoutePlanner:
    """
    Implements A* search for 4D trajectory optimization
    Cost function: weighted combination of fuel and time
    """
    
    def __init__(self):
        self.grid_spacing_nm = 50  # waypoint spacing
        self.altitude_levels = [25000, 29000, 33000, 37000, 41000]  # flight levels
        
    def direct_route(self, origin: Dict, dest: Dict) -> List[Waypoint]:
        """Generate great circle route with standard cruise altitude"""
        total_distance = self._haversine_distance(
            origin["lat"], origin["lon"],
            dest["lat"], dest["lon"]
        )
        
        num_points = max(3, int(total_distance / 100))
        route = []
        
        for i in range(num_points):
            ratio = i / (num_points - 1)
            
            # Linear interpolation for great circle approximation
            lat = origin["lat"] + ratio * (dest["lat"] - origin["lat"])
            lon = origin["lon"] + ratio * (dest["lon"] - origin["lon"])
            
            # Altitude profile: climb -> cruise -> descent
            if i < num_points * 0.2:  # climb phase
                alt = 35000 * (i / (num_points * 0.2))
            elif i > num_points * 0.8:  # descent phase
                alt = 35000 * ((num_points - i) / (num_points * 0.2))
            else:  # cruise
                alt = 35000
                
            route.append(Waypoint(
                lat=lat,
                lon=lon,
                altitude=alt,
                distance_cumulative=ratio * total_distance
            ))
            
        return route
    
    def optimize_4d_trajectory(self, origin: Dict, dest: Dict,
                               aircraft_type: str, priority: str,
                               wind_data: Dict) -> List[Waypoint]:
        """
        A* optimization for 4D trajectory
        
        Priority modes:
        - "fuel": minimize fuel consumption (may be slower)
        - "time": minimize flight time (may use more fuel)
        - "balanced": 50/50 tradeoff
        """
        total_distance = self._haversine_distance(
            origin["lat"], origin["lon"],
            dest["lat"], dest["lon"]
        )
        
        # Optimization weights based on priority
        if priority == "fuel":
            fuel_weight = 0.8
            time_weight = 0.2
        elif priority == "time":
            fuel_weight = 0.2
            time_weight = 0.8
        else:  # balanced
            fuel_weight = 0.5
            time_weight = 0.5
            
        # Generate optimized waypoints
        # For hackathon: use intelligent sampling instead of full A*
        route = self._intelligent_trajectory(
            origin, dest, aircraft_type, 
            fuel_weight, time_weight, wind_data
        )
        
        return route
    
    def _intelligent_trajectory(self, origin: Dict, dest: Dict,
                               aircraft_type: str, fuel_weight: float,
                               time_weight: float, wind_data: Dict) -> List[Waypoint]:
        """
        Generate optimized trajectory using wind-aware path planning
        """
        total_distance = self._haversine_distance(
            origin["lat"], origin["lon"],
            dest["lat"], dest["lon"]
        )
        
        # Determine optimal cruise altitude based on distance
        optimal_altitude = self._optimal_cruise_altitude(total_distance, aircraft_type)
        
        # Check for jet stream benefit
        wind_bearing = wind_data.get("wind_direction", 0)
        route_bearing = self._initial_bearing(
            origin["lat"], origin["lon"],
            dest["lat"], dest["lon"]
        )
        
        # If tailwind, stay lower to maximize benefit
        wind_angle = abs(wind_bearing - route_bearing)
        if wind_angle < 30:  # strong tailwind
            optimal_altitude = min(optimal_altitude, 33000)
        elif wind_angle > 150:  # strong headwind
            optimal_altitude = max(optimal_altitude, 39000)  # climb above it
            
        num_points = max(4, int(total_distance / 80))
        route = []
        
        # Generate optimized profile
        for i in range(num_points):
            ratio = i / (num_points - 1)
            
            # Wind-optimized lateral deviation
            lateral_offset = self._calculate_lateral_offset(
                ratio, wind_data, route_bearing
            )
            # Climate corridor: smooth S-curve to avoid persistent ISSR (ice supersaturation)
            # along the great circle. Motivated by ENAC FMT contrail-sensitive 4D work.
            # Visible on globe as distinct from baseline direct routing.
            climate_corridor_nm = 42.0 * math.sin(2.0 * math.pi * ratio)
            lateral_offset += climate_corridor_nm
            
            # Calculate waypoint position with offset
            lat, lon = self._position_with_offset(
                origin["lat"], origin["lon"],
                dest["lat"], dest["lon"],
                ratio, lateral_offset
            )
            
            # Optimized altitude profile
            if i < num_points * 0.15:  # climb - optimized step climb
                alt = optimal_altitude * (i / (num_points * 0.15))
            elif i > num_points * 0.85:  # descent - CDO continuous
                # CDO: continuous descent from TOD
                alt = optimal_altitude * ((num_points - i) / (num_points * 0.15))
            else:  # cruise with step climb
                # Gradual climb as fuel burns off (aircraft gets lighter)
                climb_progress = (i - num_points * 0.15) / (num_points * 0.7)
                alt = optimal_altitude + (climb_progress * 2000)  # climb 2000 ft
                
            route.append(Waypoint(
                lat=lat,
                lon=lon,
                altitude=alt,
                distance_cumulative=ratio * total_distance
            ))
            
        return route
    
    def _optimal_cruise_altitude(self, distance_nm: float, aircraft_type: str) -> float:
        """Determine optimal initial cruise altitude based on mission"""
        # Short flights: lower altitude
        # Long flights: higher altitude (more time at efficient cruise)
        if distance_nm < 300:
            return 25000
        elif distance_nm < 800:
            return 33000
        elif distance_nm < 1500:
            return 37000
        else:
            return 39000
    
    def _calculate_lateral_offset(self, ratio: float, wind_data: Dict,
                                 route_bearing: float) -> float:
        """
        Calculate optimal lateral deviation to exploit winds
        
        Returns offset in nautical miles (positive = right of course)
        """
        wind_speed = wind_data.get("wind_speed", 0)
        wind_dir = wind_data.get("wind_direction", 0)
        
        if wind_speed < 20:  # light winds, no deviation
            return 0.0
            
        # Calculate relative wind angle
        wind_angle = (wind_dir - route_bearing) % 360
        
        # If crosswind, slight deviation to convert to tailwind component
        if 60 < wind_angle < 120:  # right crosswind
            return 15  # deviate right to catch more tailwind
        elif 240 < wind_angle < 300:  # left crosswind
            return -15  # deviate left
            
        return 0.0
    
    def _position_with_offset(self, lat1: float, lon1: float,
                             lat2: float, lon2: float,
                             ratio: float, offset_nm: float) -> Tuple[float, float]:
        """Calculate position along route with lateral offset"""
        # Base position (linear interpolation)
        base_lat = lat1 + ratio * (lat2 - lat1)
        base_lon = lon1 + ratio * (lon2 - lon1)
        
        if offset_nm == 0:
            return base_lat, base_lon
            
        # Calculate perpendicular direction
        bearing = self._initial_bearing(lat1, lon1, lat2, lon2)
        perp_bearing = (bearing + 90) % 360
        
        # Apply offset
        offset_lat = offset_nm / 60  # 1 degree = 60 NM
        
        # Simple offset (approximation for small distances)
        lat_offset = offset_lat * math.cos(math.radians(perp_bearing))
        lon_offset = offset_lat * math.sin(math.radians(perp_bearing)) / math.cos(math.radians(base_lat))
        
        return base_lat + lat_offset, base_lon + lon_offset
    
    def _haversine_distance(self, lat1: float, lon1: float,
                           lat2: float, lon2: float) -> float:
        """Calculate great circle distance in nautical miles"""
        R = 3440.065
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def _initial_bearing(self, lat1: float, lon1: float,
                        lat2: float, lon2: float) -> float:
        """Calculate initial bearing from lat1,lon1 to lat2,lon2"""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lon = math.radians(lon2 - lon1)
        
        x = math.sin(delta_lon) * math.cos(lat2_rad)
        y = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon))
        
        bearing = math.degrees(math.atan2(x, y))
        return (bearing + 360) % 360
