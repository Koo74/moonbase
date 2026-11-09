"""
MoonBase v2.2.0
===============
Lunar Site Selection & Sweet Spot Analysis.
Based on NASA LRO / Artemis mission criteria.
UI: Cyberpunk Silver/Cyan theme.
Map: NASA LRO WAC Global Mosaic (tile layer).

CHANGELOG v2.2.0:
  - ADDED: 🎲 Mission Randomizer / "Surprise Me"
  - ADDED: 💧 Water Production Calculator
  - ADDED: ☢️ Radiation Shield Depth Calculator
  - ADDED: 🌅 Sun Position Animation

CHANGELOG v2.1.0:
  - ADDED: Compare Mode (2-3 Sites Side-by-Side)
  - ADDED: Artemis III Landing Zones Overlay Toggle
  - ADDED: Elevation Cross-Section Chart
  - REMOVED: PDF export (to avoid dependency issues)

CHANGELOG v2.0.1:
  - ADDED: Click-Anywhere dynamic site generation (matches VenusBase).
"""

import streamlit as st
import folium
from folium.plugins import Fullscreen, MousePosition
from folium.raster_layers import ImageOverlay
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from abc import ABC
import math
import sqlite3
import pickle
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import os
import base64
import streamlit.components.v1 as components
import tempfile

# ============================================================================
# MOON CYBERPUNK STYLING (Silver / Cyan)
# ============================================================================

MOON_CSS = """
<style>
    :root {
        --moon-cyan: #00f0ff;
        --moon-silver: #a0a0c0;
        --moon-white: #ffffff;
        --moon-purple: #b026ff;
        --moon-pink: #ff2d95;
    }
    .stApp { background: linear-gradient(135deg, #050510 0%, #0a0a1a 50%, #050510 100%); }
    .main-title {
        font-family: 'Courier New', monospace;
        font-size: 3.5rem; font-weight: 900;
        background: linear-gradient(90deg, #00f0ff, #a0a0c0, #ffffff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-shadow: 0 0 40px rgba(0, 240, 255, 0.4);
        letter-spacing: 4px; animation: moonGlow 3s ease-in-out infinite;
    }
    @keyframes moonGlow {
        0%, 100% { text-shadow: 0 0 40px rgba(0, 240, 255, 0.4); }
        50% { text-shadow: 0 0 60px rgba(0, 240, 255, 0.7), 0 0 80px rgba(160, 160, 192, 0.4); }
    }
    .subtitle {
        font-family: 'Courier New', monospace; color: #00f0ff;
        font-size: 1.1rem; letter-spacing: 6px;
        text-shadow: 0 0 20px rgba(0, 240, 255, 0.4);
        border-bottom: 1px solid rgba(0, 240, 255, 0.3);
        padding-bottom: 10px; margin-bottom: 20px;
    }
    .phase-badge {
        display: inline-block; padding: 4px 15px; border-radius: 20px;
        font-family: 'Courier New', monospace; font-size: 0.7rem;
        letter-spacing: 2px; text-transform: uppercase; font-weight: bold;
        margin: 0 5px; border: 1px solid;
    }
    .phase-badge-2 { color: #00f0ff; border-color: #00f0ff; background: rgba(0,240,255,0.05); }
    .phase-badge-3 { color: #39ff14; border-color: #39ff14; background: rgba(57,255,20,0.05); }
    .phase-badge-4 { color: #ffffff; border-color: #ffffff; background: rgba(255,255,255,0.05); }
    .phase-badge-5 { color: #ff2d95; border-color: #ff2d95; background: rgba(255,45,149,0.05); }
    .recommendation-container {
        background: rgba(10, 10, 25, 0.85);
        border: 1px solid rgba(0, 240, 255, 0.25);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
    .recommendation-title {
        color: #00f0ff; font-family: 'Courier New', monospace;
        font-size: 1.2rem; font-weight: bold; letter-spacing: 2px;
        margin-bottom: 10px;
    }
    .recommendation-item {
        color: #ffffff; font-family: 'Courier New', monospace;
        font-size: 0.9rem; padding: 6px 0;
        border-bottom: 1px solid rgba(0, 240, 255, 0.08);
    }
    .stButton > button {
        background: linear-gradient(135deg, rgba(0, 240, 255, 0.15), rgba(160, 160, 192, 0.15)) !important;
        border: 1px solid rgba(0, 240, 255, 0.5) !important;
        color: #00f0ff !important;
        font-family: 'Courier New', monospace !important;
        font-weight: bold !important; text-transform: uppercase !important;
        letter-spacing: 2px !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(0, 240, 255, 0.3), rgba(160, 160, 192, 0.3)) !important;
        border-color: #00f0ff !important;
        color: #ffffff !important;
    }
    [data-testid="metric-container"] {
        background: rgba(10, 10, 25, 0.8);
        border: 1px solid rgba(0, 240, 255, 0.2);
        border-radius: 10px; padding: 15px;
    }
    [data-testid="metric-container"] label { color: #00f0ff !important; }
    [data-testid="metric-container"] div { color: #ffffff !important; }
    .cyber-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #00f0ff, #a0a0c0, #ffffff, transparent);
        margin: 20px 0; opacity: 0.6;
    }
    .stMarkdown p, .stMarkdown li { color: #ffffff !important; }
    .stMarkdown h1 { color: #00f0ff !important; }
    .stMarkdown h2 { color: #a0a0c0 !important; }
    .stMarkdown h3 { color: #ffffff !important; }
    .moon-banner {
        background: linear-gradient(135deg, rgba(0, 240, 255, 0.15), rgba(160, 160, 192, 0.10));
        border: 1px solid rgba(0, 240, 255, 0.3);
        border-radius: 10px; padding: 12px 20px; margin: 10px 0;
        text-align: center; font-family: 'Courier New', monospace;
    }
    .delta-v-box {
        background: linear-gradient(135deg, rgba(0, 240, 255, 0.1), rgba(160, 160, 192, 0.1));
        border: 1px solid rgba(0, 240, 255, 0.4);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
    .climate-box {
        background: linear-gradient(135deg, rgba(160, 160, 192, 0.1), rgba(0, 240, 255, 0.1));
        border: 1px solid rgba(160, 160, 192, 0.4);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
    .nasa-trek-box {
        background: linear-gradient(135deg, rgba(255, 45, 149, 0.1), rgba(176, 38, 255, 0.1));
        border: 1px solid rgba(255, 45, 149, 0.4);
        border-radius: 12px; padding: 20px; margin: 15px 0;
        text-align: center;
    }
    .blocked-score {
        background: rgba(255, 45, 149, 0.15) !important;
        border: 2px solid #ff2d95 !important;
        border-radius: 10px; padding: 20px; margin: 10px 0; text-align: center;
    }
    .subsurface-box {
        background: linear-gradient(135deg, rgba(176, 38, 255, 0.1), rgba(255, 45, 149, 0.1));
        border: 1px solid rgba(176, 38, 255, 0.4);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
    .winner-badge {
        background: linear-gradient(135deg, #39ff14, #00f0ff);
        color: #000; font-weight: bold; padding: 4px 12px;
        border-radius: 20px; font-size: 0.8rem;
    }
    .water-box {
        background: linear-gradient(135deg, rgba(0, 150, 255, 0.1), rgba(0, 240, 255, 0.1));
        border: 1px solid rgba(0, 150, 255, 0.4);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
    .radiation-box {
        background: linear-gradient(135deg, rgba(255, 200, 0, 0.1), rgba(255, 45, 149, 0.1));
        border: 1px solid rgba(255, 200, 0, 0.4);
        border-radius: 12px; padding: 20px; margin: 15px 0;
    }
</style>
"""

# ============================================================================
# MOON MAP — NASA LRO WAC GLOBAL MOSAIC
# ============================================================================

MOON_TILES = "https://trek.nasa.gov/tiles/Moon/EQ/LRO_WAC_Mosaic_Global_303ppd_v02/1.0.0/default/default028mm/{z}/{y}/{x}.jpg"

# Artemis III Candidate Landing Regions (NASA, 2022)
ARTEMIS_III_SITES = {
    "Connecting Ridge": [-89.45, 222.7],
    "Connecting Ridge Extension": [-89.3, 210.0],
    "de Gerlache Rim 2": [-88.5, 68.0],
    "Haworth": [-87.0, 4.0],
    "Malapert Massif": [-86.0, 0.0],
    "Mons Mouton": [-84.0, 30.0],
    "Mons Mouton Plateau": [-84.5, 31.0],
    "Nobile Rim 1": [-85.4, 53.0],
    "Nobile Rim 2": [-85.2, 51.0],
    "Peak near Cabeus B": [-85.0, -40.0],
    "Slater Plain": [-88.0, 150.0],
    "Leibnitz Beta Plateau": [-87.0, -30.0],
    "Shackleton Connecting Ridge": [-89.7, 222.0],
}

# ============================================================================
# LUNAR SCIENCE ENGINE
# ============================================================================

