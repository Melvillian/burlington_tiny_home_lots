#!/bin/bash

# Create a docker container with postgis
# The data directory is mounted locally, so data will persist across database 
# start / stops. there's a better way to do this with docker volumes, 
# but this is what I know how to do without querying any external source of knowledge.
docker run --rm -d --name btv_tiny_homes -p 6543:5432 -v $(pwd)/pgdata:/tmp/pgdata -e POSTGRES_PASSWORD=postgres -e PGDATA=/tmp/pgdata postgis/postgis:latest

# Clip the buildings dataset and project to [UTM zone 19](https://epsg.io/26919)
# so that we can use meters for calculations and check it
ogr2ogr -f GeoJSON new_north_end_buildings.geojson Vermont.geojson -spat -73.277012 44.445915 -73.175797 44.539938 -t_srs EPSG:26919

# Reproject tax parcels to utm as well
ogr2ogr -f GeoJSON parcels.geojson Tax_Parcels.geojson -t_srs EPSG:26919

# Load to postgres for further processing
ogr2ogr -f PostgreSQL PG:"host=localhost user=postgres password=postgres port=6543" parcels.geojson -nln new_north_end_parcels
ogr2ogr -f PostgreSQL PG:"host=localhost user=postgres password=postgres port=6543" new_north_end_buildings.geojson -nln new_north_end_buildings

PGPASSWORD=postgres psql -h localhost -p 6543 -U postgres -d postgres -f processing.sql