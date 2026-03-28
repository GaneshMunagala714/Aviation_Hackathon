"""
Contrail Formation & Climate Impact Model

Based on:
- Google/Breakthrough Energy research (2023-2025)
- Schmidt-Appleman criterion for contrail formation
- IPCC contrail radiative forcing estimates

KEY INSIGHT: Contrails cause ~35% of aviation's total warming impact.
Google proved 62% contrail reduction possible with AI (American Airlines, 2025).
Only 0.11% fuel cost increase for 73% warming reduction.
"""

import numpy as np
from typing import List, Dict, Tuple
import math


class ContrailModel:
    """
    Predicts contrail formation probability and climate impact
    along flight trajectories.

    Schmidt-Appleman criterion: contrails form when exhaust mixes
    with ambient air that is cold enough and humid enough for ice
    supersaturation.
    """

    # Threshold temperature for contrail formation (simplified Schmidt-Appleman)
    # Below this temp at given humidity, contrails persist
    CONTRAIL_TEMP_THRESHOLD_C = -40.0

    # Relative humidity threshold for persistent contrails
    RH_ICE_THRESHOLD = 0.95  # 95% RH over ice

    # Radiative forcing per km of persistent contrail (mW/m^2/km)
    # From IPCC and Lee et al. 2021
    RF_PER_CONTRAIL_KM = 0.012

    # CO2-equivalent multiplier for contrail warming
    # Contrails have ~35% of aviation's total climate forcing
    CONTRAIL_CO2_EQUIV_FACTOR = 0.54  # kg CO2-eq per km of contrail

    def __init__(self):
        # Global regions (order = first match wins). Cruise-level priors for ISSR / humidity.
        self._atmo_regions = self._build_global_atmosphere_regions()

    def predict_contrail_zones(self, route: List[Dict],
                                altitude_ft: float) -> List[Dict]:
        """
        Predict contrail formation probability along a route.

        Returns list of waypoints with contrail risk scores.
        """
        results = []

        for wp in route:
            lat = wp["lat"]
            lon = wp["lon"]
            alt = wp.get("altitude", altitude_ft)

            # Get atmospheric conditions at this point
            atmo = self._get_atmosphere(lat, lon, alt)

            # Schmidt-Appleman criterion (simplified)
            contrail_prob = self._schmidt_appleman(
                atmo["temperature_c"],
                atmo["rh_ice"],
                alt
            )

            # Persistence factor (how long contrail lasts)
            persistence = self._contrail_persistence(
                atmo["rh_ice"],
                atmo["wind_shear"]
            )

            # Climate impact score (0-1)
            # Accounts for: formation probability * persistence * time of day
            climate_score = contrail_prob * persistence * atmo["solar_factor"]

            results.append({
                "lat": lat,
                "lon": lon,
                "altitude": alt,
                "contrail_probability": round(contrail_prob, 3),
                "persistence_hours": round(persistence * 6, 1),  # max 6 hours
                "climate_impact_score": round(climate_score, 3),
                "temperature_c": round(atmo["temperature_c"], 1),
                "rh_ice": round(atmo["rh_ice"], 2),
                "risk_level": self._risk_category(climate_score)
            })

        return results

    def calculate_contrail_warming(self, route: List[Dict],
                                    contrail_zones: List[Dict]) -> Dict:
        """
        Calculate total contrail warming impact for a route.

        Returns warming in CO2-equivalent kg.
        """
        total_contrail_km = 0.0
        high_risk_km = 0.0

        for i in range(1, len(contrail_zones)):
            prev = contrail_zones[i - 1]
            curr = contrail_zones[i]

            segment_km = self._haversine_km(
                prev["lat"], prev["lon"],
                curr["lat"], curr["lon"]
            )

            # Weighted by contrail probability
            contrail_km = segment_km * curr["contrail_probability"]
            total_contrail_km += contrail_km

            if curr["risk_level"] == "HIGH":
                high_risk_km += segment_km

        # Total warming impact
        co2_equiv_kg = total_contrail_km * self.CONTRAIL_CO2_EQUIV_FACTOR
        radiative_forcing_mw = total_contrail_km * self.RF_PER_CONTRAIL_KM

        return {
            "total_contrail_km": round(total_contrail_km, 1),
            "high_risk_km": round(high_risk_km, 1),
            "co2_equivalent_kg": round(co2_equiv_kg, 1),
            "radiative_forcing_mw_m2": round(radiative_forcing_mw, 4),
            "warming_percent_of_co2": round(
                co2_equiv_kg / max(1, total_contrail_km * 0.8) * 100, 1
            )
        }

    def find_contrail_free_altitude(self, lat: float, lon: float,
                                     preferred_alt: float) -> Dict:
        """
        Find nearby altitude that avoids contrail formation.

        Google research shows: small altitude changes (1000-4000 ft)
        can avoid contrail formation entirely.
        """
        test_altitudes = np.arange(
            max(25000, preferred_alt - 4000),
            min(43000, preferred_alt + 4000),
            1000
        )

        best_alt = preferred_alt
        min_risk = 1.0

        alternatives = []
        for alt in test_altitudes:
            atmo = self._get_atmosphere(lat, lon, alt)
            prob = self._schmidt_appleman(
                atmo["temperature_c"], atmo["rh_ice"], alt
            )

            alternatives.append({
                "altitude_ft": int(alt),
                "contrail_probability": round(prob, 3),
                "fuel_penalty_percent": round(
                    abs(alt - preferred_alt) / preferred_alt * 2, 2
                )
            })

            if prob < min_risk:
                min_risk = prob
                best_alt = alt

        fuel_penalty = abs(best_alt - preferred_alt) / preferred_alt * 2

        return {
            "recommended_altitude": int(best_alt),
            "contrail_risk_reduction": round((1 - min_risk) * 100, 1),
            "fuel_penalty_percent": round(fuel_penalty, 2),
            "net_climate_benefit": min_risk < 0.3 and fuel_penalty < 3.0,
            "alternatives": sorted(alternatives, key=lambda x: x["contrail_probability"])[:5]
        }

    def optimize_route_for_contrails(self, route: List[Dict],
                                      aircraft_type: str) -> List[Dict]:
        """
        Modify route to avoid high-risk contrail zones.

        Strategy:
        1. Identify high-risk segments
        2. Find contrail-free altitudes
        3. Accept small fuel penalty for large climate gain
        """
        optimized = []

        for wp in route:
            lat = wp["lat"]
            lon = wp["lon"]
            alt = wp.get("altitude", 35000)

            # Check contrail risk at current altitude
            atmo = self._get_atmosphere(lat, lon, alt)
            risk = self._schmidt_appleman(atmo["temperature_c"], atmo["rh_ice"], alt)

            if risk > 0.6:  # High risk - try to avoid
                alt_result = self.find_contrail_free_altitude(lat, lon, alt)
                if alt_result["net_climate_benefit"]:
                    new_wp = wp.copy()
                    new_wp["altitude"] = alt_result["recommended_altitude"]
                    new_wp["contrail_avoidance"] = True
                    new_wp["original_altitude"] = alt
                    optimized.append(new_wp)
                    continue

            wp_copy = wp.copy()
            wp_copy["contrail_avoidance"] = False
            optimized.append(wp_copy)

        return optimized

    def _schmidt_appleman(self, temp_c: float, rh_ice: float,
                          altitude_ft: float) -> float:
        """
        Simplified Schmidt-Appleman criterion.

        Contrails form when:
        1. Temperature is below threshold (colder = more likely)
        2. Relative humidity over ice is high (more moisture = persist longer)
        3. Altitude is in contrail-prone range (30,000-42,000 ft)
        """
        # Temperature factor
        if temp_c > -30:
            temp_factor = 0.0
        elif temp_c > -40:
            temp_factor = (-30 - temp_c) / 10
        elif temp_c > -60:
            temp_factor = 1.0
        else:
            temp_factor = 0.8  # very cold, less moisture available

        # Humidity factor
        if rh_ice < 0.6:
            hum_factor = 0.0
        elif rh_ice < 0.95:
            hum_factor = (rh_ice - 0.6) / 0.35
        else:
            hum_factor = 1.0

        # Altitude factor (peak at 34,000-38,000 ft)
        alt_kft = altitude_ft / 1000
        if alt_kft < 28 or alt_kft > 43:
            alt_factor = 0.0
        elif 32 <= alt_kft <= 40:
            alt_factor = 1.0
        elif alt_kft < 32:
            alt_factor = (alt_kft - 28) / 4
        else:
            alt_factor = (43 - alt_kft) / 3

        return temp_factor * hum_factor * alt_factor

    def _contrail_persistence(self, rh_ice: float, wind_shear: float) -> float:
        """How long a contrail persists (0 = dissipates immediately, 1 = hours)"""
        if rh_ice < self.RH_ICE_THRESHOLD:
            return max(0, (rh_ice - 0.6) / 0.35) * 0.3  # short-lived
        else:
            # Ice-supersaturated: persistent contrails
            base = 0.7 + 0.3 * min(1, (rh_ice - 0.95) / 0.15)
            # Wind shear spreads contrails (increases coverage but reduces density)
            shear_effect = 1.0 + wind_shear * 0.1
            return min(1.0, base * shear_effect)

    def _risk_category(self, score: float) -> str:
        if score < 0.2:
            return "LOW"
        elif score < 0.5:
            return "MEDIUM"
        else:
            return "HIGH"

    def _build_global_atmosphere_regions(self) -> List[Dict]:
        """
        Ordered bounding boxes (lat_min, lat_max, lon_min, lon_max) + priors.
        First match wins. Covers major international cruise airspace.
        """
        R = lambda la0, la1, lo0, lo1, to, rh, sh: {
            "lat": (la0, la1), "lon": (lo0, lo1),
            "temp_offset": to, "rh_base": rh, "shear_base": sh,
        }
        return [
            R(5, 35, 65, 98, 2, 0.84, 0.32),      # South Asia / monsoon (high ISSR risk)
            R(18, 50, 100, 150, -1, 0.70, 0.35),  # East Asia / Pacific rim
            R(-12, 25, 95, 155, 4, 0.78, 0.22),   # SE Asia / maritime convection
            R(12, 38, 35, 63, 6, 0.52, 0.28),     # Middle East / desert (often drier aloft)
            R(30, 42, -12, 42, 3, 0.68, 0.25),     # Mediterranean / N Africa
            R(45, 72, -25, 45, -3, 0.72, 0.36),   # Northern Europe / W Asia
            R(-48, -10, 110, 180, 0, 0.62, 0.38),  # Australia / NZ / S Pacific
            R(-45, -8, -75, -35, 2, 0.76, 0.22),  # South America (humid tropics)
            R(-36, 5, 8, 52, 4, 0.55, 0.30),      # Sub-Saharan / equatorial Africa
            R(25, 52, -105, -65, -4, 0.70, 0.33), # US East / Canada East
            R(28, 52, -125, -102, 0, 0.48, 0.28), # US West / dry
            R(35, 48, -115, -100, -2, 0.42, 0.45), # US Rockies
        ]

    def _get_atmosphere(self, lat: float, lon: float,
                        altitude_ft: float) -> Dict:
        """Get atmospheric conditions at a point"""
        # Find matching region
        region = self._find_region(lat, lon)

        # ISA temperature at altitude
        isa_temp = 15.0 - (altitude_ft / 1000) * 1.98
        temp = isa_temp + region["temp_offset"]

        # Add some realistic variation
        noise = np.random.normal(0, 2)
        temp += noise

        # Humidity varies with altitude
        # Higher altitude = generally drier, but depends on region
        alt_factor = max(0, 1 - (altitude_ft - 30000) / 20000)
        rh = region["rh_base"] * (0.7 + 0.3 * alt_factor)
        rh += np.random.normal(0, 0.05)
        rh = np.clip(rh, 0.1, 1.1)

        # Solar factor (daytime contrails have different impact)
        solar_factor = 0.7  # average

        return {
            "temperature_c": temp,
            "rh_ice": rh,
            "wind_shear": region["shear_base"] + np.random.normal(0, 0.1),
            "solar_factor": solar_factor
        }

    def _find_region(self, lat: float, lon: float) -> Dict:
        """Find atmospheric region for given coordinates (global)."""
        for box in self._atmo_regions:
            la, lo = box["lat"], box["lon"]
            if la[0] <= lat <= la[1] and lo[0] <= lon <= lo[1]:
                return {
                    "temp_offset": box["temp_offset"],
                    "rh_base": box["rh_base"],
                    "shear_base": box["shear_base"],
                }

        # Default: mid-latitude maritime
        return {"temp_offset": 0, "rh_base": 0.62, "shear_base": 0.30}

    def _haversine_km(self, lat1: float, lon1: float,
                      lat2: float, lon2: float) -> float:
        """Calculate distance in kilometers"""
        R = 6371.0
        lat1_r = math.radians(lat1)
        lat2_r = math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (math.sin(dlat / 2) ** 2 +
             math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2)
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
