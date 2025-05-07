import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium
from folium.plugins import MarkerCluster

# Load Datasets
# Assume CSV files with lat/lon
bus_stops_df = pd.read_csv("bus_stops.csv")  # columns: stop_id, name, lat, lon
routes_df = pd.read_csv("bus_routes.csv")    # columns: route_id, stop_id, schedule_time
air_quality_df = pd.read_csv("air_quality.csv")  # columns: station_id, lat, lon, PM2.5, PM10, NO2, O3

# Convert to GeoDataFrames
bus_stops_gdf = gpd.GeoDataFrame(bus_stops_df, geometry=gpd.points_from_xy(bus_stops_df.lon, bus_stops_df.lat))
air_quality_gdf = gpd.GeoDataFrame(air_quality_df, geometry=gpd.points_from_xy(air_quality_df.lon, air_quality_df.lat))

# Match each bus stop to the nearest air quality station
def get_nearest_station(stop_geom, stations_gdf):
    distances = stations_gdf.geometry.distance(stop_geom)
    return stations_gdf.iloc[distances.idxmin()]

# Annotate each bus stop with nearest station's air quality
bus_stops_gdf[['PM2.5', 'PM10', 'NO2', 'O3']] = bus_stops_gdf.apply(
    lambda row: get_nearest_station(row.geometry, air_quality_gdf)[['PM2.5', 'PM10', 'NO2', 'O3']],
    axis=1, result_type="expand"
)

# Define pollution thresholds (simplified for visualization)
def get_pollution_level(pm25):
    if pm25 <= 12:
        return 'Good'
    elif pm25 <= 35:
        return 'Moderate'
    else:
        return 'Unhealthy'

bus_stops_gdf['Air_Quality'] = bus_stops_gdf['PM2.5'].apply(get_pollution_level)

# Visualize using Folium
m = folium.Map(location=[24.4539, 54.3773], zoom_start=11)
marker_cluster = MarkerCluster().add_to(m)

for _, row in bus_stops_gdf.iterrows():
    color = {'Good': 'green', 'Moderate': 'orange', 'Unhealthy': 'red'}.get(row['Air_Quality'], 'gray')
    popup = f"""
    <b>Bus Stop:</b> {row['name']}<br>
    <b>PM2.5:</b> {row['PM2.5']}<br>
    <b>Air Quality:</b> {row['Air_Quality']}
    """
    folium.Marker(
        location=[row.geometry.y, row.geometry.x],
        popup=popup,
        icon=folium.Icon(color=color)
    ).add_to(marker_cluster)

# Save or display the map
m.save("transport_airquality_map.html")
print("Map saved to 'transport_airquality_map.html'")
