import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
import os
import random
import numpy as np
import pandas as pd
import threading
import time
import logging
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def load_config():
    try:
        if os.path.exists('simulation_config.json'):
            with open('simulation_config.json', 'r') as f:
                return json.load(f)
    except:
        pass
    return {
        'num_viewers': 100,
        'cache_size_mb': 100,
        'cache_ttl': 30,
        'origin_latency': 850,
        'origin_city': 'Chennai',
        'cities_enabled': ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad', 'Kolkata'],
        'running': False
    }

config = load_config()

INDIAN_LOCATIONS = {
        'Mumbai': {'lat': 19.0760, 'lon': 72.8777, 'type': 'regional', 'region': 'West'},
    'Chennai': {'lat': 13.0827, 'lon': 80.2707, 'type': 'regional', 'region': 'South'},
    'Delhi': {'lat': 28.7041, 'lon': 77.1025, 'type': 'regional', 'region': 'North'},
    'Bangalore': {'lat': 12.9716, 'lon': 77.5946, 'type': 'regional', 'region': 'South'},
    'Hyderabad': {'lat': 17.3850, 'lon': 78.4867, 'type': 'regional', 'region': 'South'},
    'Kolkata': {'lat': 22.5726, 'lon': 88.3639, 'type': 'regional', 'region': 'East'},
    'Ahmedabad': {'lat': 23.0225, 'lon': 72.5714, 'type': 'regional', 'region': 'West'},
    'Pune': {'lat': 18.5204, 'lon': 73.8567, 'type': 'sub-regional', 'region': 'West'},
    'Jaipur': {'lat': 26.9124, 'lon': 75.7873, 'type': 'sub-regional', 'region': 'North'},
    'Surat': {'lat': 21.1702, 'lon': 72.8311, 'type': 'sub-regional', 'region': 'West'},
    'Lucknow': {'lat': 26.8467, 'lon': 80.9462, 'type': 'sub-regional', 'region': 'North'},
    'Kanpur': {'lat': 26.4499, 'lon': 80.3319, 'type': 'sub-regional', 'region': 'North'},
    'Nagpur': {'lat': 21.1458, 'lon': 79.0882, 'type': 'sub-regional', 'region': 'Central'},
    'Indore': {'lat': 22.7196, 'lon': 75.8577, 'type': 'sub-regional', 'region': 'Central'},
    'Bhopal': {'lat': 23.2599, 'lon': 77.4126, 'type': 'sub-regional', 'region': 'Central'},
    'Visakhapatnam': {'lat': 17.6869, 'lon': 83.2185, 'type': 'sub-regional', 'region': 'South'},
    'Patna': {'lat': 25.5941, 'lon': 85.1376, 'type': 'sub-regional', 'region': 'East'},
    'Vadodara': {'lat': 22.3072, 'lon': 73.1812, 'type': 'sub-regional', 'region': 'West'},
    'Coimbatore': {'lat': 11.0168, 'lon': 76.9558, 'type': 'sub-regional', 'region': 'South'},
    'Ludhiana': {'lat': 30.9010, 'lon': 75.8573, 'type': 'sub-regional', 'region': 'North'},
    'Kochi': {'lat': 9.9312, 'lon': 76.2673, 'type': 'sub-regional', 'region': 'South'},
    'Guwahati': {'lat': 26.1445, 'lon': 91.7362, 'type': 'sub-regional', 'region': 'East'},
    'Chandigarh': {'lat': 30.7333, 'lon': 76.7794, 'type': 'local', 'region': 'North'},
    'Agra': {'lat': 27.1767, 'lon': 78.0081, 'type': 'local', 'region': 'North'},
    'Varanasi': {'lat': 25.3176, 'lon': 82.9739, 'type': 'local', 'region': 'North'},
    'Amritsar': {'lat': 31.6340, 'lon': 74.8723, 'type': 'local', 'region': 'North'},
    'Allahabad': {'lat': 25.4358, 'lon': 81.8463, 'type': 'local', 'region': 'North'},
    'Ranchi': {'lat': 23.3441, 'lon': 85.3096, 'type': 'local', 'region': 'East'},
    'Bhubaneswar': {'lat': 20.2961, 'lon': 85.8245, 'type': 'local', 'region': 'East'},
    'Dehradun': {'lat': 30.3165, 'lon': 78.0322, 'type': 'local', 'region': 'North'},
    'Raipur': {'lat': 21.2514, 'lon': 81.6296, 'type': 'local', 'region': 'Central'},
    'Thiruvananthapuram': {'lat': 8.5241, 'lon': 76.9366, 'type': 'local', 'region': 'South'},
    'Mysuru': {'lat': 12.2958, 'lon': 76.6394, 'type': 'local', 'region': 'South'},
    'Madurai': {'lat': 9.9252, 'lon': 78.1198, 'type': 'local', 'region': 'South'},
    'Tirupati': {'lat': 13.6288, 'lon': 79.4192, 'type': 'local', 'region': 'South'},
    'Vijayawada': {'lat': 16.5062, 'lon': 80.6480, 'type': 'local', 'region': 'South'},
    'Mangalore': {'lat': 12.9141, 'lon': 74.8560, 'type': 'local', 'region': 'South'},
    'Nashik': {'lat': 19.9975, 'lon': 73.7898, 'type': 'local', 'region': 'West'},
    'Aurangabad': {'lat': 19.8762, 'lon': 75.3433, 'type': 'local', 'region': 'West'},
    'Rajkot': {'lat': 22.3039, 'lon': 70.8022, 'type': 'local', 'region': 'West'},
    'Jodhpur': {'lat': 26.2389, 'lon': 73.0243, 'type': 'local', 'region': 'West'},
    'Udaipur': {'lat': 24.5854, 'lon': 73.7125, 'type': 'local', 'region': 'West'},
    'Jammu': {'lat': 32.7266, 'lon': 74.8570, 'type': 'local', 'region': 'North'},
    'Shimla': {'lat': 31.1048, 'lon': 77.1734, 'type': 'local', 'region': 'North'},
    'Gurgaon': {'lat': 28.4595, 'lon': 77.0266, 'type': 'local', 'region': 'North'},
    'Noida': {'lat': 28.5355, 'lon': 77.3910, 'type': 'local', 'region': 'North'},
    'Faridabad': {'lat': 28.4089, 'lon': 77.3178, 'type': 'local', 'region': 'North'},
    'Ghaziabad': {'lat': 28.6692, 'lon': 77.4538, 'type': 'local', 'region': 'North'},
    'Meerut': {'lat': 28.9845, 'lon': 77.7064, 'type': 'local', 'region': 'North'},
    'Vellore': {'lat': 12.9165, 'lon': 79.1325, 'type': 'local', 'region': 'South'},
    'Salem': {'lat': 11.6643, 'lon': 78.1460, 'type': 'local', 'region': 'South'},
    'Trichy': {'lat': 10.7905, 'lon': 78.7047, 'type': 'local', 'region': 'South'},
    'Tirunelveli': {'lat': 8.7139, 'lon': 77.7567, 'type': 'local', 'region': 'South'},
    'Guntur': {'lat': 16.3067, 'lon': 80.4365, 'type': 'local', 'region': 'South'},
    'Warangal': {'lat': 17.9689, 'lon': 79.5941, 'type': 'local', 'region': 'South'},
    'Karimnagar': {'lat': 18.4386, 'lon': 79.1288, 'type': 'local', 'region': 'South'},
    'Rajahmundry': {'lat': 17.0005, 'lon': 81.8040, 'type': 'local', 'region': 'South'},
    'Nellore': {'lat': 14.4426, 'lon': 79.9865, 'type': 'local', 'region': 'South'},
    'Kadapa': {'lat': 14.4673, 'lon': 78.8242, 'type': 'local', 'region': 'South'},
    'Kakinada': {'lat': 16.9891, 'lon': 82.2475, 'type': 'local', 'region': 'South'},
    'Hubli': {'lat': 15.3647, 'lon': 75.1240, 'type': 'local', 'region': 'South'},
    'Belgaum': {'lat': 15.8497, 'lon': 74.4977, 'type': 'local', 'region': 'South'},
    'Gulbarga': {'lat': 17.3297, 'lon': 76.8343, 'type': 'local', 'region': 'South'},
    'Jamshedpur': {'lat': 22.8046, 'lon': 86.2029, 'type': 'local', 'region': 'East'},
    'Dhanbad': {'lat': 23.7957, 'lon': 86.4304, 'type': 'local', 'region': 'East'},
    'Siliguri': {'lat': 26.7271, 'lon': 88.3953, 'type': 'local', 'region': 'East'},
    'Asansol': {'lat': 23.6739, 'lon': 86.9524, 'type': 'local', 'region': 'East'},
    'Durgapur': {'lat': 23.5204, 'lon': 87.3119, 'type': 'local', 'region': 'East'},
    'Panchkula': {'lat': 30.6942, 'lon': 76.8535, 'type': 'village', 'region': 'North'},
    'Mohali': {'lat': 30.7046, 'lon': 76.7179, 'type': 'village', 'region': 'North'},
    'Zirakpur': {'lat': 30.6425, 'lon': 76.8173, 'type': 'village', 'region': 'North'},
    'Dharamshala': {'lat': 32.2190, 'lon': 76.3234, 'type': 'village', 'region': 'North'},
    'Manali': {'lat': 32.2432, 'lon': 77.1892, 'type': 'village', 'region': 'North'},
    'Rishikesh': {'lat': 30.0869, 'lon': 78.2676, 'type': 'village', 'region': 'North'},
    'Haridwar': {'lat': 29.9457, 'lon': 78.1642, 'type': 'village', 'region': 'North'},
    'Muzaffarpur': {'lat': 26.1225, 'lon': 85.3906, 'type': 'village', 'region': 'East'},
    'Purnia': {'lat': 25.7771, 'lon': 87.4753, 'type': 'village', 'region': 'East'},
    'Darbhanga': {'lat': 26.1542, 'lon': 85.9009, 'type': 'village', 'region': 'East'},
    'Bhagalpur': {'lat': 25.2425, 'lon': 86.9842, 'type': 'village', 'region': 'East'},
    'Kurnool': {'lat': 15.8281, 'lon': 78.0373, 'type': 'village', 'region': 'South'},
    'Anantapur': {'lat': 14.6819, 'lon': 77.6006, 'type': 'village', 'region': 'South'},
    'Chittoor': {'lat': 13.2172, 'lon': 79.1003, 'type': 'village', 'region': 'South'},
    'Ongole': {'lat': 15.5057, 'lon': 80.0499, 'type': 'village', 'region': 'South'},
    'Nizamabad': {'lat': 18.6725, 'lon': 78.0941, 'type': 'village', 'region': 'South'},
    'Khammam': {'lat': 17.2473, 'lon': 80.1514, 'type': 'village', 'region': 'South'},
    'Mahbubnagar': {'lat': 16.7378, 'lon': 77.9826, 'type': 'village', 'region': 'South'},
    'Tumkur': {'lat': 13.3392, 'lon': 77.1011, 'type': 'village', 'region': 'South'},
    'Davangere': {'lat': 14.4644, 'lon': 75.9218, 'type': 'village', 'region': 'South'},
    'Bellary': {'lat': 15.1394, 'lon': 76.9214, 'type': 'village', 'region': 'South'},
    'Bijapur': {'lat': 16.8302, 'lon': 75.7100, 'type': 'village', 'region': 'South'},
    'Shimoga': {'lat': 13.9299, 'lon': 75.5681, 'type': 'village', 'region': 'South'},
    'Erode': {'lat': 11.3410, 'lon': 77.7172, 'type': 'village', 'region': 'South'},
    'Thanjavur': {'lat': 10.7870, 'lon': 79.1378, 'type': 'village', 'region': 'South'},
    'Dindigul': {'lat': 10.3673, 'lon': 77.9803, 'type': 'village', 'region': 'South'},
    'Vellankanni': {'lat': 10.6833, 'lon': 79.8333, 'type': 'village', 'region': 'South'},
    'Cuddalore': {'lat': 11.7480, 'lon': 79.7714, 'type': 'village', 'region': 'South'},
    'Kumbakonam': {'lat': 10.9601, 'lon': 79.3845, 'type': 'village', 'region': 'South'},
    'Palakkad': {'lat': 10.7867, 'lon': 76.6548, 'type': 'village', 'region': 'South'},
    'Thrissur': {'lat': 10.5276, 'lon': 76.2144, 'type': 'village', 'region': 'South'},
    'Kannur': {'lat': 11.8745, 'lon': 75.3704, 'type': 'village', 'region': 'South'},
    'Kollam': {'lat': 8.8932, 'lon': 76.6141, 'type': 'village', 'region': 'South'},
    'Alappuzha': {'lat': 9.4981, 'lon': 76.3388, 'type': 'village', 'region': 'South'},
    'Kottayam': {'lat': 9.5916, 'lon': 76.5222, 'type': 'village', 'region': 'South'},
    'Kozhikode': {'lat': 11.2588, 'lon': 75.7804, 'type': 'village', 'region': 'South'},
    'Tiruppur': {'lat': 11.1075, 'lon': 77.3398, 'type': 'village', 'region': 'South'},
    'Karur': {'lat': 10.9601, 'lon': 78.0766, 'type': 'village', 'region': 'South'},
    'Namakkal': {'lat': 11.2189, 'lon': 78.1677, 'type': 'village', 'region': 'South'},
    'Puducherry': {'lat': 11.9416, 'lon': 79.8083, 'type': 'village', 'region': 'South'},
    'Bikaner': {'lat': 28.0229, 'lon': 73.3119, 'type': 'village', 'region': 'North'},
    'Ajmer': {'lat': 26.4499, 'lon': 74.6399, 'type': 'village', 'region': 'North'},
    'Kota': {'lat': 25.2138, 'lon': 75.8648, 'type': 'village', 'region': 'North'},
    'Bharatpur': {'lat': 27.2152, 'lon': 77.4900, 'type': 'village', 'region': 'North'},
    'Alwar': {'lat': 27.5530, 'lon': 76.6346, 'type': 'village', 'region': 'North'},
    'Bhilwara': {'lat': 25.3407, 'lon': 74.6408, 'type': 'village', 'region': 'North'},
    'Sikar': {'lat': 27.6119, 'lon': 75.1397, 'type': 'village', 'region': 'North'},
    'Pali': {'lat': 25.7711, 'lon': 73.3234, 'type': 'village', 'region': 'North'},
    'Gorakhpur': {'lat': 26.7606, 'lon': 83.3732, 'type': 'village', 'region': 'North'},
    'Bareilly': {'lat': 28.3670, 'lon': 79.4304, 'type': 'village', 'region': 'North'},
    'Moradabad': {'lat': 28.8389, 'lon': 78.7378, 'type': 'village', 'region': 'North'},
    'Aligarh': {'lat': 27.8974, 'lon': 78.0880, 'type': 'village', 'region': 'North'},
    'Saharanpur': {'lat': 29.9680, 'lon': 77.5460, 'type': 'village', 'region': 'North'},
    'Mathura': {'lat': 27.4924, 'lon': 77.6737, 'type': 'village', 'region': 'North'},
    'Firozabad': {'lat': 27.1591, 'lon': 78.3957, 'type': 'village', 'region': 'North'},
    'Jhansi': {'lat': 25.4484, 'lon': 78.5685, 'type': 'village', 'region': 'North'},
    'Gwalior': {'lat': 26.2183, 'lon': 78.1828, 'type': 'village', 'region': 'North'},
    'Ujjain': {'lat': 23.1765, 'lon': 75.7885, 'type': 'village', 'region': 'Central'},
    'Jabalpur': {'lat': 23.1815, 'lon': 79.9864, 'type': 'village', 'region': 'Central'},
    'Guna': {'lat': 24.6460, 'lon': 77.3103, 'type': 'village', 'region': 'Central'},
    'Sagar': {'lat': 23.8388, 'lon': 78.7378, 'type': 'village', 'region': 'Central'},
    'Satna': {'lat': 24.6005, 'lon': 80.8322, 'type': 'village', 'region': 'Central'},
    'Ratlam': {'lat': 23.3315, 'lon': 75.0367, 'type': 'village', 'region': 'Central'},
    'Bilaspur': {'lat': 22.0797, 'lon': 82.1409, 'type': 'village', 'region': 'Central'},
    'Korba': {'lat': 22.3595, 'lon': 82.7501, 'type': 'village', 'region': 'Central'},
    'Raigarh': {'lat': 21.8974, 'lon': 83.3950, 'type': 'village', 'region': 'Central'},
    'Bhilai': {'lat': 21.2095, 'lon': 81.3785, 'type': 'village', 'region': 'Central'},
    'Kolhapur': {'lat': 16.7050, 'lon': 74.2433, 'type': 'village', 'region': 'West'},
    'Sangli': {'lat': 16.8524, 'lon': 74.5815, 'type': 'village', 'region': 'West'},
    'Solapur': {'lat': 17.6599, 'lon': 75.9064, 'type': 'village', 'region': 'West'},
    'Nanded': {'lat': 19.1383, 'lon': 77.3210, 'type': 'village', 'region': 'West'},
    'Jalgaon': {'lat': 21.0077, 'lon': 75.5626, 'type': 'village', 'region': 'West'},
    'Amravati': {'lat': 20.9374, 'lon': 77.7796, 'type': 'village', 'region': 'West'},
    'Akola': {'lat': 20.7002, 'lon': 77.0082, 'type': 'village', 'region': 'West'},
    'Latur': {'lat': 18.3983, 'lon': 76.5604, 'type': 'village', 'region': 'West'},
    'Dhule': {'lat': 20.9042, 'lon': 74.7749, 'type': 'village', 'region': 'West'},
    'Ahmednagar': {'lat': 19.0948, 'lon': 74.7480, 'type': 'village', 'region': 'West'},
    'Bhavnagar': {'lat': 21.7645, 'lon': 72.1519, 'type': 'village', 'region': 'West'},
    'Jamnagar': {'lat': 22.4707, 'lon': 70.0577, 'type': 'village', 'region': 'West'},
    'Junagadh': {'lat': 21.5222, 'lon': 70.4579, 'type': 'village', 'region': 'West'},
    'Gandhinagar': {'lat': 23.2156, 'lon': 72.6369, 'type': 'village', 'region': 'West'},
    'Anand': {'lat': 22.5645, 'lon': 72.9289, 'type': 'village', 'region': 'West'},
    'Nadiad': {'lat': 22.6939, 'lon': 72.8618, 'type': 'village', 'region': 'West'},
    'Morbi': {'lat': 22.8173, 'lon': 70.8377, 'type': 'village', 'region': 'West'},
    'Surendranagar': {'lat': 22.7031, 'lon': 71.6371, 'type': 'village', 'region': 'West'},
    'Gandhidham': {'lat': 23.0752, 'lon': 70.1327, 'type': 'village', 'region': 'West'},
}

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def find_nearest_cache(from_city, target_type, enabled_cities, exclude=None):
    if from_city not in INDIAN_LOCATIONS:
        return None
    from_info = INDIAN_LOCATIONS[from_city]
    candidates = []
    for city in enabled_cities:
        if city == from_city or city == exclude or city not in INDIAN_LOCATIONS:
            continue
        city_info = INDIAN_LOCATIONS[city]
        if city_info['type'] == target_type:
            dist = calculate_distance(from_info['lat'], from_info['lon'], city_info['lat'], city_info['lon'])
            candidates.append((city, dist))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[1])
    return candidates[0][0]

