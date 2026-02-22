"""
Marauder's Map of Sensory Safety — Flask Backend
=================================================
Listens to Arduino serial for "DANGER" signals, deduplicates via Haversine,
stores danger-zone coordinates in map_data.json, and serves the themed frontend.
Includes geocoding search and multi-route comparison with danger avoidance.
"""

import json
import math
import os
import random
import threading
import time
from datetime import datetime

import requests as http_requests
from flask import Flask, jsonify, render_template, request

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
COM_PORT = "COM3"          # Change to match your Arduino port
BAUD_RATE = 9600
DATA_FILE = os.path.join(os.path.dirname(__file__), "map_data.json")
DEDUP_RADIUS_METERS = 50   # 50m radius for danger zones (one zone per 50m)
DANGER_PROXIMITY_M = 80    # Matches the 80m visual radius in index.html

GOOGLE_MAPS_API_KEY = "YOUR_API_KEY_HERE"  # Add your Google Maps API Key here!

# Stony Brook University — SAC bus stop area
DEFAULT_LAT = 40.91420
DEFAULT_LNG = -73.12320

# Bounding box for search bias (Stony Brook campus area)
SBU_BOUNDS = "40.900,-73.150,40.930,-73.100"  # S,W,N,E

app = Flask(__name__)
data_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Haversine helpers
# ---------------------------------------------------------------------------

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in **meters** between two lat/lon points."""
    R = 6_371_000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (math.sin(d_phi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# Removed is_duplicate function as requested

# ---------------------------------------------------------------------------
# JSON persistence
# ---------------------------------------------------------------------------

def load_data() -> list:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_data(points: list) -> None:
    with open(DATA_FILE, "w") as f:
        json.dump(points, f, indent=2)


def add_danger_point(lat: float, lng: float) -> dict | None:
    """Add a point if it passes dedup. Returns the new record or None."""
    with data_lock:
        points = load_data()
        # Deduplication removed as per user request
        # if is_duplicate(lat, lng, points):
        #     return None
        record = {
            "lat": round(lat, 6),
            "lng": round(lng, 6),
            "timestamp": datetime.now().isoformat(),
            "label": "Dementor Presence Detected",
        }
        points.append(record)
        save_data(points)
        return record

# ---------------------------------------------------------------------------
# Serial listener (background thread)
# ---------------------------------------------------------------------------

def serial_listener():
    """
    Continuously read the serial port.  When 'DANGER' arrives, log a point.
    Falls back gracefully if the port is unavailable.
    """
    try:
        import serial  # pyserial
    except ImportError:
        print("[serial] pyserial not installed — serial listener disabled.")
        return

    while True:
        try:
            ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
            print(f"[serial] Connected to {COM_PORT}")
            while True:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if line == "DANGER":
                    lat, lng = get_coordinates()
                    result = add_danger_point(lat, lng)
                    if result:
                        print(f"[serial] Logged danger @ ({lat:.6f}, {lng:.6f})")
                    else:
                        print(f"[serial] Duplicate — skipped ({lat:.6f}, {lng:.6f})")
        except Exception as e:
            print(f"[serial] {e} — retrying in 5 s …")
            time.sleep(5)


def get_coordinates() -> tuple[float, float]:
    """Return (lat, lng). Always returns a random point near the Stony Brook campus."""
    # Jitter to place them scattered around campus
    jitter = 0.0035
    return (
        DEFAULT_LAT + random.uniform(-jitter, jitter),
        DEFAULT_LNG + random.uniform(-jitter, jitter),
    )

# ---------------------------------------------------------------------------
# Route analysis helpers
# ---------------------------------------------------------------------------

def route_passes_danger(route_coords: list, danger_points: list,
                        proximity_m: float = DANGER_PROXIMITY_M) -> dict:
    """
    Check if a route passes near any danger zones.
    Returns { "passes_danger": bool, "danger_count": int, "nearby_dangers": [...] }
    """
    nearby = []
    seen = set()
    for rlat, rlng in route_coords:
        for dp in danger_points:
            dp_id = f"{dp['lat']},{dp['lng']}"
            if dp_id in seen:
                continue
            dist = haversine(rlat, rlng, dp["lat"], dp["lng"])
            if dist < proximity_m:
                nearby.append({
                    "lat": dp["lat"], "lng": dp["lng"],
                    "distance_m": round(dist, 1),
                    "label": dp.get("label", "Dementor Presence Detected"),
                })
                seen.add(dp_id)
    return {
        "passes_danger": len(nearby) > 0,
        "danger_count": len(nearby),
        "nearby_dangers": nearby,
    }


def polyline_length_m(coords: list) -> float:
    """Total length of a polyline in meters."""
    total = 0.0
    for i in range(len(coords) - 1):
        total += haversine(coords[i][0], coords[i][1],
                           coords[i + 1][0], coords[i + 1][1])
    return total

# ---------------------------------------------------------------------------
# Flask routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/dangers", methods=["GET"])
def get_dangers():
    """Return all logged danger points."""
    with data_lock:
        return jsonify(load_data())


@app.route("/api/danger", methods=["POST"])
def post_danger():
    """
    Manually add a danger point (useful for testing without Arduino).
    Body: { "lat": 40.71, "lng": -74.00 }   — or omit for auto-coords.
    """
    body = request.get_json(silent=True) or {}
    lat = body.get("lat")
    lng = body.get("lng")
    if lat is None or lng is None:
        lat, lng = get_coordinates()
    result = add_danger_point(float(lat), float(lng))
    return jsonify({"status": "added", "point": result}), 201
    # return jsonify({"status": "duplicate"}), 200


@app.route("/api/dangers/clear", methods=["POST"])
def clear_dangers():
    """Clear all danger points (dev helper)."""
    with data_lock:
        save_data([])
    return jsonify({"status": "cleared"})


@app.route("/api/search", methods=["GET"])
def search_location():
    """
    Geocode a search query using OpenStreetMap Nominatim.
    Biased toward Stony Brook campus area.
    """
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])

    try:
        resp = http_requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": q,
                "format": "json",
                "limit": 6,
                "viewbox": "-73.150,40.930,-73.100,40.900",
                "bounded": 0,  # prefer but don't restrict
                "addressdetails": 1,
            },
            headers={"User-Agent": "MaraudersMapSensorySafety/1.0"},
            timeout=5,
        )
        results = resp.json()
        return jsonify([
            {
                "name": r.get("display_name", ""),
                "lat": float(r["lat"]),
                "lng": float(r["lon"]),
            }
            for r in results
        ])
    except Exception as e:
        print(f"[search] Error: {e}")
        return jsonify([])


@app.route("/api/route", methods=["POST"])
def compute_route():
    """
    Compute walking routes between two points using Google Maps Directions API.
    Returns multiple route alternatives with danger analysis.

    Body: { "start": [lat, lng], "end": [lat, lng] }
    """
    if GOOGLE_MAPS_API_KEY == "YOUR_API_KEY_HERE" or not GOOGLE_MAPS_API_KEY:
        return jsonify({"error": "Google Maps API Key not configured. Please add it to app.py"}), 500

    body = request.get_json(silent=True) or {}
    start = body.get("start")
    end = body.get("end")

    if not start or not end:
        return jsonify({"error": "start and end required"}), 400

    slat, slng = float(start[0]), float(start[1])
    elat, elng = float(end[0]), float(end[1])

    # Load current danger points from the database
    with data_lock:
        all_dangers = load_data()

    routes = []

    # Try Google Maps Directions API for real walking routes with alternatives
    try:
        import polyline
        gmaps_url = (
            f"https://maps.googleapis.com/maps/api/directions/json"
            f"?origin={slat},{slng}&destination={elat},{elng}"
            f"&mode=walking&alternatives=true&key={GOOGLE_MAPS_API_KEY}"
        )
        resp = http_requests.get(gmaps_url, timeout=8)
        data = resp.json()

        if data.get("status") == "OK" and data.get("routes"):
            for i, route in enumerate(data["routes"]):
                leg = route["legs"][0]
                
                # Decode Google's overview_polyline
                coords = polyline.decode(route["overview_polyline"]["points"])
                
                distance_m = leg["distance"]["value"]
                duration_s = leg["duration"]["value"]

                danger_info = route_passes_danger(coords, all_dangers)

                # Classify the route
                if danger_info["passes_danger"]:
                    tag = "⚠️ Fastest (Dementor Zone!)"
                    safety = "dangerous"
                else:
                    tag = "🛡️ Safe Route (Patronus Protected)"
                    safety = "safe"

                routes.append({
                    "index": i,
                    "tag": tag,
                    "safety": safety,
                    "distance_m": round(distance_m),
                    "duration_min": round(duration_s / 60, 1),
                    "coords": coords,
                    "danger_info": danger_info,
                })
        else:
            print(f"[route] Google Maps status: {data.get('status')} - {data.get('error_message')}")
    except Exception as e:
        print(f"[route] Google Maps error: {e}")

    # If Google Maps returned nothing, make a simple straight-line fallback
    if not routes:
        straight = [(slat, slng), (elat, elng)]
        dist = haversine(slat, slng, elat, elng)
        danger_info = route_passes_danger(straight, all_dangers)
        routes.append({
            "index": 0,
            "tag": "📍 Direct Path (API Error)",
            "safety": "unknown",
            "distance_m": round(dist),
            "duration_min": round(dist / 80, 1),  # ~80m/min walk
            "coords": straight,
            "danger_info": danger_info,
        })

    # Sort: safe routes first, then by distance
    routes.sort(key=lambda r: (0 if r["safety"] == "safe" else 1, r["distance_m"]))

    # FALLBACK: If NO safe routes found, try hardcoded "Safe Corridors" (e.g., Zebra Path / Starbucks)
    if not any(r["safety"] == "safe" for r in routes) and len(all_dangers) > 0:
        # User requested specific corridors via Starbucks and Zebra Crossing
        safe_hubs = [
            {"name": "Zebra Crossing Path", "lat": 40.9148, "lng": -73.1232},
            {"name": "Starbucks Library Corridor", "lat": 40.9153, "lng": -73.1220},
        ]
        
        for hub in safe_hubs:
            try:
                gmaps_hub_url = (
                    f"https://maps.googleapis.com/maps/api/directions/json"
                    f"?origin={slat},{slng}&destination={elat},{elng}"
                    f"&waypoints=via:{hub['lat']},{hub['lng']}&mode=walking&key={GOOGLE_MAPS_API_KEY}"
                )
                resp_hub = http_requests.get(gmaps_hub_url, timeout=5)
                data_hub = resp_hub.json()
                
                if data_hub.get("status") == "OK" and data_hub.get("routes"):
                    route_hub = data_hub["routes"][0]
                    import polyline
                    coords_hub = polyline.decode(route_hub["overview_polyline"]["points"])
                    danger_info_hub = route_passes_danger(coords_hub, all_dangers)
                    
                    if not danger_info_hub["passes_danger"]:
                        dist_hub = sum(leg["distance"]["value"] for leg in route_hub["legs"])
                        dur_hub = sum(leg["duration"]["value"] for leg in route_hub["legs"])
                        
                        routes.append({
                            "index": 500 + len(routes),
                            "tag": f"🛡️ Recommended (via {hub['name']})",
                            "safety": "safe",
                            "distance_m": round(dist_hub),
                            "duration_min": round(dur_hub / 60, 1),
                            "coords": coords_hub,
                            "danger_info": danger_info_hub,
                        })
                        break # Found a safe hardcoded path
            except Exception as e:
                print(f"[fallback-hub] error: {e}")

    # SECONDARY FALLBACK: General POI Search (if hardcoded corridors also pass danger)
    if not any(r["safety"] == "safe" for r in routes) and len(all_dangers) > 0:
        try:
            # 1. Search for nearby POIs (buildings, landmarks) near the route midpoint
            m_lat, m_lng = (slat + elat) / 2, (slng + elng) / 2
            
            # Use Google Places Nearby Search with a slightly larger radius for more natural detours
            places_url = (
                f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
                f"?location={m_lat},{m_lng}&radius=400&type=university|point_of_interest|park|establishment"
                f"&key={GOOGLE_MAPS_API_KEY}"
            )
            resp_p = http_requests.get(places_url, timeout=5)
            places_data = resp_p.json()
            p_candidates = []
            if places_data.get("status") == "OK" and places_data.get("results"):
                for poi in places_data["results"][:10]:
                    p_lat = poi["geometry"]["location"]["lat"]
                    p_lng = poi["geometry"]["location"]["lng"]
                    
                    is_p_safe = True
                    for dp in all_dangers:
                        if haversine(p_lat, p_lng, dp["lat"], dp["lng"]) < DANGER_PROXIMITY_M:
                            is_p_safe = False
                            break
                    if is_p_safe:
                        p_candidates.append(poi)
                        if len(p_candidates) >= 3:
                            break
                
                for safe_poi in p_candidates:
                    w_lat = safe_poi["geometry"]["location"]["lat"]
                    w_lng = safe_poi["geometry"]["location"]["lng"]
                    gmaps_wp_url = (
                        f"https://maps.googleapis.com/maps/api/directions/json"
                        f"?origin={slat},{slng}&destination={elat},{elng}"
                        f"&waypoints=via:{w_lat},{w_lng}&mode=walking&key={GOOGLE_MAPS_API_KEY}"
                    )
                    resp_wp = http_requests.get(gmaps_wp_url, timeout=8)
                    data_wp = resp_wp.json()
                    
                    if data_wp.get("status") == "OK" and data_wp.get("routes"):
                        route_wp = data_wp["routes"][0]
                        import polyline
                        coords_wp = polyline.decode(route_wp["overview_polyline"]["points"])
                        danger_info_wp = route_passes_danger(coords_wp, all_dangers)
                        
                        if not danger_info_wp["passes_danger"]:
                            dist_wp = sum(leg["distance"]["value"] for leg in route_wp["legs"])
                            dur_wp = sum(leg["duration"]["value"] for leg in route_wp["legs"])
                            
                            routes.append({
                                "index": 1000 + len(routes),
                                "tag": f"🛡️ Recommended (via {safe_poi.get('name', 'Safe Path')})",
                                "safety": "safe",
                                "distance_m": round(dist_wp),
                                "duration_min": round(dur_wp / 60, 1),
                                "coords": coords_wp,
                                "danger_info": danger_info_wp,
                            })
        except Exception as e:
            print(f"[fallback-multi-poi] error: {e}")

    # Final Sort
    routes.sort(key=lambda r: (0 if r["safety"] == "safe" else 1, r["distance_m"]))

    # Re-tag after sorting: best safe = recommended
    for i, r in enumerate(routes):
        if i == 0 and r["safety"] == "safe":
            r["tag"] = "🛡️ Recommended (Patronus Protected)"
        elif r["safety"] == "safe":
            r["tag"] = "🛡️ Safe Alternative"

    return jsonify({"routes": routes})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Start serial listener in a daemon thread
    t = threading.Thread(target=serial_listener, daemon=True)
    t.start()
    print("✦ Mischief Managed — server starting on http://127.0.0.1:5000")
    app.run(debug=False, host="0.0.0.0", port=5000)