def compute_moon_delta_v(lat_deg: float) -> Dict:
    dv_earth = 2400.0
    dv_leo = 5900.0
    R_moon = 1737.4
    rotation_period_days = 27.3
    v_rotation = (2 * math.pi * R_moon * 1000) / (rotation_period_days * 86400)
    v_rotation_site = v_rotation * math.cos(math.radians(lat_deg))
    
    return {
        'dv_earth': dv_earth,
        'dv_leo': dv_leo,
        'rotation_speed': round(v_rotation_site, 3),
        'travel_time_days': 3,
    }

def fetch_moon_climate_model(lat_deg: float, illum_pct: float) -> Dict:
    if illum_pct > 80:
        temp_c = 80.0
    elif illum_pct > 50:
        temp_c = 20.0
    elif illum_pct > 20:
        temp_c = -50.0
    else:
        temp_c = -150.0
    
    return {
        'temperature_c': temp_c,
        'pressure_atm': 0.0,
        'radiation_msv_year': 500.0,
        'solar_wind': 'Direct (no magnetosphere)',
        'source': 'NASA LRO Diviner / LAMP'
    }

# ============================================================================
# SEASONAL ILLUMINATION MODEL
# ============================================================================

def get_seasonal_illumination(base_illum: float, lat: float, year: int) -> float:
    year_offset = (year - 2026) % 19
    cycle_phase = (2 * math.pi * year_offset) / 18.6
    amplitude = 15.0 * (abs(lat) / 90.0)
    drift = amplitude * math.sin(cycle_phase)
    return max(0.0, min(100.0, base_illum + drift))

# ============================================================================
# 🆕 FEATURE 2: WATER PRODUCTION CALCULATOR
# ============================================================================

def water_production_estimate(rd: Dict, regolith_kg_per_day: float = 5000.0) -> Dict:
    """Estimate liters of water per day from ISRU processing at this site."""
    ice = rd.get('ice_confidence', 0.0)
    # NASA baseline: ~5% water by mass in ice-rich regolith
    water_fraction = 0.05 * ice
    water_kg_day = regolith_kg_per_day * water_fraction
    water_l_day = water_kg_day  # ~1 kg water = 1 L
    crew_need_l_day = 150.0  # 10-crew baseline
    crew_supported = water_l_day / crew_need_l_day if crew_need_l_day > 0 else 0
    return {
        'water_l_day': round(water_l_day, 1),
        'water_kg_day': round(water_kg_day, 1),
        'regolith_processed_kg_day': regolith_kg_per_day,
        'ice_fraction': round(ice, 3),
        'crew_supported': round(crew_supported, 1),
        'viable': water_l_day > 100.0,
    }

# ============================================================================
# 🆕 FEATURE 3: RADIATION SHIELD DEPTH CALCULATOR
# ============================================================================

def radiation_shield_estimate(rd: Dict, target_msv_year: float = 50.0) -> Dict:
    """Estimate regolith depth needed to reach target radiation dose."""
    surface_msv = 500.0
    # Regolith attenuation: ~e^(-depth / attenuation_length), attenuation_length ~ 0.3 m
    attenuation_length_m = 0.3
    if target_msv_year >= surface_msv:
        depth_needed = 0.0
    else:
        depth_needed = attenuation_length_m * math.log(surface_msv / target_msv_year)
    lava = rd.get('lava_tube_proximity', 'None')
    has_lava_shield = (lava == 'Nearby')
    regolith_available = rd.get('regolith_depth_m', 5.0)
    can_dig_in = regolith_available >= depth_needed
    return {
        'surface_msv_year': surface_msv,
        'target_msv_year': target_msv_year,
        'depth_needed_m': round(depth_needed, 2),
        'regolith_available_m': round(regolith_available, 1),
        'can_dig_in': can_dig_in,
        'has_lava_shield': has_lava_shield,
        'recommendation': (
            'Lava tube provides natural shielding — no excavation needed.'
            if has_lava_shield else
            f'Need {depth_needed:.2f} m of regolith overburden.' if not can_dig_in
            else 'Sufficient regolith for buried habitat.'
        ),
    }

# ============================================================================
# LUNAR DATA (14 Sites + Lava Tubes)
# ============================================================================

MOON_SITES = {
    'Shackleton Crater Rim': {
        'lat': -89.90, 'lon': 0.0, 'region': 'south_pole',
        'illumination_pct': 86, 'ice_confidence': 0.85,
        'slope_deg': 12, 'temperature_k': 270,
        'regolith_depth_m': 6, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'None', 'skylight_distance_km': 999,
        'notes': 'Highest illumination at South Pole; abundant ice in adjacent PSR.',
    },
    'Connecting Ridge (Site 001)': {
        'lat': -89.45, 'lon': 222.7, 'region': 'south_pole',
        'illumination_pct': 92, 'ice_confidence': 0.80,
        'slope_deg': 10, 'temperature_k': 280,
        'regolith_depth_m': 5, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'None', 'skylight_distance_km': 999,
        'notes': 'Artemis III candidate; near-constant sunlight + ice access.',
    },
    'de Gerlache Rim 1': {
        'lat': -88.50, 'lon': 88.0, 'region': 'south_pole',
        'illumination_pct': 78, 'ice_confidence': 0.75,
        'slope_deg': 8, 'temperature_k': 290,
        'regolith_depth_m': 7, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'Nearby', 'skylight_distance_km': 15,
        'notes': 'Low-slope rim near ice-bearing de Gerlache crater.',
    },
    'Cabeus Crater Rim': {
        'lat': -85.3, 'lon': -42.0, 'region': 'south_pole',
        'illumination_pct': 55, 'ice_confidence': 0.90,
        'slope_deg': 13, 'temperature_k': 240,
        'regolith_depth_m': 5, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'Nearby', 'skylight_distance_km': 20,
        'notes': 'LCROSS impact confirmed water ice; lower illumination.',
    },
    'Malapert Massif': {
        'lat': -86.0, 'lon': 0.0, 'region': 'south_pole',
        'illumination_pct': 80, 'ice_confidence': 0.55,
        'slope_deg': 18, 'temperature_k': 310,
        'regolith_depth_m': 4, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'None', 'skylight_distance_km': 999,
        'notes': 'Excellent Earth visibility; slope is challenging.',
    },
    'Haworth Crater Rim': {
        'lat': -87.0, 'lon': 4.0, 'region': 'south_pole',
        'illumination_pct': 65, 'ice_confidence': 0.72,
        'slope_deg': 11, 'temperature_k': 265,
        'regolith_depth_m': 6, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'Nearby', 'skylight_distance_km': 12,
        'notes': 'Ice-rich Haworth crater nearby.',
    },
    'Mons Mouton Plateau': {
        'lat': -84.5, 'lon': 31.0, 'region': 'south_pole',
        'illumination_pct': 85, 'ice_confidence': 0.50,
        'slope_deg': 5, 'temperature_k': 295,
        'regolith_depth_m': 8, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'None', 'skylight_distance_km': 999,
        'notes': 'Artemis III candidate; excellent flat plateau.',
    },
    'Mons Mouton': {
        'lat': -84.0, 'lon': 30.0, 'region': 'south_pole',
        'illumination_pct': 82, 'ice_confidence': 0.45,
        'slope_deg': 7, 'temperature_k': 290,
        'regolith_depth_m': 7, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'None', 'skylight_distance_km': 999,
        'notes': 'Large flat region; good for base construction.',
    },
    'Nobile Rim 1': {
        'lat': -85.4, 'lon': 53.0, 'region': 'south_pole',
        'illumination_pct': 60, 'ice_confidence': 0.78,
        'slope_deg': 9, 'temperature_k': 260,
        'regolith_depth_m': 7, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'Nearby', 'skylight_distance_km': 18,
        'notes': 'Ice-rich region; moderate illumination.',
    },
    'Nobile Rim 2': {
        'lat': -85.2, 'lon': 51.0, 'region': 'south_pole',
        'illumination_pct': 58, 'ice_confidence': 0.80,
        'slope_deg': 11, 'temperature_k': 258,
        'regolith_depth_m': 6, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'Nearby', 'skylight_distance_km': 10,
        'notes': 'Higher ice confidence; steeper slope.',
    },
    'Slater Plain': {
        'lat': -88.0, 'lon': 150.0, 'region': 'south_pole',
        'illumination_pct': 70, 'ice_confidence': 0.65,
        'slope_deg': 6, 'temperature_k': 275,
        'regolith_depth_m': 9, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'None', 'skylight_distance_km': 999,
        'notes': 'Artemis III candidate; very flat and stable.',
    },
    'Peak near Cabeus B': {
        'lat': -85.0, 'lon': -40.0, 'region': 'south_pole',
        'illumination_pct': 72, 'ice_confidence': 0.85,
        'slope_deg': 14, 'temperature_k': 250,
        'regolith_depth_m': 5, 'earth_visibility': 'yes',
        'lava_tube_proximity': 'Nearby', 'skylight_distance_km': 22,
        'notes': 'High ice confidence; steep approach.',
    },
    'Peary Crater (North)': {
        'lat': 88.6, 'lon': 33.0, 'region': 'north_pole',
        'illumination_pct': 80, 'ice_confidence': 0.40,
        'slope_deg': 8, 'temperature_k': 290,
        'regolith_depth_m': 6, 'earth_visibility': 'no',
        'lava_tube_proximity': 'None', 'skylight_distance_km': 999,
        'notes': 'North Pole analog; less ice confirmed.',
    },
    'Whipple Crater (North)': {
        'lat': 89.1, 'lon': 120.0, 'region': 'north_pole',
        'illumination_pct': 75, 'ice_confidence': 0.50,
        'slope_deg': 9, 'temperature_k': 280,
        'regolith_depth_m': 5, 'earth_visibility': 'no',
        'lava_tube_proximity': 'None', 'skylight_distance_km': 999,
        'notes': 'North Pole candidate; comms via relay required.',
    },
}