def get_cache_hierarchy(from_city, origin_city):
    if from_city == origin_city:
        return [origin_city]
    if from_city not in INDIAN_LOCATIONS or origin_city not in INDIAN_LOCATIONS:
        return [origin_city]
    
    enabled_cities = config.get('cities_enabled', [])
    city_info = INDIAN_LOCATIONS[from_city]
    path = [from_city]
    current = from_city
    
    if city_info['type'] == 'village':
        nearest_local = find_nearest_cache(current, 'local', enabled_cities)
        if nearest_local and nearest_local not in path:
            path.append(nearest_local)
            current = nearest_local
    
    if INDIAN_LOCATIONS[current]['type'] in ['village', 'local']:
        nearest_sub = find_nearest_cache(current, 'sub-regional', enabled_cities)
        if nearest_sub and nearest_sub not in path:
            path.append(nearest_sub)
            current = nearest_sub
    
    if INDIAN_LOCATIONS[current]['type'] in ['village', 'local', 'sub-regional']:
        nearest_regional = find_nearest_cache(current, 'regional', enabled_cities)
        if nearest_regional and nearest_regional not in path:
            path.append(nearest_regional)
            current = nearest_regional
    
    if origin_city not in path:
        path.append(origin_city)
    
    return path

def calculate_latency(path, is_cache_hit):
    if not path:
        return config.get('origin_latency', 850)
    if is_cache_hit:
        return random.randint(15, 35)
    total = 10
    for i in range(1, len(path)):
        loc_type = INDIAN_LOCATIONS.get(path[i], {}).get('type', 'unknown')
        if loc_type == 'origin':
            total += config.get('origin_latency', 850)
        elif loc_type == 'regional':
            total += random.randint(80, 150)
        elif loc_type == 'sub-regional':
            total += random.randint(40, 80)
        elif loc_type == 'local':
            total += random.randint(20, 40)
        else:
            total += random.randint(10, 25)
    return total

