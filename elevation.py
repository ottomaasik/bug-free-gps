import gpxpy
import matplotlib.pyplot as plt
from gpxpy.geo import haversine_distance


def extract_elevation_and_distance(file_path):
    with open(file_path, 'r') as f:
        gpx = gpxpy.parse(f)

    distances = []
    elevations = []
    total_dist = 0.0

    for track in gpx.tracks:
        for segment in track.segments:
            prev_point = None
            for point in segment.points:
                if point.elevation is not None:
                    if prev_point:
                        dist = haversine_distance(
                            prev_point.latitude, prev_point.longitude,
                            point.latitude, point.longitude
                        )
                        total_dist += dist
                    distances.append(total_dist / 1000.0)  # in km
                    elevations.append(point.elevation)
                    prev_point = point
    return distances, elevations


# Replace with your file paths
gpx_barometric = "uart_log (7)_bar.gpx"
gpx_gps = "uart_log (7)_gps.gpx"
gpx_osm = "uart_log (7)_map.gpx"

# Load data
d_baro, e_baro = extract_elevation_and_distance(gpx_barometric)
d_gps, e_gps = extract_elevation_and_distance(gpx_gps)
d_osm, e_osm = extract_elevation_and_distance(gpx_osm)

# Plotting
plt.figure(figsize=(10, 6), dpi=300)
plt.plot(d_baro, e_baro, alpha=0.5, label='Baromeetriline*')
plt.plot(d_gps, e_gps, alpha=0.5, label='GPS')
plt.plot(d_osm, e_osm, label='Mapbox')

plt.xlim(d_baro[0], d_baro[-1])
plt.xlabel("Kaugus (km)")
plt.ylabel("Kõrgus (m)")
plt.title("Kõrgus profiilide võrdlus")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("profile.png")
plt.show()