# ============================================================================
# LUNAR SCORING ENGINE
# ============================================================================

def compute_display_score(rd: Dict) -> Dict:
    raw_score = rd.get('suitability_percentage', 0)
    raw_rating = rd.get('rating', 'Unknown')
    raw_emoji = rd.get('rating_emoji', '⚪')
    
    slope = rd.get('slope_deg', 0)
    illum = rd.get('illumination_pct', 0)
    ice = rd.get('ice_confidence', 0)
    
    cap_reason = None
    display_score = raw_score
    
    if slope > 15:
        display_score = min(raw_score, 30.0)
        cap_reason = f"Slope {slope:.1f}° > 15° lander limit — MISSION KILL"
    elif illum < 30 and ice < 0.3:
        display_score = min(raw_score, 35.0)
        cap_reason = "Low illumination AND low ice — no viable power OR ISRU"
    
    is_capped = display_score < raw_score
    not_feasible = bool(cap_reason and slope > 15)
    
    if is_capped:
        if display_score < 40:
            display_rating, display_emoji = 'Blocked', '🚫'
        elif display_score < 60:
            display_rating, display_emoji = 'High Risk', '🔴'
        else:
            display_rating, display_emoji = 'Limited', '⚠️'
    else:
        display_rating = raw_rating
        display_emoji = raw_emoji
    
    return {
        'display_score': round(display_score, 1),
        'raw_score': raw_score,
        'display_rating': display_rating,
        'display_emoji': display_emoji,
        'is_capped': is_capped,
        'cap_reason': cap_reason,
        'not_feasible': not_feasible,
    }

def _quick_static_estimate(data: Dict) -> Dict:
    ill = data['illumination_pct']
    ice = data['ice_confidence']
    slope = data['slope_deg']
    temp = data['temperature_k']
    reg = data['regolith_depth_m']
    lava = data.get('lava_tube_proximity', 'None')
    
    ill_s = 5.0 * (ill / 100.0)
    ice_s = 5.0 * ice
    slope_s = 5.0 if slope <= 5 else (4.5 if slope <= 10 else (3.0 if slope <= 15 else 1.0))
    temp_s = 5.0 if 200 <= temp <= 320 else (3.5 if 150 <= temp <= 350 else 2.0)
    reg_s = 5.0 if reg >= 6 else (4.0 if reg >= 3 else 2.5)
    lava_s = 5.0 if lava == 'Excellent' else (4.0 if lava == 'Nearby' else 2.0)
    
    composite = (ill_s * 0.25 + ice_s * 0.25 + slope_s * 0.15 + temp_s * 0.10 + reg_s * 0.10 + lava_s * 0.15) / 5.0 * 100
    
    if composite >= 80: rating, emoji = 'Excellent', '🌕'
    elif composite >= 65: rating, emoji = 'Good', '👍'
    elif composite >= 50: rating, emoji = 'Moderate', '👌'
    else: rating, emoji = 'Poor', '❌'
    
    investment = 'Extreme' if ill < 50 else ('Very High' if ill < 70 else 'High')
    
    return {'suitability': round(composite, 1), 'rating': rating,
            'rating_emoji': emoji, 'investment': investment}

def estimate_cost_range(rd: Dict) -> Dict:
    ill = rd.get('illumination_pct', 50)
    slope = rd.get('slope_deg', 15)
    ice = rd.get('ice_confidence', 0.3)
    temp = rd.get('temperature_k', 250)
    lava = rd.get('lava_tube_proximity', 'None')
    
    base = 80.0
    if ill < 50: base += 30.0
    if slope > 10: base += 15.0
    if ice > 0.7: base -= 10.0
    if temp < 100: base += 20.0
    if lava == 'Nearby': base -= 15.0
    
    low = round(base * 0.7, 1)
    mid = round(base, 1)
    high = round(base * 1.3, 1)
    
    extras = []
    if slope > 12: extras.append("Lander slope modification (~$5B)")
    if ill < 60: extras.append("Nuclear power supplement (~$8B)")
    if rd.get('earth_visibility') == 'no': extras.append("Relay satellite (~$12B)")
    if lava == 'None': extras.append("Regolith radiation shielding (~$10B)")
    
    return {
        'low_billion': low, 'mid_billion': mid, 'high_billion': high,
        'includes': ['Launch', 'Lander', 'Habitat', 'Power', 'ISRU', 'Comms'],
        'excludes': extras if extras else ['Crew transport', 'Contingency'],
    }

def generate_recommendation_strategy(rd: Dict) -> Dict:
    score = rd.get('suitability_percentage', 0)
    ill = rd.get('illumination_pct', 0)
    ice = rd.get('ice_confidence', 0)
    slope = rd.get('slope_deg', 0)
    temp = rd.get('temperature_k', 250)
    lava = rd.get('lava_tube_proximity', 'None')
    
    recs = {'immediate_actions': [], 'short_term_actions': [], 'long_term_actions': [],
            'investment_required': 'High', 'overall_feasibility': 'Moderate',
            'risk_level': 'Medium', 'timeline_summary': {}}
    
    def add(bucket, text, priority, cost):
        recs[bucket].append({'text': text, 'priority': priority, 'cost': cost})
    
    if ill < 30:
        add('immediate_actions', f'🚨 ILLUMINATION {ill:.0f}% — Nuclear reactor MANDATORY.', 'Critical', '💸💸💸💸💸')
        recs['investment_required'] = 'Extreme'
    elif ill < 50:
        add('short_term_actions', f'☀️ Illumination {ill:.0f}% — Hybrid solar+nuclear.', 'High', '💸💸💸💸')
        recs['investment_required'] = 'Very High'
    else:
        add('immediate_actions', f'✅ Illumination {ill:.0f}% — Solar viable.', 'Low', '💸')
    
    if ice < 0.3:
        add('immediate_actions', f'💧 Ice confidence {ice:.0%} — ISRU unlikely. Import water.', 'High', '💸💸💸💸')
    elif ice > 0.7:
        add('immediate_actions', f'✅ Ice confidence {ice:.0%} — ISRU highly viable.', 'Low', '💸')
    else:
        add('short_term_actions', f'💧 Ice confidence {ice:.0%} — Prospecting rovers.', 'Medium', '💸💸')
    
    if slope > 15:
        add('immediate_actions', f'🚨 SLOPE {slope:.1f}° — Lander tip-over risk. TERRAIN BLOCKED.', 'Critical', '💸💸💸💸💸')
    elif slope > 10:
        add('short_term_actions', f'⛰️ Slope {slope:.1f}° — Reinforced landing legs required.', 'High', '💸💸💸')
    else:
        add('immediate_actions', f'✅ Slope {slope:.1f}° — Excellent for lander.', 'Low', '💸')
    
    if lava == 'Nearby':
        add('immediate_actions', f'🌋 Lava tube nearby — Natural radiation shielding! Excellent for habitat.', 'Low', '💸')
    elif lava == 'None':
        add('short_term_actions', f'🪨 No lava tube access — Sintered regolith shielding required.', 'Medium', '💸💸💸')
    
    if temp < 150:
        add('immediate_actions', f'❄️ Temperature {temp:.0f}K — RTG heating mandatory.', 'Critical', '💸💸💸💸')
    elif 200 <= temp <= 320:
        add('immediate_actions', f'✅ Temperature {temp:.0f}K — Within habitable band.', 'Low', '💸')
    else:
        add('short_term_actions', f'🌡️ Temperature {temp:.0f}K — Thermal control needed.', 'Medium', '💸💸')
    
    add('long_term_actions', '🏗️ Habitat excavation or lava tube utilization.', 'Medium', '💸💸💸')
    add('long_term_actions', '🚀 ISRU plant (O2 + H2O + metals).', 'High', '💸💸💸💸')
    
    critical_count = sum(1 for a in recs['immediate_actions'] if a['priority'] == 'Critical')
    
    if score >= 80: band, emoji = 'Excellent', '🌕'
    elif score >= 65: band, emoji = 'Good', '👍'
    elif score >= 50: band, emoji = 'Moderate', '👌'
    else: band, emoji = 'Limited', '⚠️'
    
    if critical_count >= 3:
        feasibility, risk_level = '❌ Poor - Multiple critical hazards', 'Very High'
    elif critical_count >= 1:
        feasibility, risk_level = '👌 Moderate - One critical issue', 'High'
    else:
        feasibility = f'{emoji} {band}'
        risk_level = {'Excellent': 'Low', 'Good': 'Low', 'Moderate': 'Medium', 'Limited': 'High'}.get(band, 'Medium')
    
    recs['overall_feasibility'] = feasibility
    recs['risk_level'] = risk_level
    recs['critical_action_count'] = critical_count
    recs['high_action_count'] = 0
    recs['timeline_summary'] = {
        'immediate': f"{len(recs['immediate_actions'])} actions (0-6 months)",
        'short_term': f"{len(recs['short_term_actions'])} actions (6-18 months)",
        'long_term': f"{len(recs['long_term_actions'])} actions (18-36 months)",
    }
    return recs