class SimulationState:
    def __init__(self):
        self.running = False
        self.viewers = {}
        self.cache_stats = {}
        self.request_log = []
        self.total_hits = 0
        self.total_requests = 0
        self.bandwidth_saved_bytes = 0
        
sim = SimulationState()

def simulation_loop():
    """Simulated CDN loop - works without streaming server"""
    logger.info("🚀 CDN Simulation started")
    warmup_cycles = 0
    
    while sim.running:
        try:
            warmup_cycles += 1
            cache_hit_probability = min(0.85, 0.3 + (warmup_cycles * 0.05))
            segment_size = 500 * 1024  # 500 KB per segment
            
            for viewer_id, viewer_data in list(sim.viewers.items()):
                city = viewer_data['city']
                cache_path = viewer_data['cache_path']
                
                is_hit = len(cache_path) > 1 and random.random() < cache_hit_probability
                latency = calculate_latency(cache_path, is_hit)
                
                sim.total_requests += 1
                if is_hit:
                    sim.total_hits += 1
                    sim.bandwidth_saved_bytes += segment_size
                
                for cache_city in cache_path:
                    if cache_city in sim.cache_stats:
                        sim.cache_stats[cache_city]['requests'] += 1
                        if is_hit and cache_city == cache_path[0]:
                            sim.cache_stats[cache_city]['hits'] += 1
                        elif not is_hit:
                            sim.cache_stats[cache_city]['misses'] += 1
                
                sim.request_log.append({
                    'timestamp': datetime.now(),
                    'viewer_id': viewer_id,
                    'city': city,
                    'path': cache_path,
                    'hit': is_hit,
                    'latency': latency,
                })
            
            if len(sim.request_log) > 1000:
                sim.request_log = sim.request_log[-1000:]
            
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Simulation error: {e}")
            time.sleep(2)

