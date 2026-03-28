"""
Global airport set (ICAO) for international demo routes.
Coords approximate WGS84 for major hubs.
"""

AIRPORTS = [
    # --- North America ---
    {"code": "KJFK", "name": "John F. Kennedy Intl", "lat": 40.6413, "lon": -73.7781, "city": "New York", "region": "Americas"},
    {"code": "KLAX", "name": "Los Angeles Intl", "lat": 33.9416, "lon": -118.4085, "city": "Los Angeles", "region": "Americas"},
    {"code": "KORD", "name": "Chicago O'Hare", "lat": 41.9742, "lon": -87.9073, "city": "Chicago", "region": "Americas"},
    {"code": "KATL", "name": "Atlanta Hartsfield-Jackson", "lat": 33.6407, "lon": -84.4277, "city": "Atlanta", "region": "Americas"},
    {"code": "KSFO", "name": "San Francisco Intl", "lat": 37.6213, "lon": -122.3790, "city": "San Francisco", "region": "Americas"},
    {"code": "CYYZ", "name": "Toronto Pearson", "lat": 43.6777, "lon": -79.6248, "city": "Toronto", "region": "Americas"},
    {"code": "MMMX", "name": "Mexico City Intl", "lat": 19.4363, "lon": -99.0721, "city": "Mexico City", "region": "Americas"},
    {"code": "SBGR", "name": "Sao Paulo Guarulhos", "lat": -23.4356, "lon": -46.4731, "city": "Sao Paulo", "region": "Americas"},
    # --- Europe ---
    {"code": "EGLL", "name": "London Heathrow", "lat": 51.4700, "lon": -0.4543, "city": "London", "region": "Europe"},
    {"code": "LFPG", "name": "Paris Charles de Gaulle", "lat": 49.0097, "lon": 2.5479, "city": "Paris", "region": "Europe"},
    {"code": "EDDF", "name": "Frankfurt Main", "lat": 50.0379, "lon": 8.5622, "city": "Frankfurt", "region": "Europe"},
    {"code": "EHAM", "name": "Amsterdam Schiphol", "lat": 52.3105, "lon": 4.7683, "city": "Amsterdam", "region": "Europe"},
    {"code": "LEMD", "name": "Madrid Barajas", "lat": 40.4839, "lon": -3.5680, "city": "Madrid", "region": "Europe"},
    {"code": "LIRF", "name": "Rome Fiumicino", "lat": 41.8003, "lon": 12.2389, "city": "Rome", "region": "Europe"},
    {"code": "EKCH", "name": "Copenhagen", "lat": 55.6180, "lon": 12.6560, "city": "Copenhagen", "region": "Europe"},
    {"code": "LOWW", "name": "Vienna Intl", "lat": 48.1103, "lon": 16.5697, "city": "Vienna", "region": "Europe"},
    # --- Middle East / Africa ---
    {"code": "OMDB", "name": "Dubai Intl", "lat": 25.2532, "lon": 55.3657, "city": "Dubai", "region": "Middle East"},
    {"code": "OERK", "name": "Riyadh King Khalid", "lat": 24.9576, "lon": 46.6988, "city": "Riyadh", "region": "Middle East"},
    {"code": "HECA", "name": "Cairo Intl", "lat": 30.1219, "lon": 31.4056, "city": "Cairo", "region": "Africa"},
    {"code": "FACT", "name": "Cape Town Intl", "lat": -33.9648, "lon": 18.6017, "city": "Cape Town", "region": "Africa"},
    # --- Asia Pacific ---
    {"code": "VHHH", "name": "Hong Kong Intl", "lat": 22.3080, "lon": 113.9185, "city": "Hong Kong", "region": "Asia"},
    {"code": "ZSPD", "name": "Shanghai Pudong", "lat": 31.1434, "lon": 121.8053, "city": "Shanghai", "region": "Asia"},
    {"code": "RJTT", "name": "Tokyo Haneda", "lat": 35.5494, "lon": 139.7798, "city": "Tokyo", "region": "Asia"},
    {"code": "RKSI", "name": "Seoul Incheon", "lat": 37.4602, "lon": 126.4407, "city": "Seoul", "region": "Asia"},
    {"code": "VIDP", "name": "Delhi Indira Gandhi", "lat": 28.5562, "lon": 77.1000, "city": "Delhi", "region": "Asia"},
    {"code": "VTBS", "name": "Bangkok Suvarnabhumi", "lat": 13.6811, "lon": 100.7473, "city": "Bangkok", "region": "Asia"},
    {"code": "WSSS", "name": "Singapore Changi", "lat": 1.3644, "lon": 103.9915, "city": "Singapore", "region": "Asia"},
    {"code": "YSSY", "name": "Sydney Kingsford Smith", "lat": -33.9461, "lon": 151.1772, "city": "Sydney", "region": "Oceania"},
    {"code": "NZAA", "name": "Auckland", "lat": -37.0082, "lon": 174.7850, "city": "Auckland", "region": "Oceania"},
]
