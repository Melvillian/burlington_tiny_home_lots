import geopandas as gpd
from shapely import wkt
import matplotlib.pyplot as plt
from psycopg2 import pool
import random

# a helper functions cript to visualize arbitrary geometries (which are the parcels, buildings, and rectangles that we're working with)


def visualize_parcel_and_buildings(
    parcel_num, parcel_address, parcel_polygon, tiny_home_polygon
):
    parcel_geom = wkt.loads(parcel_polygon)
    tiny_home_geom = wkt.loads(tiny_home_polygon)

    # Create GeoDataFrames for both geometries
    parcel_gdf = gpd.GeoDataFrame(geometry=[parcel_geom])
    structure_gdf = gpd.GeoDataFrame(geometry=[tiny_home_geom])

    # Create the plot
    fig, ax = plt.subplots()

    # Plot parcel in blue with transparency
    parcel_gdf.plot(ax=ax, color="blue", alpha=0.3)

    # Plot tiny home structure in red on top
    structure_gdf.plot(ax=ax, color="red")

    plt.title(f"#{parcel_num}: {parcel_address}")

    # Make sure the aspect ratio is equal
    plt.axis("equal")

    # Show the plot
    plt.show()


# Create a threadsafe connection pool
connection_pool = pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=20,  # Adjust based on your parallel process count
    dbname="postgres",
    user="postgres",
    password="postgres",
    host="localhost",
    port=6543,
)

conn = connection_pool.getconn()

cursor = conn.cursor()

# Query setback parcels
cursor.execute(
    """
    SELECT ogc_fid, siteaddress, geom, tiny_home_structure
    FROM buildable_parcel_areas
    WHERE tiny_home_structure IS NOT NULL AND
    tiny_home_structure != ''
"""
)

rows = cursor.fetchall()
random_rows = random.sample(rows, 10)

# we're done with the pre-task db usage, so let's tidy up
# those db resources
cursor.close()
connection_pool.putconn(conn)


for [id, address, parcel_polygon, tiny_home_polygon] in random_rows:
    visualize_parcel_and_buildings(id, address, parcel_polygon, tiny_home_polygon)