app.layout = html.Div([
    dcc.Interval(id='interval', interval=2000),
    dcc.Interval(id='config-check', interval=3000),
    dcc.Store(id='click-data-store'),
    
    html.Div([
        html.Div([
            html.H1("EdgeStream CDN", style={
                'margin': '0', 'fontSize': '28px', 'fontWeight': '600',
                'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                'WebkitBackgroundClip': 'text', 'WebkitTextFillColor': 'transparent',
            }),
            html.Div(id='status-text', style={'fontSize': '13px', 'color': '#8b92a8', 'marginTop': '4px'})
        ], style={'display': 'inline-block'}),
        
        html.Div(id='live-badge', children='● OFFLINE', style={
            'float': 'right', 'padding': '8px 20px', 'borderRadius': '20px',
            'fontSize': '12px', 'fontWeight': '600',
            'backgroundColor': '#2a2d3a', 'color': '#6b7280'
        })
    ], style={
        'padding': '20px 40px', 'backgroundColor': 'rgba(17, 20, 32, 0.98)',
        'borderBottom': '1px solid rgba(255,255,255,0.05)',
        'position': 'sticky', 'top': '0', 'zIndex': '1000'
    }),
    
    html.Div([
        html.Div([
            dcc.Graph(id='india-map', style={'height': '90vh', 'width': '100%'},
                     config={'displayModeBar': False, 'scrollZoom': False}),
            
            html.Div([
                html.Div('👥', style={'fontSize': '28px', 'marginBottom': '10px', 'opacity': '0.8'}),
                html.Div(id='stat-viewers', children='0', style={
                    'fontSize': '44px', 'fontWeight': '700',
                    'background': 'linear-gradient(135deg, #667eea, #764ba2)',
                    'WebkitBackgroundClip': 'text', 'WebkitTextFillColor': 'transparent',
                    'lineHeight': '1', 'marginBottom': '8px'
                }),
                html.Div('Active Viewers', style={'fontSize': '11px', 'color': '#8b92a8', 'textTransform': 'uppercase'})
            ], style={
                'position': 'absolute', 'top': '30px', 'left': '40px', 'padding': '26px 32px',
                'backgroundColor': 'rgba(17, 20, 32, 0.93)', 'borderRadius': '18px',
                'backdropFilter': 'blur(25px)', 'border': '1px solid rgba(102, 126, 234, 0.25)',
                'boxShadow': '0 10px 40px rgba(0,0,0,0.5)', 'minWidth': '185px',
                'textAlign': 'center', 'zIndex': '10'
            }),
            
            html.Div([
                html.Div('📊', style={'fontSize': '28px', 'marginBottom': '10px', 'opacity': '0.8'}),
                html.Div(id='stat-hitrate', children='0%', style={
                    'fontSize': '44px', 'fontWeight': '700',
                    'background': 'linear-gradient(135deg, #f093fb, #f5576c)',
                    'WebkitBackgroundClip': 'text', 'WebkitTextFillColor': 'transparent',
                    'lineHeight': '1', 'marginBottom': '8px'
                }),
                html.Div(id='stat-hitrate-detail', children='0/0 hits', style={'fontSize': '11px', 'color': '#8b92a8'})
            ], style={
                'position': 'absolute', 'top': '30px', 'right': '40px', 'padding': '26px 32px',
                'backgroundColor': 'rgba(17, 20, 32, 0.93)', 'borderRadius': '18px',
                'backdropFilter': 'blur(25px)', 'border': '1px solid rgba(245, 87, 108, 0.25)',
                'boxShadow': '0 10px 40px rgba(0,0,0,0.5)', 'minWidth': '185px',
                'textAlign': 'center', 'zIndex': '10'
            }),
            
            html.Div([
                html.Div('⚡', style={'fontSize': '28px', 'marginBottom': '10px', 'opacity': '0.8'}),
                html.Div(id='stat-latency', children='0ms', style={
                    'fontSize': '44px', 'fontWeight': '700',
                    'background': 'linear-gradient(135deg, #4facfe, #00f2fe)',
                    'WebkitBackgroundClip': 'text', 'WebkitTextFillColor': 'transparent',
                    'lineHeight': '1', 'marginBottom': '8px'
                }),
                html.Div('Avg Latency', style={'fontSize': '11px', 'color': '#8b92a8', 'textTransform': 'uppercase'})
            ], style={
                'position': 'absolute', 'bottom': '30px', 'left': '40px', 'padding': '26px 32px',
                'backgroundColor': 'rgba(17, 20, 32, 0.93)', 'borderRadius': '18px',
                'backdropFilter': 'blur(25px)', 'border': '1px solid rgba(79, 172, 254, 0.25)',
                'boxShadow': '0 10px 40px rgba(0,0,0,0.5)', 'minWidth': '185px',
                'textAlign': 'center', 'zIndex': '10'
            }),
            
            html.Div([
                html.Div('💾', style={'fontSize': '28px', 'marginBottom': '10px', 'opacity': '0.8'}),
                html.Div(id='stat-bandwidth', children='0 MB', style={
                    'fontSize': '44px', 'fontWeight': '700',
                    'background': 'linear-gradient(135deg, #43e97b, #38f9d7)',
                    'WebkitBackgroundClip': 'text', 'WebkitTextFillColor': 'transparent',
                    'lineHeight': '1', 'marginBottom': '8px'
                }),
                html.Div('Bandwidth Saved', style={'fontSize': '11px', 'color': '#8b92a8', 'textTransform': 'uppercase'})
            ], style={
                'position': 'absolute', 'bottom': '30px', 'right': '40px', 'padding': '26px 32px',
                'backgroundColor': 'rgba(17, 20, 32, 0.93)', 'borderRadius': '18px',
                'backdropFilter': 'blur(25px)', 'border': '1px solid rgba(67, 233, 123, 0.25)',
                'boxShadow': '0 10px 40px rgba(0,0,0,0.5)', 'minWidth': '185px',
                'textAlign': 'center', 'zIndex': '10'
            }),
            
        ], style={'position': 'relative'}),
    ], style={'backgroundColor': '#0f1218', 'marginBottom': '120px'}),
    
    html.Div([
        html.Div([
            html.Div([
                html.H3('🔀 CDN Routing', style={'fontSize': '20px', 'fontWeight': '600', 'color': '#e2e8f0', 'marginBottom': '12px'}),
                html.Div('Click any bubble', style={'fontSize': '13px', 'color': '#64748b', 'marginBottom': '20px'}),
                html.Div(id='location-details', style={'minHeight': '350px'})
            ], style={'flex': '1', 'padding': '30px', 'backgroundColor': 'rgba(17, 20, 32, 0.95)', 'borderRadius': '16px', 'marginRight': '15px', 'border': '1px solid rgba(102, 126, 234, 0.15)'}),
            
            html.Div([
                html.H3('⚡ Live Requests', style={'fontSize': '20px', 'fontWeight': '600', 'color': '#e2e8f0', 'marginBottom': '12px'}),
                html.Div('Green = Hit • Red = Miss', style={'fontSize': '13px', 'color': '#64748b', 'marginBottom': '20px'}),
                html.Div(id='request-log', style={'maxHeight': '350px', 'overflowY': 'auto'})
            ], style={'flex': '1', 'padding': '30px', 'backgroundColor': 'rgba(17, 20, 32, 0.95)', 'borderRadius': '16px', 'marginLeft': '15px', 'border': '1px solid rgba(245, 87, 108, 0.15)'})
        ], style={'display': 'flex', 'marginBottom': '30px'}),
        
        html.Div([
            html.Div([
                html.H3('📈 Cache Performance', style={'fontSize': '20px', 'fontWeight': '600', 'color': '#e2e8f0', 'marginBottom': '15px'}),
                dcc.Graph(id='cache-chart', style={'height': '340px'})
            ], style={'flex': '1', 'padding': '30px', 'backgroundColor': 'rgba(17, 20, 32, 0.95)', 'borderRadius': '16px', 'marginRight': '15px', 'border': '1px solid rgba(79, 172, 254, 0.15)'}),
            
            html.Div([
                html.H3('⏱️ Latency Distribution', style={'fontSize': '20px', 'fontWeight': '600', 'color': '#e2e8f0', 'marginBottom': '15px'}),
                dcc.Graph(id='latency-chart', style={'height': '340px'})
            ], style={'flex': '1', 'padding': '30px', 'backgroundColor': 'rgba(17, 20, 32, 0.95)', 'borderRadius': '16px', 'marginLeft': '15px', 'border': '1px solid rgba(67, 233, 123, 0.15)'})
        ], style={'display': 'flex', 'marginBottom': '30px'}),
        
        html.Div([
            html.Div([
                html.H3('🌏 Regional Distribution', style={'fontSize': '20px', 'fontWeight': '600', 'color': '#e2e8f0', 'marginBottom': '15px'}),
                dcc.Graph(id='regional-chart', style={'height': '340px'})
            ], style={'flex': '1', 'padding': '30px', 'backgroundColor': 'rgba(17, 20, 32, 0.95)', 'borderRadius': '16px', 'marginRight': '15px', 'border': '1px solid rgba(245, 158, 11, 0.15)'}),
            
            html.Div([
                html.H3('📡 Traffic Timeline', style={'fontSize': '20px', 'fontWeight': '600', 'color': '#e2e8f0', 'marginBottom': '15px'}),
                dcc.Graph(id='timeline-chart', style={'height': '340px'})
            ], style={'flex': '1', 'padding': '30px', 'backgroundColor': 'rgba(17, 20, 32, 0.95)', 'borderRadius': '16px', 'marginLeft': '15px', 'border': '1px solid rgba(139, 92, 246, 0.15)'})
        ], style={'display': 'flex', 'marginBottom': '40px'})
        
    ], style={'padding': '40px', 'backgroundColor': '#0f1218', 'paddingTop': '80px'})
    
], style={'backgroundColor': '#0f1218', 'minHeight': '100vh'})

