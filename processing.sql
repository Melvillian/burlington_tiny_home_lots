create index on new_north_end_parcels using gist(wkb_geometry);
create index on new_north_end_buildings using gist(wkb_geometry);

create table buffered_buildings as select st_buffer(wkb_geometry, 4.572) as geom from new_north_end_buildings;

create table setback_parcels as
select st_buffer(wkb_geometry, -4.572) as geom,
       siteaddress,
       ogc_fid
from new_north_end_parcels;

create table buildable_parcel_areas as
select
    st_astext(st_difference(st_makevalid(new_north_end_parcels.geom), st_union(buffered_buildings.geom))) as geom,
    siteaddress,
    new_north_end_parcels.ogc_fid
from setback_parcels as new_north_end_parcels, buffered_buildings
where st_intersects(buffered_buildings.geom, new_north_end_parcels.geom)
group by new_north_end_parcels.ogc_fid, new_north_end_parcels.geom, siteaddress;