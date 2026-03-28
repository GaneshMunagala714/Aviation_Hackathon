"""
4D trajectory enrichment: add cumulative time (ETA) per waypoint.

4D = latitude, longitude, altitude (ft MSL), time (minutes from brake release).
"""

from typing import List, Dict
import math


def _haversine_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 3440.065
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _recompute_distance_cumulative(waypoints: List[Dict]) -> None:
    """
    NM along the actual lat/lon polyline. Required when lateral offsets or
    climate corridors make path length differ from ratio * great-circle distance.
    """
    if not waypoints:
        return
    waypoints[0]["distance_cumulative"] = 0.0
    cum = 0.0
    for i in range(1, len(waypoints)):
        prev = waypoints[i - 1]
        w = waypoints[i]
        seg = _haversine_nm(
            float(prev["lat"]),
            float(prev["lon"]),
            float(w["lat"]),
            float(w["lon"]),
        )
        cum += seg
        w["distance_cumulative"] = round(cum, 2)


def enrich_waypoints_4d(waypoints: List[Dict], wind_data: Dict) -> List[Dict]:
    if not waypoints:
        return []

    # Copy so callers' dicts are not mutated; fix distance before time integration
    track: List[Dict] = [dict(w) for w in waypoints]
    _recompute_distance_cumulative(track)

    headwind = float(wind_data.get("average_headwind", 0) or 0)
    out: List[Dict] = []
    t_cum = 0.0

    for i, w in enumerate(track):
        wp = dict(w)
        if i == 0:
            wp["time_cumulative_min"] = 0.0
            wp["flight_phase"] = "GND"
            out.append(wp)
            continue

        prev = track[i - 1]
        dist_nm = _haversine_nm(
            prev["lat"], prev["lon"], w["lat"], w["lon"]
        )

        alt = float(w.get("altitude", 0) or 0)
        prev_alt = float(prev.get("altitude", 0) or 0)

        if alt > prev_alt + 500:
            tas = 280.0
            phase = "CLB"
        elif alt < prev_alt - 500:
            tas = 260.0
            phase = "DES"
        else:
            tas = 450.0
            phase = "CRZ"

        gs = max(160.0, tas - headwind)
        segment_h = dist_nm / gs
        t_cum += segment_h * 60.0

        wp["time_cumulative_min"] = round(t_cum, 2)
        wp["flight_phase"] = phase
        wp["segment_distance_nm"] = round(dist_nm, 2)
        wp["segment_groundspeed_kts"] = round(gs, 1)
        out.append(wp)

    total_min = out[-1]["time_cumulative_min"] if out else 0.0
    for wp in out:
        wp["block_time_min"] = round(total_min, 2)

    return out