@app.callback(
    [Output('status-text', 'children'),
     Output('live-badge', 'children'),
     Output('live-badge', 'style')],
    Input('config-check', 'n_intervals')
)
def update_header(n):
    config = load_config()
    origin = config.get('origin_city', 'Chennai')
    viewers = config.get('num_viewers', 0)
    running = config.get('running', False)
    
    if running:
        return (
            f"Live from {origin} • {viewers:,} viewers • {len(INDIAN_LOCATIONS)} locations",
            "● LIVE",
            {'float': 'right', 'padding': '8px 20px', 'borderRadius': '20px', 'fontSize': '12px',
             'fontWeight': '600', 'backgroundColor': '#10b981', 'color': '#ffffff'}
        )
    return (
        f"{len(INDIAN_LOCATIONS)} locations available",
        "● OFFLINE",
        {'float': 'right', 'padding': '8px 20px', 'borderRadius': '20px', 'fontSize': '12px',
         'fontWeight': '600', 'backgroundColor': '#2a2d3a', 'color': '#6b7280'}
    )

@app.callback(
    Output('interval', 'disabled'),
    Input('config-check', 'n_intervals')
)
def check_simulation(n):
    global config, sim
    new_config = load_config()
    should_run = new_config.get('running', False)
    
    if should_run and not sim.running:
        config = new_config
        sim.running = True
        sim.viewers = {}
        sim.cache_stats = {city: {'hits': 0, 'misses': 0, 'requests': 0} 
                          for city in config.get('cities_enabled', [])}
        sim.total_hits = 0
        sim.total_requests = 0
        sim.bandwidth_saved_bytes = 0
        
        origin_city = config.get('origin_city', 'Chennai')
        enabled_cities = [c for c in config.get('cities_enabled', []) if c in INDIAN_LOCATIONS]
        
        for i in range(config.get('num_viewers', 100)):
            city = random.choice(enabled_cities)
            cache_path = get_cache_hierarchy(city, origin_city)
            sim.viewers[f"v{i}"] = {'city': city, 'cache_path': cache_path}
        
        threading.Thread(target=simulation_loop, daemon=True).start()
    elif not should_run and sim.running:
        sim.running = False
        sim.viewers = {}
    
    return not sim.running

