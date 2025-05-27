import xml.etree.ElementTree as ET
from datetime import datetime
import re
import õhurõhk

# Pressure to altitude conversion (standard atmosphere)
def pressure_to_altitude(pressure_hpa, sea_level_pressure=1013.25, T0=20):
    return (T0 + 273.15) / 0.0065 * (1.0 - (pressure_hpa / sea_level_pressure) ** 0.1903)

# Read file and parse records
def parse_nmea_with_pressure(filename):
    gpx_points = []

    sea_level_pressure = õhurõhk.merepinnal(save=False)
    T0 = 22

    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    i = 0
    while i < len(lines) - 1:
        line = lines[i]
        next_line = lines[i+1]

        if line.startswith("$GPGGA") and not next_line.startswith("$"):
            parts = line.split(",")
            time_str = parts[1]
            lat_raw = parts[2]
            lat_dir = parts[3]
            lon_raw = parts[4]
            lon_dir = parts[5]
            precision = float(parts[8])
            gps_alt = float(parts[9])  # GPS altitude in meters

            # Convert NMEA to decimal degrees
            lat = float(lat_raw[:2]) + float(lat_raw[2:]) / 60.0
            if lat_dir == 'S':
                lat = -lat

            lon = float(lon_raw[:3]) + float(lon_raw[3:]) / 60.0
            if lon_dir == 'W':
                lon = -lon

            bar_altitude = pressure_to_altitude(float(next_line), sea_level_pressure, T0) +10

            # Convert time to ISO format (just time since no full timestamp)
            iso_time = f"2025-05-21T{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}Z"

            gpx_points.append((lat, lon, gps_alt, bar_altitude, iso_time))

            i += 2  # Skip pressure line
        else:
            i += 1

    return gpx_points

# Generate GPX XML
def generate_gpx(points, output_file, gps_ele = False):
    gpx = ET.Element("gpx", version="1.1", creator="NMEA-Pressure-Converter", xmlns="http://www.topografix.com/GPX/1/1")
    trk = ET.SubElement(gpx, "trk")
    trkseg = ET.SubElement(trk, "trkseg")

    for lat, lon, ele, baro_ele, time in points:
        trkpt = ET.SubElement(trkseg, "trkpt", lat=f"{lat:.6f}", lon=f"{lon:.6f}")
        if gps_ele:
            ET.SubElement(trkpt, "ele").text = f"{ele:.2f}"
        else:
            ET.SubElement(trkpt, "ele").text = f"{baro_ele:.2f}"
        ET.SubElement(trkpt, "time").text = time

    tree = ET.ElementTree(gpx)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)

def rework_file(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    for line in lines:
        print(line)

# ---- Run conversion ----
input_file = "uart_log (7).txt"
output_file_gps = f"{input_file[:-4]}_gps.gpx"
output_file_bar = f"{input_file[:-4]}_bar.gpx"


points = parse_nmea_with_pressure(input_file)
#generate_gpx(points, output_file_gps, gps_ele=True)
generate_gpx(points, output_file_bar)

print(f"Generated files with {len(points)} points.")
