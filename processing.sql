create index on new_north_end_parcels using gist(wkb_geometry);
create index on new_north_end_buildings using gist(wkb_geometry);

create table buffered_buildings as select st_buffer(wkb_geometry, 4.572) as geom from new_north_end_buildings;

select st_astext(st_collect(geom)) as buildings, st_astext(st_collect(wkb_geometry)) as parcels
from buffered_buildings, new_north_end_parcels
where st_intersects(buffered_buildings.geom, new_north_end_parcels.wkb_geometry)
  and siteaddress = '472 ETHAN ALLEN PKWY';

    select st_astext(st_difference(new_north_end_parcels.wkb_geometry, st_union(buffered_buildings.geom))) as geom
from new_north_end_parcels, buffered_buildings
where st_intersects(buffered_buildings.geom, new_north_end_parcels.wkb_geometry)
    and siteaddress = '472 ETHAN ALLEN PKWY'
group by new_north_end_parcels.ogc_fid

create table setback_parcels as
select st_buffer(wkb_geometry, -4.572) as geom,
       siteaddress,
       ogc_fid
from new_north_end_parcels;

create table buildable_parcel_areas as
select
    st_difference(st_makevalid(new_north_end_parcels.geom), st_union(buffered_buildings.geom)) as geom,
    siteaddress,
    new_north_end_parcels.ogc_fid
from setback_parcels as new_north_end_parcels, buffered_buildings
where st_intersects(buffered_buildings.geom, new_north_end_parcels.geom)
group by new_north_end_parcels.ogc_fid