# ✦ Sensory Safety Marauder's Map ✦

**"I solemnly swear that I am up to no good... but also searching for a safe path."**

The **Sensory Safety Marauder's Map** is an interactive, Harry Potter-themed navigation tool designed to help students and neurodivergent individuals navigate the Stony Brook University campus safely. By integrating physical sensors with digital mapping, it identifies areas with high sensory triggers (loud noises, crowds, or intense lighting) and provides safe, "Patronus Protected" walking detours.

## 🪄 Key Features

- **Real-Time Danger Detection**: Integrated with Arduino sensors that listen for "DANGER" signals (noise, crowds, or sensory overload) and log them instantly as "Dementor Presence" coordinates on the map.
- **High-Visibility Safety Zones**: Dangerous areas are marked with prominent, high-contrast red zones, ensuring they are easily identifiable at a glance.
- **Smart Safety Detours**: When a direct route passes through a danger zone, the system automatically uses **Google Places API** and **Directions API** to find safe landmarks and calculate a natural walking detour.
- **Themed Experience**: A fully customized UI featuring parchment-style aesthetics, custom markers, and animations inspired by the wizarding world.

## 🛠️ Technology Stack

- **Backend**: Python (Flask)
- **Frontend**: HTML5, Vanilla CSS, JavaScript (Leaflet.js)
- **Mapping APIs**: 
  - **Google Maps Directions API**: For pedestrian route calculation.
  - **Google Maps Places API**: For identifying safe landmarks and corridors.
  - **OpenStreetMap (Nominatim)**: For geocoding and search bias.
- **Hardware Integration**: Arduino (Serial Communication)
- **Data Persistence**: JSON-based coordinate storage.

## 🚀 Setup & Installation

### 1. Prerequisites
- Python 3.10+
- A Google Cloud Platform account with **Directions API**, **Places API**, and **Maps SDK for JavaScript** enabled.
- (Optional) An Arduino with a sound/sensory sensor.

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/Param2k23/Hopper-Hacks-2026.git
cd Hopper-Hacks-2026

# Install dependencies
pip install flask pyserial requests polyline
```

### 3. Configuration
Open `app.py` and update the following:
- `GOOGLE_MAPS_API_KEY`: Replace `"YOUR_API_KEY_HERE"` with your actual Google Cloud API key.
- `COM_PORT`: Update to match your Arduino's serial port (e.g., `COM3`, `/dev/ttyUSB0`).

### 4. Running the Application
```bash
python app.py
```
Visit `http://127.0.0.1:5000` in your browser.

## 📂 Project Structure
- `app.py`: The Flask backend handling data processing, routing, and serial communication.
- `templates/index.html`: The interactive parchment map and sidebar UI.
- `static/style.css`: Custom wizarding-world themes and map styling.
- `arduino/`: Contains the firmware (`sketch_feb21a.ino`) for the sensory detection hardware.
- `map_data.json`: The live database of logged danger coordinates.

## 📜 Credits
Developed for **Hopper Hacks 2026**.

---
*Mischief Managed.*