@app.callback(
    [Output('stat-viewers', 'children'),
     Output('stat-hitrate', 'children'),
     Output('stat-hitrate-detail', 'children'),
     Output('stat-latency', 'children'),
     Output('stat-bandwidth', 'children')],
    Input('interval', 'n_intervals')
)
def update_stats(n):
    hitrate = (sim.total_hits / sim.total_requests * 100) if sim.total_requests > 0 else 0
    
    recent = sim.request_log[-100:] if sim.request_log else []
    avg_latency = np.mean([r['latency'] for r in recent]) if recent else 0
    
    bw_bytes = sim.bandwidth_saved_bytes
    if bw_bytes >= 1024**3:
        bw_display = f"{bw_bytes / (1024**3):.2f} GB"
    elif bw_bytes >= 1024**2:
        bw_display = f"{bw_bytes / (1024**2):.1f} MB"
    elif bw_bytes >= 1024:
        bw_display = f"{bw_bytes / 1024:.1f} KB"
    else:
        bw_display = f"{bw_bytes} B"
    
    return (
        f"{len(sim.viewers):,}",
        f"{hitrate:.1f}%",
        f"{sim.total_hits:,}/{sim.total_requests:,} hits",
        f"{avg_latency:.0f}ms",
        bw_display
    )

@app.callback(
    Output('india-map', 'figure'),
    [Input('interval', 'n_intervals'),
     Input('click-data-store', 'data')]
)
def update_map(n, click_data):
    fig = go.Figure()
    
    fig.update_geos(
        projection_type="mercator",
        showcountries=True,
        countrycolor="rgba(100,116,139,0.2)",
        showcoastlines=True,
        coastlinecolor="rgba(100,116,139,0.3)",
        showland=True,
        landcolor="rgba(17, 20, 32, 0.98)",
        bgcolor="rgba(15, 18, 24, 1)",
        center=dict(lat=20.5937, lon=78.9629),
        lataxis=dict(range=[6, 37]),
        lonaxis=dict(range=[68, 98]),
    )
    
    city_counts = {}
    for v in sim.viewers.values():
        city_counts[v['city']] = city_counts.get(v['city'], 0) + 1
    
    enabled_cities = config.get('cities_enabled', [])
    origin_city = config.get('origin_city', 'Chennai')
    
    for city in enabled_cities:
        if city not in INDIAN_LOCATIONS:
            continue
            
        info = INDIAN_LOCATIONS[city]
        viewer_count = city_counts.get(city, 0)
        
        if city == origin_city:
            color, size = '#f5576c', 42
        elif info['type'] == 'regional':
            color, size = '#667eea', 32
        elif info['type'] == 'sub-regional':
            color, size = '#4facfe', 26
        elif info['type'] == 'local':
            color, size = '#43e97b', 20
        else:
            color, size = '#fbbf24', 16
        
        size += min(viewer_count / 50, 18)
        
        line_width = 5 if (click_data and click_data.get('city') == city) else 2
        line_color = '#fbbf24' if (click_data and click_data.get('city') == city) else 'rgba(255,255,255,0.8)'
        
        fig.add_trace(go.Scattergeo(
            lon=[info['lon']],
            lat=[info['lat']],
            text=None,
            mode='markers',
            marker=dict(size=size, color=color, line=dict(width=line_width, color=line_color), opacity=0.95),
            customdata=[[city]],
            hovertemplate=f"<b>{city}</b><br>Viewers: {viewer_count}<br>Type: {info['type']}<extra></extra>",
            showlegend=False
        ))
    
    drawn = set()
    
    if click_data and click_data.get('city'):
        clicked_city = click_data['city']
        if clicked_city in INDIAN_LOCATIONS:
            path = get_cache_hierarchy(clicked_city, origin_city)
            for i in range(len(path)-1):
                if path[i] in INDIAN_LOCATIONS and path[i+1] in INDIAN_LOCATIONS:
                    from_info = INDIAN_LOCATIONS[path[i]]
                    to_info = INDIAN_LOCATIONS[path[i+1]]
                    fig.add_trace(go.Scattergeo(
                        lon=[from_info['lon'], to_info['lon']],
                        lat=[from_info['lat'], to_info['lat']],
                        mode='lines',
                        line=dict(width=5, color='rgba(251, 191, 36, 0.9)'),
                        hoverinfo='skip',
                        showlegend=False
                    ))
                    drawn.add(f"{path[i]}-{path[i+1]}")
    
    for v in list(sim.viewers.values())[:100]:
        path = v['cache_path']
        for i in range(len(path)-1):
            key = f"{path[i]}-{path[i+1]}"
            if key in drawn or path[i] not in INDIAN_LOCATIONS or path[i+1] not in INDIAN_LOCATIONS:
                continue
            drawn.add(key)
            from_info = INDIAN_LOCATIONS[path[i]]
            to_info = INDIAN_LOCATIONS[path[i+1]]
            
            if path[i+1] == origin_city:
                line_color, width = 'rgba(245, 87, 108, 0.3)', 1.5
            else:
                line_color, width = 'rgba(102, 126, 234, 0.25)', 1
            
            fig.add_trace(go.Scattergeo(
                lon=[from_info['lon'], to_info['lon']],
                lat=[from_info['lat'], to_info['lat']],
                mode='lines',
                line=dict(width=width, color=line_color),
                hoverinfo='skip',
                showlegend=False
            ))
    
    fig.update_layout(
        title=None,
        height=900,
        margin=dict(l=0,r=0,t=0,b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        geo=dict(bgcolor='rgba(0,0,0,0)', framecolor='rgba(0,0,0,0)', framewidth=0),
        dragmode=False
    )
    
    return fig

@app.callback(
    [Output('click-data-store', 'data'),
     Output('location-details', 'children')],
    Input('india-map', 'clickData'),
    prevent_initial_call=True
)
def display_click_info(clickData):
    if not clickData:
        return None, html.Div("Click location", style={'color': '#64748b', 'textAlign': 'center', 'padding': '60px'})
    
    city = clickData['points'][0]['customdata'][0]
    origin_city = config.get('origin_city', 'Chennai')
    path = get_cache_hierarchy(city, origin_city)
    
    cdn_latency = 25
    origin_latency = 10
    
    for i in range(1, len(path)):
        loc_type = INDIAN_LOCATIONS.get(path[i], {}).get('type', 'unknown')
        if loc_type == 'origin':
            origin_latency += 850
        elif loc_type == 'regional':
            origin_latency += 120
        elif loc_type == 'sub-regional':
            origin_latency += 60
        elif loc_type == 'local':
            origin_latency += 30
        else:
            origin_latency += 20
    
    reduction_pct = ((origin_latency - cdn_latency) / origin_latency * 100) if origin_latency > 0 else 0
    
    distances = []
    for i in range(len(path)-1):
        if path[i] in INDIAN_LOCATIONS and path[i+1] in INDIAN_LOCATIONS:
            from_info = INDIAN_LOCATIONS[path[i]]
            to_info = INDIAN_LOCATIONS[path[i+1]]
            dist = calculate_distance(from_info['lat'], from_info['lon'], to_info['lat'], to_info['lon'])
            distances.append(dist)
    
    header = html.Div([
        html.H4(f"{city} → {origin_city}", style={'color': '#e2e8f0', 'marginBottom': '25px', 'fontSize': '22px'}),
        
        html.Div([
            html.Div([
                html.Div('Without CDN', style={'fontSize': '13px', 'color': '#ef4444', 'marginBottom': '10px', 'fontWeight': '600'}),
                html.Div(f"{origin_latency}ms", style={'fontSize': '42px', 'fontWeight': '700', 'color': '#ef4444'}),
            ], style={'flex': '1', 'padding': '24px', 'backgroundColor': 'rgba(239, 68, 68, 0.08)', 'borderRadius': '14px', 'border': '2px solid rgba(239, 68, 68, 0.3)', 'textAlign': 'center'}),
            
            html.Div([
                html.Div('→', style={'fontSize': '40px', 'color': '#8b92a8'}),
                html.Div(f"{reduction_pct:.0f}% faster", style={'fontSize': '16px', 'color': '#10b981', 'fontWeight': '700', 'marginTop': '10px'})
            ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center', 'padding': '0 25px'}),
            
            html.Div([
                html.Div('With CDN', style={'fontSize': '13px', 'color': '#10b981', 'marginBottom': '10px', 'fontWeight': '600'}),
                html.Div(f"{cdn_latency}ms", style={'fontSize': '42px', 'fontWeight': '700', 'color': '#10b981'}),
            ], style={'flex': '1', 'padding': '24px', 'backgroundColor': 'rgba(16, 185, 129, 0.08)', 'borderRadius': '14px', 'border': '2px solid rgba(16, 185, 129, 0.3)', 'textAlign': 'center'})
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '30px'}),
        
        html.H5('Routing Path:', style={'color': '#e2e8f0', 'marginBottom': '15px', 'fontSize': '16px'}),
    ])
    
    details = [header]
    
    icon_colors = {
        'origin': ('🎯', '#f5576c'),
        'regional': ('🌐', '#667eea'),
        'sub-regional': ('📡', '#4facfe'),
        'local': ('📍', '#43e97b'),
        'village': ('🏘️', '#fbbf24')
    }
    
    for i, loc in enumerate(path):
        loc_info = INDIAN_LOCATIONS.get(loc, {})
        loc_type = loc_info.get('type', 'unknown')
        dist_text = f"{distances[i-1]:.1f} km" if i > 0 and i-1 < len(distances) else ""
        icon, color = icon_colors.get(loc_type, ('●', '#8b92a8'))
        
        details.append(html.Div([
            html.Div([
                html.Span(icon, style={'fontSize': '22px', 'marginRight': '14px'}),
                html.Span(loc, style={'fontSize': '17px', 'color': '#e2e8f0', 'fontWeight': '600'}),
                html.Span(f" ({loc_type})", style={'fontSize': '13px', 'color': '#8b92a8', 'marginLeft': '8px'})
            ], style={'marginBottom': '8px'}),
            html.Div(dist_text, style={'fontSize': '13px', 'color': '#64748b', 'marginBottom': '10px'}),
            (html.Div("↓", style={'textAlign': 'center', 'fontSize': '24px', 'margin': '12px 0', 'color': color, 'opacity': '0.4'}) 
             if i < len(path)-1 else None)
        ], style={
            'padding': '18px 22px', 'backgroundColor': 'rgba(30, 35, 48, 0.6)',
            'borderRadius': '12px', 'marginBottom': '12px',
            'borderLeft': f'4px solid {color}'
        }))
    
    return {'city': city}, details

@app.callback(
    Output('request-log', 'children'),
    Input('interval', 'n_intervals')
)
def update_log(n):
    if not sim.request_log:
        return html.Div("Waiting...", style={'color': '#64748b', 'textAlign': 'center', 'padding': '60px'})
    
    entries = []
    for req in sim.request_log[-25:][::-1]:
        icon = '●' if req['hit'] else '○'
        color = '#10b981' if req['hit'] else '#ef4444'
        status = 'HIT' if req['hit'] else 'MISS'
        
        entries.append(html.Div([
            html.Span(icon, style={'color': color, 'marginRight': '14px', 'fontSize': '16px'}),
            html.Span(req['city'], style={'fontSize': '15px', 'color': '#e2e8f0', 'fontWeight': '500', 'marginRight': '18px', 'minWidth': '120px', 'display': 'inline-block'}),
            html.Span(f"{req['latency']:.0f}ms", style={'fontSize': '14px', 'color': color, 'fontWeight': '600', 'marginRight': '12px'}),
            html.Span(status, style={'fontSize': '12px', 'color': color, 'opacity': '0.7'})
        ], style={'padding': '12px 0', 'borderBottom': '1px solid rgba(255,255,255,0.05)'}))
    
    return entries

@app.callback(
    Output('cache-chart', 'figure'),
    Input('interval', 'n_intervals')
)
def update_cache_chart(n):
    if not sim.cache_stats:
        fig = go.Figure()
        fig.add_annotation(text="No data yet", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16, color='#64748b'))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=340, margin=dict(l=0,r=0,t=0,b=0))
        return fig
    
    cities = []
    hitrates = []
    
    for city, stats in sim.cache_stats.items():
        if stats['requests'] > 10:
            cities.append(city)
            hitrates.append((stats['hits'] / stats['requests']) * 100)
    
    if not cities:
        fig = go.Figure()
        fig.add_annotation(text="Collecting data...", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16, color='#64748b'))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=340, margin=dict(l=0,r=0,t=0,b=0))
        return fig
    
    df = pd.DataFrame({'City': cities, 'Hit Rate': hitrates})
    df = df.sort_values('Hit Rate', ascending=False).head(10)
    
    fig = px.bar(df, x='City', y='Hit Rate', color='Hit Rate', color_continuous_scale='RdYlGn', text='Hit Rate')
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', size=12),
        xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title=''),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='Hit Rate (%)', range=[0, 100]),
        margin=dict(l=40, r=20, t=20, b=40),
        showlegend=False,
        height=340
    )
    
    return fig