# ============================================================================
# ELEVATION CROSS-SECTION GENERATOR
# ============================================================================

def generate_elevation_profile(rd: Dict, length_km: float = 50.0, points: int = 100) -> pd.DataFrame:
    """Generate a synthetic elevation profile based on the site's slope and regolith."""
    slope = rd.get('slope_deg', 0)
    base_slope_rise = math.tan(math.radians(slope)) * 1000  # m per km
    np.random.seed(hash(rd.get('site_name', '')) % 2**32)
    x = np.linspace(0, length_km, points)
    # Base terrain + gentle crater + noise
    base = base_slope_rise * x
    crater = 50 * np.exp(-((x - length_km/2)**2) / (2 * (length_km/6)**2)) * -1
    noise = np.random.normal(0, 8, points)
    y = base + crater + noise
    return pd.DataFrame({'Distance (km)': x, 'Elevation (m)': y})

# ============================================================================
# 🆕 FEATURE 4: SUN POSITION ANIMATION
# ============================================================================

def generate_sun_position_frames(lat: float, illum_pct: float, n_frames: int = 60) -> List[Dict]:
    """Generate an animation showing sun position over a lunar day."""
    frames = []
    for i in range(n_frames):
        lunar_day_fraction = i / n_frames
        # Simplified: sun angle goes from 0 to 360 degrees
        sun_angle_deg = lunar_day_fraction * 360.0
        # Illumination factor oscillates but never hits zero at pole
        illum_factor = (math.sin(math.radians(sun_angle_deg)) + 1) / 2
        # Blend with base illum
        current_illum = illum_pct * 0.4 + illum_pct * 0.6 * illum_factor
        temp_c = -150 + 230 * (current_illum / 100.0)
        frames.append({
            'frame': i,
            'lunar_day_fraction': round(lunar_day_fraction, 3),
            'hour': round(lunar_day_fraction * 29.5 * 24, 1),
            'sun_angle_deg': round(sun_angle_deg, 1),
            'illumination_pct': round(current_illum, 1),
            'temperature_c': round(temp_c, 1),
        })
    return frames

# ============================================================================
# MEMORY REPOSITORY
# ============================================================================

