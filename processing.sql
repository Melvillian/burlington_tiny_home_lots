create index on new_north_end_parcels using gist(wkb_geometry);
create index on new_north_end_buildings using gist(wkb_geometry);

-- add 15 feet (4.572 meters) buffer to all building geometries, because according to Burlington city ordinances
-- all secondary buildings must be set back 15 feet from the other buildings
create table buffered_buildings as select st_buffer(wkb_geometry, 4.572) as geom from new_north_end_buildings;

-- subtract 15 feet from the parcel geometries, because according to Burlington city ordinances
-- there must be a 15 feet setback from the parcel boundary to the building
create table setback_parcels as
select st_buffer(wkb_geometry, -4.572) as geom,
       siteaddress,
       ogc_fid
from new_north_end_parcels;

-- now finally subtract the buffered buildings from the setback parcels to get the buildable parcel areas
create table buildable_parcel_areas as
select
    st_astext(st_difference(st_makevalid(new_north_end_parcels.geom), st_union(buffered_buildings.geom))) as geom,
    siteaddress,
    new_north_end_parcels.ogc_fid,
    NULL::text as tiny_home_structure
from setback_parcels as new_north_end_parcels, buffered_buildings
where st_intersects(buffered_buildings.geom, new_north_end_parcels.geom)
group by new_north_end_parcels.ogc_fid, new_north_end_parcels.geom, siteaddress;