@app.callback(
    Output('latency-chart', 'figure'),
    Input('interval', 'n_intervals')
)
def update_latency_chart(n):
    if not sim.request_log:
        fig = go.Figure()
        fig.add_annotation(text="No data yet", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16, color='#64748b'))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=340, margin=dict(l=0,r=0,t=0,b=0))
        return fig
    
    recent = sim.request_log[-200:]
    latencies = [r['latency'] for r in recent]
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=latencies,
        nbinsx=25,
        marker=dict(color='#4facfe', line=dict(color='rgba(255,255,255,0.2)', width=1))
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', size=12),
        xaxis=dict(title='Latency (ms)', gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(title='Frequency', gridcolor='rgba(255,255,255,0.05)'),
        margin=dict(l=40, r=20, t=20, b=40),
        showlegend=False,
        height=340
    )
    
    return fig

@app.callback(
    Output('regional-chart', 'figure'),
    Input('interval', 'n_intervals')
)
def update_regional_chart(n):
    if not sim.viewers:
        fig = go.Figure()
        fig.add_annotation(text="No data yet", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16, color='#64748b'))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=340, margin=dict(l=0,r=0,t=0,b=0))
        return fig
    
    regions = {}
    for v in sim.viewers.values():
        city = v['city']
        if city in INDIAN_LOCATIONS:
            region = INDIAN_LOCATIONS[city]['region']
            regions[region] = regions.get(region, 0) + 1
    
    fig = go.Figure(data=[go.Pie(
        labels=list(regions.keys()),
        values=list(regions.values()),
        hole=0.5,
        marker=dict(colors=['#667eea', '#f5576c', '#4facfe', '#43e97b', '#fbbf24'])
    )])
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', size=13),
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=True,
        legend=dict(font=dict(size=12), orientation='v'),
        height=340
    )
    
    return fig