class MemoryRepository:
    def __init__(self, db_path: str = "moonbase_memory.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL, query_hash TEXT NOT NULL,
                result_summary TEXT, success INTEGER, execution_time REAL,
                parameters TEXT, timestamp TEXT, embedding BLOB
            )
        """)
        conn.commit(); conn.close()

    def store_analysis(self, query, summary, success, exec_time, params):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        qhash = hashlib.md5(query.lower().encode()).hexdigest()
        cursor.execute("""
            INSERT INTO analysis_memory
            (query, query_hash, result_summary, success, execution_time, parameters, timestamp, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (query, qhash, summary, 1 if success else 0, exec_time,
              json.dumps(params), datetime.now().isoformat(), pickle.dumps([])))
        conn.commit(); conn.close()

    def get_all_analyses(self, limit=20):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM analysis_memory ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        results = [{
            'query': r[1], 'result_summary': r[3],
            'success': bool(r[4]), 'execution_time': r[5],
            'parameters': json.loads(r[6]) if r[6] else {},
            'timestamp': r[7],
        } for r in rows]
        conn.close()
        return results

    def get_analysis_stats(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM analysis_memory")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM analysis_memory WHERE success = 1")
        success = cursor.fetchone()[0]
        conn.close()
        return {'total_analyses': total, 'successful_analyses': success,
                'success_rate': success / total if total > 0 else 0}

    def clear_all(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analysis_memory")
        conn.commit(); conn.close()

# ============================================================================
# MOON ANALYSIS STRATEGY
# ============================================================================

class MoonSiteAnalysisStrategy(ABC):
    def __init__(self, region: str = "south_pole"):
        self.region = region

    def analyse(self, site_name: str, params: Dict) -> Dict:
        data = MOON_SITES.get(site_name, {
            'lat': 0.0, 'lon': 0.0, 'region': 'unknown',
            'illumination_pct': 50, 'ice_confidence': 0.3,
            'slope_deg': 15, 'temperature_k': 250,
            'regolith_depth_m': 5, 'earth_visibility': 'partial',
            'lava_tube_proximity': 'None', 'skylight_distance_km': 999,
            'notes': 'Unknown site'
        })

        mission_year = params.get('mission_year', 2026)
        ill = get_seasonal_illumination(data['illumination_pct'], data['lat'], mission_year)
        
        ice = data['ice_confidence']
        slope = data['slope_deg']
        temp = data['temperature_k']
        reg = data['regolith_depth_m']
        comms = data['earth_visibility']
        lava = data.get('lava_tube_proximity', 'None')

        scores = {}
        scores['illumination'] = round(5.0 * (ill / 100.0), 2)
        scores['ice_access'] = round(5.0 * ice, 2)
        scores['slope_safety'] = 5.0 if slope <= 5 else (4.5 if slope <= 10 else (3.0 if slope <= 15 else 1.0))
        scores['temperature'] = 5.0 if 200 <= temp <= 320 else (3.5 if 150 <= temp <= 350 else 2.0)
        scores['regolith'] = 5.0 if reg >= 6 else (4.0 if reg >= 3 else 2.5)
        scores['comms'] = 5.0 if comms == 'yes' else (3.0 if comms == 'partial' else 1.0)
        scores['subsurface_access'] = 5.0 if lava == 'Excellent' else (4.0 if lava == 'Nearby' else 2.0)

        weights = {
            'illumination': 0.20, 'ice_access': 0.20, 'slope_safety': 0.15,
            'temperature': 0.10, 'regolith': 0.10, 'comms': 0.05,
            'subsurface_access': 0.20,
        }
        weighted_total = sum(scores[k] * weights[k] for k in weights)
        percentage = (weighted_total / 5.0) * 100

        if percentage >= 80: rating, emoji = 'Excellent', '🌕'
        elif percentage >= 65: rating, emoji = 'Good', '👍'
        elif percentage >= 50: rating, emoji = 'Moderate', '👌'
        elif percentage >= 35: rating, emoji = 'Limited', '⚠️'
        else: rating, emoji = 'Poor', '❌'

        return {
            'success': True, 'scores': scores, 'details': {
                'illumination': {'score': scores['illumination'], 'value': f"{ill:.0f}%", 'weight': weights['illumination'], 'source': f'LRO LOLA (Year {mission_year})'},
                'ice_access': {'score': scores['ice_access'], 'value': f"{ice:.0%}", 'weight': weights['ice_access'], 'source': 'Mini-RF + LCROSS'},
                'slope_safety': {'score': scores['slope_safety'], 'value': f"{slope:.1f}°", 'weight': weights['slope_safety'], 'source': 'LOLA DEM'},
                'temperature': {'score': scores['temperature'], 'value': f"{temp:.0f}K", 'weight': weights['temperature'], 'source': 'Diviner'},
                'regolith': {'score': scores['regolith'], 'value': f"{reg:.1f}m", 'weight': weights['regolith'], 'source': 'Mini-RF'},
                'comms': {'score': scores['comms'], 'value': comms.capitalize(), 'weight': weights['comms'], 'source': 'Geometry'},
                'subsurface_access': {'score': scores['subsurface_access'], 'value': lava, 'weight': weights['subsurface_access'], 'source': 'LRO LROC'},
            },
            'weighted_score': weighted_total, 'max_possible_score': 5.0,
            'suitability_percentage': round(percentage, 1),
            'base_percentage': round(percentage, 1),
            'rating': rating, 'rating_emoji': emoji,
            'location': f"{site_name} ({data['lat']:.4f}, {data['lon']:.4f})",
            'site_name': site_name, 'region': self.region,
            'lat': data['lat'], 'lon': data['lon'],
            'illumination_pct': ill, 'ice_confidence': ice,
            'slope_deg': slope, 'temperature_k': temp,
            'regolith_depth_m': reg, 'earth_visibility': comms,
            'lava_tube_proximity': lava,
            'mission_year': mission_year,
            'notes': data['notes'],
            'analysis_method': 'Moon: NASA LRO data',
            'data_source_details': [f"Illum: {ill:.0f}%", f"Ice: {ice:.0%}", f"Slope: {slope:.1f}°"],
        }

# ============================================================================
# SESSION STATE
# ============================================================================

def init_session_state():
    if 'memory_repo' not in st.session_state:
        st.session_state.memory_repo = MemoryRepository()
    if 'analysis_history' not in st.session_state:
        st.session_state.analysis_history = []
    if 'region' not in st.session_state:
        st.session_state.region = 'south_pole'
    if 'selected_site_name' not in st.session_state:
        st.session_state.selected_site_name = 'Shackleton Crater Rim'
    if 'current_results' not in st.session_state:
        st.session_state.current_results = None
    if 'mission_year' not in st.session_state:
        st.session_state.mission_year = 2026
    if 'show_artemis_overlay' not in st.session_state:
        st.session_state.show_artemis_overlay = False
    if 'compare_mode' not in st.session_state:
        st.session_state.compare_mode = False
    if 'compare_sites' not in st.session_state:
        st.session_state.compare_sites = []
    if 'water_regolith_kg' not in st.session_state:
        st.session_state.water_regolith_kg = 5000.0
    if 'radiation_target_msv' not in st.session_state:
        st.session_state.radiation_target_msv = 50.0

# ============================================================================
# 🆕 FEATURE 1: MISSION RANDOMIZER / SURPRISE ME
# ============================================================================

def render_randomizer():
    st.markdown("""<div style="color: #00f0ff; font-family: 'Courier New', monospace; 
         letter-spacing: 2px; font-size: 0.9rem; margin-bottom: 10px; text-align: center;">
        🎲 SURPRISE ME</div>""", unsafe_allow_html=True)
    if st.button("🎲 Random Lunar Site", use_container_width=True):
        # Bias toward poles (most interesting)
        if np.random.random() < 0.7:
            # Pole region
            lat = np.random.choice([1, -1]) * np.random.uniform(80.0, 89.9)
            lon = np.random.uniform(-180, 180)
        else:
            lat = np.random.uniform(-80.0, 80.0)
            lon = np.random.uniform(-180, 180)
        
        custom_name = f"Random Site ({lat:.1f}°, {lon:.1f}°)"
        abs_lat = abs(lat)
        
        if abs_lat > 80:
            dynamic_illum = 85.0
            dynamic_ice = 0.75
            dynamic_slope = 10.0
            dynamic_temp = 270
            dynamic_lava = 'Nearby'
        elif abs_lat > 60:
            dynamic_illum = 60.0
            dynamic_ice = 0.40
            dynamic_slope = 12.0
            dynamic_temp = 260
            dynamic_lava = 'None'
        else:
            dynamic_illum = 50.0
            dynamic_ice = 0.20
            dynamic_slope = 8.0
            dynamic_temp = 300
            dynamic_lava = 'None'
        
        MOON_SITES[custom_name] = {
            'lat': lat, 'lon': lon, 'region': 'custom',
            'illumination_pct': dynamic_illum, 'ice_confidence': dynamic_ice,
            'slope_deg': dynamic_slope, 'temperature_k': dynamic_temp,
            'regolith_depth_m': 6.0, 'earth_visibility': 'yes' if abs_lat > 60 else 'partial',
            'lava_tube_proximity': dynamic_lava, 'skylight_distance_km': 15 if dynamic_lava == 'Nearby' else 999,
            'notes': 'Randomly generated site from the Surprise Me button.',
        }
        st.session_state.selected_site_name = custom_name
        st.session_state.current_results = None
        st.rerun()

# ============================================================================
# UI — MAP (WITH CLICK ANYWHERE + ARTEMIS OVERLAY)
# ============================================================================

def render_map(params, region):
    st.subheader(f"🌙 {region.replace('_', ' ').title()} Lunar Site Map")
    
    if st.session_state.selected_site_name in MOON_SITES:
        sel = MOON_SITES[st.session_state.selected_site_name]
        center = [sel['lat'], sel['lon']]
    else:
        center = [-89.5, 0.0]

    m = folium.Map(location=center, zoom_start=4, tiles=MOON_TILES, 
                   attr='NASA LRO WAC / USGS Astrogeology')

    # FEATURE 3: Artemis III Landing Zones Overlay
    if st.session_state.show_artemis_overlay:
        for name, coords in ARTEMIS_III_SITES.items():
            folium.Circle(
                location=coords,
                radius=15000,
                color='#ff2d95',
                fill=True,
                fill_color='#ff2d95',
                fill_opacity=0.15,
                weight=2,
                dash_array='5,5',
                popup=f"<b>🛰️ Artemis III Region</b><br>{name}",
                tooltip=f"Artemis III: {name}",
            ).add_to(m)

    for name, data in MOON_SITES.items():
        if data['region'] != region: continue
        est = _quick_static_estimate(data)
        score = est['suitability']
        color = 'green' if score >= 80 else ('lightgreen' if score >= 65 else ('orange' if score >= 50 else 'red'))
        
        folium.Marker(
            [data['lat'], data['lon']],
            popup=f"<b>{name}</b><br>Score: {score:.0f}%<br>Illum: {data['illumination_pct']}%",
            tooltip=f"{name}: {score:.0f}%",
            icon=folium.Icon(color=color, icon='star', prefix='fa')
        ).add_to(m)

    if st.session_state.selected_site_name in MOON_SITES:
        sel = MOON_SITES[st.session_state.selected_site_name]
        folium.Marker(
            [sel['lat'], sel['lon']],
            popup=f"<b>🎯 {st.session_state.selected_site_name}</b>",
            icon=folium.Icon(color='blue', icon='crosshairs', prefix='fa')
        ).add_to(m)

    try:
        Fullscreen(position='topleft').add_to(m)
        MousePosition(position='bottomleft', prefix='Lunar Coords: ').add_to(m)
    except Exception: pass

    map_data = st_folium(m, width=None, height=500, use_container_width=True)

    # CLICK ANYWHERE FEATURE
    if map_data and map_data.get('last_clicked'):
        clicked_lat = map_data['last_clicked']['lat']
        clicked_lon = map_data['last_clicked']['lng']
        
        custom_name = f"Custom Site ({clicked_lat:.1f}°, {clicked_lon:.1f}°)"
        abs_lat = abs(clicked_lat)
        
        if abs_lat > 80:
            dynamic_illum = 85.0
            dynamic_ice = 0.75
            dynamic_slope = 10.0
            dynamic_temp = 270
            dynamic_lava = 'Nearby'
        elif abs_lat > 60:
            dynamic_illum = 60.0
            dynamic_ice = 0.40
            dynamic_slope = 12.0
            dynamic_temp = 260
            dynamic_lava = 'None'
        else:
            dynamic_illum = 50.0
            dynamic_ice = 0.20
            dynamic_slope = 8.0
            dynamic_temp = 300
            dynamic_lava = 'None'
        
        MOON_SITES[custom_name] = {
            'lat': clicked_lat, 'lon': clicked_lon, 'region': 'custom',
            'illumination_pct': dynamic_illum, 'ice_confidence': dynamic_ice,
            'slope_deg': dynamic_slope, 'temperature_k': dynamic_temp,
            'regolith_depth_m': 6.0, 'earth_visibility': 'yes' if abs_lat > 60 else 'partial',
            'lava_tube_proximity': dynamic_lava, 'skylight_distance_km': 15 if dynamic_lava == 'Nearby' else 999,
            'notes': 'Dynamically generated site from map click.',
        }
        
        if st.session_state.selected_site_name != custom_name:
            st.session_state.selected_site_name = custom_name
            st.rerun()

    trek_url = "https://trek.nasa.gov/moon/"
    st.markdown(f"""
    <div class="nasa-trek-box">
        <a href="{trek_url}" target="_blank" style="color: #ff2d95; font-weight: bold; text-decoration: none;">
            🌙 Open NASA Moon Trek 3D ↗
        </a>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# UI — SIDEBAR
# ============================================================================

def render_region_switcher():
    st.markdown("""
    <div style="text-align: center; margin: 10px 0;">
        <div style="color: #00f0ff; font-family: 'Courier New', monospace; 
             letter-spacing: 3px; font-size: 0.9rem; margin-bottom: 10px;">
            🌙 SELECT LUNAR REGION</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌑 SOUTH POLE\n(Artemis Zone)", use_container_width=True,
                     type="primary" if st.session_state.region == 'south_pole' else "secondary"):
            st.session_state.region = 'south_pole'
            st.session_state.selected_site_name = 'Shackleton Crater Rim'
            st.session_state.current_results = None
            st.rerun()
    with col2:
        if st.button("🌕 NORTH POLE\n(Backup Zone)", use_container_width=True,
                     type="primary" if st.session_state.region == 'north_pole' else "secondary"):
            st.session_state.region = 'north_pole'
            st.session_state.selected_site_name = 'Peary Crater (North)'
            st.session_state.current_results = None
            st.rerun()
    return st.session_state.region

def render_sidebar(region):
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 10px 0;">
            <div style="font-size: 2.2rem; font-family: 'Courier New', monospace; 
                 background: linear-gradient(90deg, #00f0ff, #a0a0c0, #ffffff);
                 -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                 font-weight: 900; letter-spacing: 3px;">MOONBASE</div>
            <div style="color: #00f0ff; font-size: 0.75rem; font-family: 'Courier New', monospace;
                 letter-spacing: 4px;">🌙 {region.replace('_', ' ').upper()}</div>
            <div class="cyber-divider"></div>
        </div>
        """, unsafe_allow_html=True)

        # 🆕 FEATURE 1: Randomizer in sidebar
        render_randomizer()
        st.divider()

        st.markdown("""<div style="color: #00f0ff; font-family: 'Courier New', monospace; 
             letter-spacing: 2px; font-size: 0.9rem; margin-bottom: 10px;">
            🌙 SITE SELECTOR</div>""", unsafe_allow_html=True)

        sites = {k: v for k, v in MOON_SITES.items() if v['region'] == region}
        st.info(f"Showing {len(sites)} NASA candidate sites")
        site_names = list(sites.keys())
        idx = site_names.index(st.session_state.selected_site_name) if st.session_state.selected_site_name in site_names else 0
        quick_site = st.selectbox("Select Site", site_names, index=idx)
        if st.button("⚡ GO TO SITE", use_container_width=True):
            st.session_state.selected_site_name = quick_site
            st.rerun()
        st.divider()

        # FEATURE 3: Artemis III Overlay Toggle
        st.markdown("""<div style="color: #ff2d95; font-family: 'Courier New', monospace; 
             letter-spacing: 2px; font-size: 0.9rem; margin-bottom: 10px;">
            🛰️ ARTEMIS III OVERLAY</div>""", unsafe_allow_html=True)
        st.session_state.show_artemis_overlay = st.toggle(
            "Show Artemis III Candidate Regions",
            value=st.session_state.show_artemis_overlay,
            help="Overlay the 13 official NASA Artemis III landing regions."
        )
        st.caption("Pink dashed circles = NASA candidate zones.")
        st.divider()

        st.markdown("""<div style="color: #00f0ff; font-family: 'Courier New', monospace; 
             letter-spacing: 2px; font-size: 0.9rem; margin-bottom: 10px;">
            📅 SEASONAL ILLUMINATION</div>""", unsafe_allow_html=True)
        mission_year = st.slider("Mission Year (Seasonal Drift)", 2026, 2034, 2026)
        st.session_state.mission_year = mission_year
        st.caption("Lunar illumination shifts by 2-3 weeks per year due to the Moon's tilt.")
        st.divider()

        st.markdown("""<div style="color: #00f0ff; font-family: 'Courier New', monospace; 
             letter-spacing: 2px; font-size: 0.9rem; margin-bottom: 10px;">
            🧠 MEMORY</div>""", unsafe_allow_html=True)

        stats = st.session_state.memory_repo.get_analysis_stats()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Analyses", stats['total_analyses'])
        with col2:
            st.metric("Success", f"{stats['success_rate']*100:.0f}%")

        if st.button("🗑️ CLEAR MEMORY", use_container_width=True):
            st.session_state.memory_repo.clear_all()
            try: Path("moonbase_memory.db").unlink(missing_ok=True)
            except Exception: pass
            st.session_state.analysis_history = []
            st.session_state.current_results = None
            st.session_state.memory_repo = MemoryRepository()
            st.success("Memory cleared!")
            st.rerun()

        return {'radius': 10000, 'mission_year': mission_year}

# ============================================================================
# UI — QUERY & RESULTS
# ============================================================================

def render_query_interface(params, region):
    st.subheader("💬 Analyse Lunar Site")
    query = st.text_area("Describe your analysis goal:",
                         placeholder="e.g., Evaluate this site for a permanent Moonbase",
                         height=100)
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        analyse_btn = st.button("🌙 ANALYSE SITE", type="primary", use_container_width=True)
    with col2:
        if st.button("🧹 CLEAR", use_container_width=True):
            st.session_state.current_results = None
            st.rerun()

    if analyse_btn:
        with st.spinner("🌙 Scoring against NASA LRO criteria..."):
            t0 = time.time()
            strategy = MoonSiteAnalysisStrategy(region)
            result = strategy.analyse(st.session_state.selected_site_name, params)
            elapsed = time.time() - t0
            st.session_state.current_results = result
            st.session_state.analysis_history.append(result)
            st.session_state.memory_repo.store_analysis(
                query or f"Evaluate {st.session_state.selected_site_name}",
                result.get('location', ''), True, elapsed, params)
            st.success(f"✅ Analysis complete in {elapsed:.2f}s")
            st.rerun()

def render_results():
    st.subheader("🌙 Moonbase Site Analysis Results")
    rd = st.session_state.current_results
    if not rd:
        st.info("No results yet. Pick a site and click ANALYSE.")
        return

    st.success(f"🌐 **NASA LRO DATA** · {rd['site_name']} · Mission Year: {rd.get('mission_year', 2026)}")

    disp = compute_display_score(rd)
    if disp['is_capped']:
        st.markdown(f"""
        <div class="blocked-score">
            <div style="color: #ff2d95; font-size: 2.5rem; font-weight: 900;">
                {disp['display_score']}% {disp['display_emoji']}
            </div>
            <div style="color: #ffffff; font-size: 0.9rem;">
                ⚠️ Capped: {disp['cap_reason']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.metric("🌙 Moonbase Suitability", f"{rd['suitability_percentage']}%",
                  delta=f"{rd['rating']} {rd['rating_emoji']}")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("Illumination", f"{rd.get('illumination_pct', 0):.0f}%")
    with c2: st.metric("Slope", f"{rd.get('slope_deg', 0):.1f}°")
    with c3: st.metric("Ice", f"{rd.get('ice_confidence', 0):.0%}")
    with c4: st.metric("Lava Tube", rd.get('lava_tube_proximity', 'None'))
    with c5: st.metric("Earth Comms", rd.get('earth_visibility', 'N/A').capitalize())

    st.write("---")
    
    dv = compute_moon_delta_v(rd.get('lat', 0))
    st.markdown(f"""
    <div class="delta-v-box">
        <div style="color: #00f0ff; font-size: 1.1rem; font-weight: bold; margin-bottom: 10px;">
            🚀 LUNAR DELTA-V & TRAVEL TIME
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Moon → Earth (direct):</span>
            <b style="color: #ff6b35;">{dv['dv_earth']:,.0f} m/s</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Moon → LEO (with refuel):</span>
            <b style="color: #39ff14;">{dv['dv_leo']:,.0f} m/s</b>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span>Travel Time:</span>
            <b style="color: #00f0ff;">~{dv['travel_time_days']} days</b>
        </div>
        <div style="font-size: 0.75rem; color: #a0a0c0; margin-top: 8px;">
            * Moon rotation adds {dv['rotation_speed']} m/s at this latitude.
        </div>
    </div>
    """, unsafe_allow_html=True)

    climate = fetch_moon_climate_model(rd.get('lat', 0), rd.get('illumination_pct', 0))
    st.markdown(f"""
    <div class="climate-box">
        <div style="color: #a0a0c0; font-size: 1.1rem; font-weight: bold; margin-bottom: 10px;">
            🌡️ LIVE LUNAR THERMAL MODEL
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Temperature:</span>
            <b style="color: #00f0ff;">{climate['temperature_c']} °C</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Atmosphere:</span>
            <b style="color: #00f0ff;">Vacuum (0 atm)</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Radiation:</span>
            <b style="color: #ff2d95;">{climate['radiation_msv_year']} mSv/year</b>
        </div>
        <div style="font-size: 0.75rem; color: #a0a0c0; margin-top: 8px;">
            * Source: {climate['source']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if rd.get('lava_tube_proximity') == 'Nearby':
        st.markdown(f"""
        <div class="subsurface-box">
            <div style="color: #b026ff; font-size: 1.1rem; font-weight: bold; margin-bottom: 10px;">
                🌋 SUBSURFACE ACCESS — LAVA TUBE DETECTED
            </div>
            <div style="color: #ffffff; font-size: 0.9rem;">
                A lava tube is nearby. This offers natural radiation shielding, 
                thermal insulation, and a ready-made habitat structure. 
                This significantly reduces construction costs and radiation risk.
            </div>
        </div>
        """, unsafe_allow_html=True)

    col_chart, col_list = st.columns([1, 1])
    with col_chart:
        st.write("**💰 Estimated Cost Breakdown**")
        fig = go.Figure(data=[go.Pie(labels=['Lander', 'Habitat', 'Power', 'ISRU', 'Comms'], 
                                     values=[30, 25, 20, 15, 10], hole=.4,
                                     marker=dict(colors=['#00f0ff', '#a0a0c0', '#ffffff', '#b026ff', '#ff2d95']))])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    with col_list:
        st.write("**Cost Estimates**")
        cost = estimate_cost_range(rd)
        st.metric("Low", f"${cost['low_billion']:.1f}B")
        st.metric("Mid", f"${cost['mid_billion']:.1f}B")
        st.metric("High", f"${cost['high_billion']:.1f}B")

    st.write("---")
    st.write("**🌍 Frame of Reference (Earth vs Moon)**")
    col_e, col_m = st.columns(2)
    with col_e: st.metric("Earth Gravity", "1.0 G", delta="Baseline")
    with col_m: st.metric("Moon Gravity", "0.16 G", delta="-0.84 G")
    st.caption("The Moon has 1/6th of Earth's gravity. Astronauts must exercise 2 hours/day to prevent bone loss.")

    # FEATURE 4: Elevation Cross-Section Chart
    st.write("---")
    st.write("**⛰️ Elevation Cross-Section (50 km traverse)**")
    profile = generate_elevation_profile(rd)
    fig_elev = go.Figure()
    fig_elev.add_trace(go.Scatter(
        x=profile['Distance (km)'], y=profile['Elevation (m)'],
        mode='lines', fill='tozeroy',
        line=dict(color='#00f0ff', width=3),
        fillcolor='rgba(0, 240, 255, 0.15)',
        name='Terrain'
    ))
    fig_elev.add_hline(y=0, line_dash="dash", line_color="#39ff14",
                       annotation_text="Landing Zone", annotation_position="top left")
    fig_elev.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(10,10,25,0.6)',
        font=dict(color='white'), height=300,
        xaxis_title="Distance (km)", yaxis_title="Elevation (m)",
        margin=dict(t=20, b=40, l=40, r=20),
        xaxis=dict(gridcolor='rgba(0,240,255,0.1)'),
        yaxis=dict(gridcolor='rgba(0,240,255,0.1)'),
    )
    st.plotly_chart(fig_elev, use_container_width=True)
    st.caption(f"Based on {rd.get('slope_deg', 0):.1f}° measured slope — visualizes lander approach terrain.")

    # 🆕 FEATURE 2: WATER PRODUCTION CALCULATOR
    st.write("---")
    st.write("**💧 ISRU Water Production Calculator**")
    st.caption("Estimate daily water output from processing lunar regolith at this site.")
    regolith_kg = st.slider(
        "Regolith processing rate (kg/day)",
        min_value=1000, max_value=20000, value=int(st.session_state.water_regolith_kg),
        step=1000, key="water_regolith_slider",
    )
    st.session_state.water_regolith_kg = regolith_kg
    water = water_production_estimate(rd, regolith_kg_per_day=regolith_kg)
    st.markdown(f"""
    <div class="water-box">
        <div style="color: #00d4ff; font-size: 1.1rem; font-weight: bold; margin-bottom: 10px;">
            💧 WATER PRODUCTION (ISRU)
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Daily Water Output:</span>
            <b style="color: #00f0ff;">{water['water_l_day']:,.0f} L/day</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Ice Fraction (regolith):</span>
            <b style="color: #00f0ff;">{water['ice_fraction']*100:.1f}%</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Crews Supported (10 crew):</span>
            <b style="color: #39ff14;">{water['crew_supported']:.1f}</b>
        </div>
        <div style="display: flex; justify-content: space-between;">
            <span>Status:</span>
            <b style="color: {'#39ff14' if water['viable'] else '#ff2d95'};">
                {'✅ Viable' if water['viable'] else '❌ Not viable'}
            </b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 🆕 FEATURE 3: RADIATION SHIELD CALCULATOR
    st.write("---")
    st.write("**☢️ Radiation Shield Depth Calculator**")
    st.caption("Estimate regolith overburden needed to reach target radiation dose.")
    target = st.slider(
        "Target dose (mSv/year)",
        min_value=10, max_value=400, value=int(st.session_state.radiation_target_msv),
        step=10, key="radiation_target_slider",
    )
    st.session_state.radiation_target_msv = target
    shield = radiation_shield_estimate(rd, target_msv_year=target)
    st.markdown(f"""
    <div class="radiation-box">
        <div style="color: #ffc800; font-size: 1.1rem; font-weight: bold; margin-bottom: 10px;">
            ☢️ RADIATION SHIELDING
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Surface Dose:</span>
            <b style="color: #ff2d95;">{shield['surface_msv_year']:.0f} mSv/year</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Target Dose:</span>
            <b style="color: #00f0ff;">{shield['target_msv_year']:.0f} mSv/year</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Regolith Depth Needed:</span>
            <b style="color: #00f0ff;">{shield['depth_needed_m']:.2f} m</b>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span>Available Depth:</span>
            <b style="color: #00f0ff;">{shield['regolith_available_m']:.1f} m</b>
        </div>
        <div style="margin-top: 10px; padding: 8px; background: rgba(0,240,255,0.08); border-radius: 6px;">
            <b style="color: #ffffff;">💡 {shield['recommendation']}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 🆕 FEATURE 4: SUN POSITION ANIMATION
    st.write("---")
    st.write("**🌅 Sun Position Animation — Lunar Day**")
    st.caption("How sunlight moves over this site during a 29.5-day lunar day.")
    frames = generate_sun_position_frames(
        rd.get('lat', 0), rd.get('illumination_pct', 50), n_frames=60
    )
    df_frames = pd.DataFrame(frames)
    col_sun1, col_sun2 = st.columns([1, 2])
    with col_sun1:
        frame_idx = st.slider(
            "Lunar day progress",
            min_value=0, max_value=59, value=0,
            key="sun_anim_slider",
            help="Drag to see how sunlight changes over a full lunar day.",
        )
        current_frame = frames[frame_idx]
        st.metric("Illumination", f"{current_frame['illumination_pct']:.0f}%")
        st.metric("Temperature", f"{current_frame['temperature_c']:.0f} °C")
        st.metric("Sun Angle", f"{current_frame['sun_angle_deg']:.0f}°")
        st.metric("Lunar Hour", f"{current_frame['hour']:.1f} h")
    with col_sun2:
        fig_sun = go.Figure()
        fig_sun.add_trace(go.Scatter(
            x=df_frames['hour'], y=df_frames['illumination_pct'],
            mode='lines', name='Illumination',
            line=dict(color='#ffc800', width=3),
            fill='tozeroy', fillcolor='rgba(255, 200, 0, 0.15)',
        ))
        fig_sun.add_trace(go.Scatter(
            x=[current_frame['hour']], y=[current_frame['illumination_pct']],
            mode='markers', name='Current',
            marker=dict(color='#ff2d95', size=18, symbol='star'),
        ))
        fig_sun.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(10,10,25,0.6)',
            font=dict(color='white'), height=320,
            xaxis_title="Lunar Hour (0 → 708 h)",
            yaxis_title="Illumination %",
            margin=dict(t=20, b=40, l=40, r=20),
            xaxis=dict(gridcolor='rgba(255,200,0,0.1)'),
            yaxis=dict(gridcolor='rgba(255,200,0,0.1)'),
            showlegend=False,
        )
        st.plotly_chart(fig_sun, use_container_width=True)

    st.write("---")
    st.write("**Detailed Scoring Breakdown:**")
    details = rd.get('details', {})
    score_data = []
    for k, d in details.items():
        display_key = k.replace('_', ' ').title()
        if 'Illumination' in display_key: display_key = '☀️ ' + display_key
        elif 'Ice' in display_key: display_key = '💧 ' + display_key
        elif 'Slope' in display_key: display_key = '⛰️ ' + display_key
        elif 'Temperature' in display_key: display_key = '🌡️ ' + display_key
        elif 'Regolith' in display_key: display_key = '🪨 ' + display_key
        elif 'Comms' in display_key: display_key = '📡 ' + display_key
        elif 'Subsurface' in display_key: display_key = '🌋 ' + display_key
        score_data.append({
            'Criteria': display_key,
            'Score': f"{d.get('score', 0):.1f}/5",
            'Value': d.get('value', 'N/A'),
            'Weight': f"{d.get('weight', 0)*100:.0f}%",
            'Source': d.get('source', 'Unknown'),
        })
    st.dataframe(pd.DataFrame(score_data), use_container_width=True, hide_index=True)

    chart = pd.DataFrame([{'Criteria': r['Criteria'], 'Score': float(r['Score'].split('/')[0])}
                          for r in score_data])
    st.bar_chart(chart.set_index('Criteria'))

    st.write("---")
    st.write("**📋 Recommendation Strategy**")
    recs = generate_recommendation_strategy(rd)
    risk = recs.get('risk_level', 'Unknown')
    risk_color = '#ff2d95' if risk in ('High', 'Very High') else '#39ff14' if risk == 'Low' else '#ffe84d'

    st.markdown(f"""
    <div class="recommendation-container">
        <div class="recommendation-title">🎯 Overall Feasibility</div>
        <div style="color: #ffffff; font-size: 1.1rem; padding: 10px;">
            {recs.get('overall_feasibility', 'N/A')}
        </div>
        <div style="display: flex; gap: 20px; margin-top: 10px; flex-wrap: wrap;">
            <div style="color: #a0a0c0;">💰 Investment: <b style="color: #00f0ff;">{recs.get('investment_required', '?')}</b></div>
            <div style="color: #a0a0c0;">⚠️ Risk: <b style="color: {risk_color};">{risk}</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for bucket, title in [
        ('immediate_actions', '🔴 IMMEDIATE ACTIONS'),
        ('short_term_actions', '🟡 SHORT-TERM ACTIONS'),
        ('long_term_actions', '🟢 LONG-TERM ACTIONS'),
    ]:
        if recs[bucket]:
            st.markdown(f"""<div class="recommendation-container">
                <div class="recommendation-title">{title}</div>""", unsafe_allow_html=True)
            for a in recs[bucket]:
                st.markdown(f"""
                <div class="recommendation-item">
                    <span>{a.get('priority', '')}</span> {a['text']}
                </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# COMPARE MODE
# ============================================================================

def render_compare_mode(region):
    st.subheader("⚖️ Compare Sites Side-by-Side")
    st.caption("Select 2–3 candidate sites to compare their metrics, costs, and scores.")

    all_site_names = [k for k, v in MOON_SITES.items() if v['region'] == region]
    if len(all_site_names) < 2:
        st.info("Need at least 2 sites in this region to compare.")
        return

    compare_sites = st.multiselect(
        "Choose 2-3 sites to compare",
        options=all_site_names,
        default=all_site_names[:min(3, len(all_site_names))],
        max_selections=3,
        key="compare_multiselect",
    )

    if len(compare_sites) < 2:
        st.info("Select at least 2 sites to see the comparison.")
        return

    params = {'mission_year': st.session_state.mission_year}
    strategy = MoonSiteAnalysisStrategy(region)
    results = [strategy.analyse(name, params) for name in compare_sites]

    winner = max(results, key=lambda r: r['suitability_percentage'])
    winner_name = winner['site_name']

    st.write("### 📊 Side-by-Side Metrics")
    metric_rows = []
    for r in results:
        is_winner = (r['site_name'] == winner_name)
        metric_rows.append({
            '🏆': '🏆' if is_winner else '',
            'Site': r['site_name'],
            'Score': f"{r['suitability_percentage']}% {r['rating_emoji']}",
            'Illum %': f"{r['illumination_pct']:.0f}",
            'Slope °': f"{r['slope_deg']:.1f}",
            'Ice %': f"{r['ice_confidence']*100:.0f}",
            'Temp K': f"{r['temperature_k']:.0f}",
            'Lava Tube': r['lava_tube_proximity'],
            'Comms': r['earth_visibility'].capitalize(),
            'Rating': r['rating'],
        })
    df_compare = pd.DataFrame(metric_rows)
    st.dataframe(df_compare, use_container_width=True, hide_index=True)

    st.write("### 🕸️ Radar Comparison")
    categories = ['Illumination', 'Ice', 'Slope', 'Temperature', 'Regolith', 'Comms', 'Subsurface']
    fig_radar = go.Figure()
    palette = ['#00f0ff', '#ff2d95', '#39ff14', '#b026ff']
    for i, r in enumerate(results):
        d = r['details']
        values = [
            d['illumination']['score'],
            d['ice_access']['score'],
            d['slope_safety']['score'],
            d['temperature']['score'],
            d['regolith']['score'],
            d['comms']['score'],
            d['subsurface_access']['score'],
        ]
        fig_radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name=r['site_name'][:25],
            line=dict(color=palette[i % len(palette)], width=2),
            opacity=0.6,
        ))
    fig_radar.update_layout(
        polar=dict(
            bgcolor='rgba(10,10,25,0.6)',
            radialaxis=dict(visible=True, range=[0, 5], gridcolor='rgba(0,240,255,0.2)'),
            angularaxis=dict(gridcolor='rgba(0,240,255,0.15)'),
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=450,
        legend=dict(bgcolor='rgba(0,0,0,0)'),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    st.write("### 🏆 Recommended Site")
    st.markdown(f"""
    <div class="recommendation-container" style="border-color: #39ff14;">
        <div class="recommendation-title" style="color: #39ff14;">🏆 {winner_name}</div>
        <div style="color: #ffffff; font-size: 1rem; padding: 6px;">
            Highest suitability score: <b style="color: #00f0ff;">{winner['suitability_percentage']}%</b>
            ({winner['rating']} {winner['rating_emoji']})
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_simulation_lab():
    st.subheader("🧪 Simulation Lab (What-If)")
    st.markdown("Adjust parameters to see how the mission scales.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        crew_size = st.slider("Crew Size", 4, 100, 10)
    with col2:
        habitat_mass = st.slider("Habitat Mass (Tons)", 50, 500, 150)
    with col3:
        power_source = st.selectbox("Power Source", ["Hybrid (Solar+Nuclear)", "Solar Only", "Nuclear Only"])

    base_cost = 80.0
    new_cost = base_cost + (crew_size * 1.5) + (habitat_mass * 0.3)
    if power_source == "Nuclear Only": new_cost += 30.0
    if power_source == "Solar Only": new_cost -= 10.0

    air_needed = crew_size * 200
    water_needed = crew_size * 150
    regolith_shielding = crew_size * 15

    st.markdown("---")
    st.write("### 📊 Updated Mission Output")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("New Cost", f"${new_cost:.1f} B")
    with c2: st.metric("Air Needed", f"{air_needed:,} L/day")
    with c3: st.metric("Water Needed", f"{water_needed:,} L/day")
    with c4: st.metric("Regolith Shield", f"{regolith_shielding:,} tons")

def render_memory_explorer():
    st.subheader("💾 Memory Explorer")
    analyses = st.session_state.memory_repo.get_all_analyses(limit=20)
    if analyses:
        st.write(f"**{len(analyses)} past analyses**")
        for entry in analyses:
            qprev = entry['query'][:50] + "..." if len(entry['query']) > 50 else entry['query']
            with st.expander(f"{'✅' if entry['success'] else '❌'} {qprev}"):
                st.write(f"**Query:** {entry['query']}")
                st.write(f"**Time:** {entry['execution_time']:.2f}s")
                st.write(f"**Timestamp:** {entry['timestamp']}")
    else:
        st.info("No past analyses yet.")

# ============================================================================
# MAIN
# ============================================================================

def main():
    st.set_page_config(page_title="MoonBase", page_icon="🌙", layout="wide")
    st.markdown(MOON_CSS, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; padding: 20px 0 10px 0;">
        <div class="main-title">🌙 MOONBASE</div>
        <div class="subtitle">🌙 LUNAR FLOATING BASE SELECTION · v2.2.0</div>
        <div style="display: flex; justify-content: center; gap: 10px; margin: 10px 0;">
            <span class="phase-badge phase-badge-2">☀️ ILLUMINATION</span>
            <span class="phase-badge phase-badge-3">💧 ICE</span>
            <span class="phase-badge phase-badge-4">⛰️ SLOPE</span>
            <span class="phase-badge phase-badge-5">🌋 LAVA TUBE</span>
        </div>
        <div class="cyber-divider"></div>
        <div class="moon-banner">
            🛰️ NASA LRO DATA · ☀️ ILLUMINATION · 💧 ICE · ⛰️ SLOPE · 🌋 LAVA TUBE · 🪨 REGOLITH
        </div>
    </div>
    """, unsafe_allow_html=True)

    init_session_state()
    region = render_region_switcher()

    region_sites = [k for k, v in MOON_SITES.items() if v['region'] == region]
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; padding: 8px 15px;
         border: 1px solid rgba(0,240,255,0.15); border-radius: 8px;
         background: rgba(0,240,255,0.03); margin-bottom: 15px;">
        <span style="color: #a0a0c0; font-family: 'Courier New'; font-size: 0.7rem;">📍 SITES LOADED</span>
        <span style="color: #00f0ff; font-family: 'Courier New'; font-size: 0.8rem; font-weight: bold;">{len(region_sites)} NASA candidates</span>
        <span style="color: #a0a0c0; font-family: 'Courier New'; font-size: 0.6rem;">{region.replace('_', ' ').upper()}</span>
    </div>
    """, unsafe_allow_html=True)

    params = render_sidebar(region)

    col1, col2 = st.columns([1.5, 1])
    with col1:
        render_map(params, region)
        render_query_interface(params, region)
    with col2:
        if st.session_state.selected_site_name:
            st.markdown(f"""
            <div style="padding: 10px 15px; border: 1px solid rgba(0,240,255,0.2);
                 border-radius: 8px; background: rgba(0,240,255,0.03); margin-bottom: 15px;">
                <div style="color: #a0a0c0; font-family: 'Courier New'; font-size: 0.6rem; letter-spacing: 1px;">SELECTED SITE</div>
                <div style="color: #00f0ff; font-family: 'Courier New'; font-size: 0.9rem;">{st.session_state.selected_site_name}</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    col_cmp1, col_cmp2 = st.columns([1, 3])
    with col_cmp1:
        st.session_state.compare_mode = st.toggle(
            "⚖️ Compare Mode",
            value=st.session_state.compare_mode,
            help="Enable side-by-side comparison of up to 3 sites."
        )

    if st.session_state.compare_mode:
        render_compare_mode(region)
        st.divider()

    if st.session_state.current_results:
        tab1, tab2 = st.tabs(["📊 Analysis Results", "🛰️ Live Solar System Tracker"])
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                render_results()
            with col2:
                render_memory_explorer()
            with st.expander("🧪 Simulation Lab (What-If)"):
                render_simulation_lab()
        with tab2:
            st.markdown("### 🛰️ Real-Time Solar System Tracker")
            st.markdown("Powered by **NASA's Eyes on the Solar System**.")
            components.iframe(
                src="https://eyes.nasa.gov/apps/solar-system/#/home",
                height=600, scrolling=True
            )
    else:
        render_memory_explorer()

    # Footer
    st.markdown("""
    <div class="cyber-divider"></div>
    <div style="text-align: center; padding: 15px 0; color: #333; font-family: 'Courier New'; 
         font-size: 0.6rem; letter-spacing: 2px;">
        <span style="color: #00f0ff;">[</span> 
        MOONBASE v2.2.0 · NASA LRO DATA · ARTEMIS-ALIGNED
        <span style="color: #00f0ff;">]</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; padding: 20px 0 40px 0;">
        <a href="https://buymeacoffee.com/stargazex" target="_blank"> 
            <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" 
                 alt="Buy Me A Coffee" 
                 style="height: 60px !important;width: 217px !important;" > 
        </a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()