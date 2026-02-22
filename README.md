# ✦ Sensory Safety Marauder's Map ✦

**"I solemnly swear that I am up to no good... but also searching for a safe path."**

The **Sensory Safety Marauder's Map** is a premium, interactive Potter-themed navigation engine designed to help neurodivergent individuals and sensory-sensitive students navigate complex environments. By fusing real-time hardware data with a state-of-the-art "Magical Glass" UI, it detects **Dementor Zones** (high-stimulation areas like loud noises or crowds) and yields **Patronus Protected** safe-harbor routes.

---

## 🧭 Premium Features

### 💎 Ultra-Translucent "Magical Glass" UI
- **Glassmorphic Design**: A near-transparent floating interface that lets you see the map while managing your journey.
- **Dynamic Micro-Animations**: Features a custom **Elder Wand Cursor** that follows your movements, with a glowing tip that illuminates when hovering over interactive elements.
- **Tabbed Sidebar Architecture**: Seamlessly toggle between "☠️ Dangers" (real-time alerts) and "⚡ Routes" to keep your view focused and clutter-free.

### 🛡️ Smart Sensory Navigation
- **Real-Time Dementor Alerts**: Integrated with Arduino sensory hardware to log disturbances instantly.
- **Patronus Route Engine**: Uses **Google Directions & Places APIs** to calculate multi-route comparisons, highlighting the safest detours that avoid logged Dementor presence.
- **Visual Contrast Boost**: Optimized typography with magical halos (text-shadows) ensures crystal-clear legibility against the complex, parchment-themed map tiles.

### 🪄 Enchanted Aesthetics
- **Metallic Craftsmanship**: Buttons are forged with multi-stop 24k gold gradients, shimmering light-sweeps, and magical glows.
- **Authentic Theme**: Features a custom interactive parchment filter and icons inspired by the legendary wizarding map.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+ (Flask Framework)
- **Frontend**: ES6+ JavaScript, Vanilla CSS3 (Glassmorphism & SVG Animations)
- **Mapping Engine**: Leaflet.js (Custom Tile Processing & Layers)
- **Intelligence Layer**: 
  - **Google Maps Directions API**: Real-time pedestrian route logic.
  - **Google Maps Places API**: Sensory landmark identification.
  - **OpenStreetMap (Nominatim)**: Strategic geocoding.
- **Hardware Integration**: Arduino Serial (Sensory Data Relay)

---

## 🚀 Setup & Installation

### 1. Prerequisites
- Python 3.10+
- Google Cloud Platform API Key (Directions, Places, Maps JS enabled)
- (Optional) Arduino with sound/proximity sensors

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/Param2k23/Hopper-Hacks-2026.git
cd Hopper-Hacks-2026

# Install dependencies
pip install flask pyserial requests polyline
```

### 3. Configuration
1. Open `app.py`.
2. Locate `GOOGLE_MAPS_API_KEY` and insert your actual key.
3. Update `COM_PORT` (e.g., `COM3`, `/dev/ttyUSB0`) to match your sensor hardware.

### 4. Ignite the Map
```bash
python app.py
```
Visit `http://127.0.0.1:5000` to begin your journey.

---

## 📂 Project Structure
- `app.py`: The magical brain handling serial data, route logic, and API calls.
- `index.html`: The core map interface and glassmorphic sidebar.
- `style.css`: All the CSS glass tokens, wand animations, and metallic button shaders.
- `arduino/`: Firmware for the sensory-detection wand/hardware.
- `map_data.json`: The living record of all Dementor presence on campus.

## 📜 Credits
Developed for **Hopper Hacks 2026**.

---
*Mischief Managed.*