@app.callback(
    Output('timeline-chart', 'figure'),
    Input('interval', 'n_intervals')
)
def update_timeline_chart(n):
    if not sim.request_log:
        fig = go.Figure()
        fig.add_annotation(text="No data yet", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16, color='#64748b'))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=340, margin=dict(l=0,r=0,t=0,b=0))
        return fig
    
    recent = sim.request_log[-60:]
    times = [r['timestamp'] for r in recent]
    latencies = [r['latency'] for r in recent]
    hits = [r['hit'] for r in recent]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times,
        y=latencies,
        mode='markers+lines',
        marker=dict(
            size=8,
            color=['#10b981' if h else '#ef4444' for h in hits]
        ),
        line=dict(color='#667eea', width=2)
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', size=12),
        xaxis=dict(title='Time', gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(title='Latency (ms)', gridcolor='rgba(255,255,255,0.05)'),
        margin=dict(l=40, r=20, t=20, b=40),
        showlegend=False,
        height=340
    )
    
    return fig

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🗺️ EdgeStream CDN Visualization - WORKING VERSION")
    print("="*80)
    print("🌐 http://localhost:8051/")
    print(f"📍 {len(INDIAN_LOCATIONS)} locations")
    print("\n✅ FIXED:")
    print("   • Hit rate calculation (uses total_requests)")
    print("   • Bandwidth tracking (proper byte counting)")
    print("   • Latency statistics (working)")
    print("   • Simulated mode (no streaming server needed)")
    print("   • All 4 graphs working")
    print("="*80 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=8051)
