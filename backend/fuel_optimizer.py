"""
Fuel Optimization Engine
Implements physics-based fuel burn calculations with ML enhancement
"""

import numpy as np
from typing import List, Dict, Optional
import math

class FuelOptimizer:
    """
    Fuel burn prediction using physics-based model enhanced with ML
    Based on BADA (Base of Aircraft Data) simplified performance model
    """
    
    def __init__(self):
        # Aircraft performance database (simplified BADA)
        self.aircraft_db = {
            "B737": {
                "mass_reference_kg": 70000,
                "fuel_flow_idle_kg_per_min": 12.5,
                "fuel_flow_cruise_coef": [0.8, 0.002, 0.00001],  # polynomial coefs
                "cruise_mach": 0.785,
                "climb_rate_fpm": 2000,
                "descent_rate_fpm": 1800,
            },
            "A320": {
                "mass_reference_kg": 68000,
                "fuel_flow_idle_kg_per_min": 11.8,
                "fuel_flow_cruise_coef": [0.75, 0.0018, 0.000009],
                "cruise_mach": 0.78,
                "climb_rate_fpm": 2200,
                "descent_rate_fpm": 1900,
            },
            "B747": {
                "mass_reference_kg": 285000,
                "fuel_flow_idle_kg_per_min": 45.0,
                "fuel_flow_cruise_coef": [2.5, 0.006, 0.00003],
                "cruise_mach": 0.855,
                "climb_rate_fpm": 1800,
                "descent_rate_fpm": 1600,
            },
            "A321": {
                "mass_reference_kg": 83000,
                "fuel_flow_idle_kg_per_min": 14.2,
                "fuel_flow_cruise_coef": [0.9, 0.0022, 0.000011],
                "cruise_mach": 0.78,
                "climb_rate_fpm": 2100,
                "descent_rate_fpm": 1850,
            }
        }
        
        # Standard atmosphere (ISA)
        self.isa_lapse_rate = 1.98  # degrees C per 1000 ft
        self.isa_sea_level_temp = 15.0  # degrees C
        
    def calculate_fuel_burn(self, route: List[dict], aircraft_type: str, 
                           wind_data: Dict) -> float:
        """
        Calculate total fuel burn for a given route
        
        Physics-based model accounting for:
        - Climb fuel (highest consumption)
        - Cruise fuel (wind impact)
        - Descent fuel (CDO vs step-down)
        """
        if aircraft_type not in self.aircraft_db:
            aircraft_type = "B737"  # default
            
        ac = self.aircraft_db[aircraft_type]
        total_fuel = 0.0
        
        for i, waypoint in enumerate(route):
            if i == 0:
                continue  # skip first waypoint
                
            prev = route[i-1]
            segment_distance = self._haversine_distance(
                prev["lat"], prev["lon"],
                waypoint["lat"], waypoint["lon"]
            )
            
            # Determine flight phase
            # Use 500ft threshold so step-climb during cruise isn't misclassified
            altitude = waypoint.get("altitude", 35000)
            prev_altitude = prev.get("altitude", 0)
            
            if altitude > prev_altitude + 500:
                phase = "climb"
            elif altitude < prev_altitude - 500:
                phase = "descent"
            else:
                phase = "cruise"
            
            # Calculate segment fuel
            segment_fuel = self._segment_fuel_burn(
                segment_distance, phase, altitude, 
                ac, wind_data
            )
            
            total_fuel += segment_fuel
            
        return total_fuel
    
    def _segment_fuel_burn(self, distance_nm: float, phase: str, 
                          altitude_ft: float, ac: Dict, 
                          wind_data: Dict) -> float:
        """Calculate fuel for a single route segment"""
        
        # Temperature at altitude (ISA)
        temp_dev = wind_data.get("temperature_dev", 0)
        oat = self.isa_sea_level_temp - (altitude_ft / 1000) * self.isa_lapse_rate + temp_dev
        
        if phase == "climb":
            # Climb fuel is ~2.5x cruise fuel for same distance
            base_rate = self._cruise_fuel_rate(altitude_ft, ac) * 2.5
            time_hours = distance_nm / 250  # average climb speed
            
        elif phase == "descent":
            # CDO: continuous descent at idle thrust
            # Saves ~30-40% vs step-down
            base_rate = ac["fuel_flow_idle_kg_per_min"] * 60  # per hour
            time_hours = distance_nm / 240  # average descent speed
            
        else:  # cruise
            base_rate = self._cruise_fuel_rate(altitude_ft, ac)
            cruise_speed = 450  # knots
            
            # Wind impact: headwind increases fuel, tailwind decreases
            wind_component = wind_data.get("average_headwind", 0)
            ground_speed = cruise_speed - wind_component
            time_hours = distance_nm / max(ground_speed, 200)
            
            # Wind penalty/bonus
            wind_factor = cruise_speed / max(ground_speed, 200)
            base_rate *= wind_factor
        
        return base_rate * time_hours
    
    def _cruise_fuel_rate(self, altitude_ft: float, ac: Dict) -> float:
        """Calculate cruise fuel consumption rate (kg/hour)"""
        coef = ac["fuel_flow_cruise_coef"]
        # Polynomial: a + b*alt + c*alt^2
        altitude_kft = altitude_ft / 1000
        fuel_rate = coef[0] + coef[1] * altitude_kft + coef[2] * (altitude_kft ** 2)
        return fuel_rate * 1000  # scale to kg/hour
    
    def evaluate_cdo_benefit(self, airport: Dict, aircraft_type: str) -> bool:
        """
        Determine if Continuous Descent Operations would be beneficial
        
        CDO is beneficial for:
        - Airports with approach over populated areas (noise + fuel)
        - High traffic airports (reduces controller workload)
        - Sufficient airspace for gradual descent
        """
        # Major hubs with CDO-style gradual descent programs (US + international)
        cdo_airports = [
            "KJFK", "KLAX", "KORD", "KDFW", "KDEN",
            "KSFO", "KSEA", "KATL", "KMIA", "KBOS",
            "EGLL", "LFPG", "EDDF", "EHAM", "LEMD", "LIRF", "EKCH", "LOWW",
            "CYYZ", "MMMX", "SBGR",
            "OMDB", "OERK", "HECA", "FACT",
            "VHHH", "ZSPD", "RJTT", "RKSI", "VIDP", "VTBS", "WSSS",
            "YSSY", "NZAA",
        ]
        
        return airport["code"] in cdo_airports
    
    def _haversine_distance(self, lat1: float, lon1: float, 
                           lat2: float, lon2: float) -> float:
        """Calculate great circle distance in nautical miles"""
        R = 3440.065  # Earth radius in nautical miles
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def predict_with_ml(self, features: Dict) -> float:
        """
        Placeholder for ML-enhanced prediction
        In production, load XGBoost/Neural Network model
        """
        # Fallback to physics model
        return 0.0
