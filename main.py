from shapely.geometry import box
import numpy as np
from shapely.affinity import rotate
from psycopg2 import pool
from shapely.wkt import loads

from multiprocessing import Pool, cpu_count

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

MINIMUM_SIZE_OF_SECONDARY_UNIT_METERS = (
    32.516  # 350 sq ft in sq meters. No building in Burlington can be smaller than this
)


def find_largest_inscribed_rectangle(
    polygon,
    precision=3.0,
    angle_step=30,
    minimum_are_needed=MINIMUM_SIZE_OF_SECONDARY_UNIT_METERS,
):
    """
    Find the largest inscribed rectangle within a polygon.

    Args:
        polygon: Shapely Polygon object
        precision: Step size for the grid search (meters)
        angle_step: Rotation angle step size (degrees)

    Returns:
        tuple: (largest_rectangle, area, angle)
    """
    max_area = 0
    best_rectangle = None
    best_angle = 0

    # Try different rotation angles
    for angle in range(0, 90, angle_step):
        # Rotate polygon to test this orientation
        rotated = rotate(polygon, angle)
        rot_minx, rot_miny, rot_maxx, rot_maxy = rotated.bounds

        # Create a grid of points to test
        for x in np.arange(rot_minx, rot_maxx, precision):
            for y in np.arange(rot_miny, rot_maxy, precision):
                # Try growing rectangles from this point
                for width in np.arange(precision, rot_maxx - x, precision):
                    for height in np.arange(precision, rot_maxy - y, precision):
                        # Create test rectangle
                        test_rect = box(x, y, x + width, y + height)

                        # Check if rectangle is fully within polygon
                        if rotated.contains(test_rect):
                            area = test_rect.area
                            if area > max_area:
                                max_area = area
                                best_rectangle = test_rect
                                best_angle = angle

                                # speed up the process by short circuiting if the rectnagle is large enough
                                # to fit in the minimum Burlington tiny home structure size
                                if area >= minimum_are_needed:
                                    return str(best_rectangle), area, best_angle

    return str(best_rectangle), max_area, best_angle


def check_parcel_buildability(min_area=MINIMUM_SIZE_OF_SECONDARY_UNIT_METERS):
    conn = connection_pool.getconn()

    cursor = conn.cursor()

    # Query setback parcels
    cursor.execute(
        """
        SELECT ogc_fid, siteaddress, geom, tiny_home_structure
        FROM buildable_parcel_areas
        WHERE geom IS NOT NULL
    """
    )

    buildable_parcels = []

    # Create a process pool with number of CPUs available
    pool = Pool(processes=cpu_count())

    # Prepare all tasks
    tasks = []
    rows = cursor.fetchall()

    # we're done with the pre-task db usage, so let's tidy up
    # those db resources
    cursor.close()
    connection_pool.putconn(conn)

    for ogc_fid, address, geom_wkt, tiny_home_structure in rows:
        tasks.append((ogc_fid, address, geom_wkt, tiny_home_structure, min_area))

    errors = []
    for result in pool.starmap(process_polygon, tasks):
        if isinstance(result, Exception):
            errors.append(result)

    # Print errors after all tasks complete
    print("Errors:")
    for error in errors:
        print(f"Error processing parcel: {error}")

    # now that we've updated the DB with the results,
    # let's fetch those results, cleanup, and return our results

    conn = connection_pool.getconn()
    cursor = conn.cursor()

    # Query setback parcels
    cursor.execute(
        """
        SELECT ogc_fid, siteaddress, geom, tiny_home_structure
        FROM buildable_parcel_areas
        WHERE geom IS NOT NULL
    """
    )

    rows = cursor.fetchall()

    # we're done with the pre-task db usage, so let's tidy up
    # those db resources
    cursor.close()
    connection_pool.putconn(conn)

    buildable_parcels = []
    nonbuildable_parcels = []
    missed_parcels = []
    for ogc_fid, address, geom_wkt, tiny_home_structure in rows:
        if tiny_home_structure == "":
            nonbuildable_parcels.append(
                (ogc_fid, address, geom_wkt, tiny_home_structure)
            )
        elif tiny_home_structure is not None and tiny_home_structure != "":
            buildable_parcels.append((ogc_fid, address, geom_wkt, tiny_home_structure))
        else:
            missed_parcels.append((ogc_fid, address, geom_wkt, tiny_home_structure))

    return len(rows), buildable_parcels, nonbuildable_parcels, missed_parcels


def process_polygon(parcel_num, address, geom_wkt, tiny_home_structure, min_area):
    # print(f"Checking {address}")
    conn = connection_pool.getconn()
    try:
        if tiny_home_structure is not None:
            return

        # we haven't attempted to find a rectangle for this parcel yet,
        # so let's do that
        polygon = loads(geom_wkt)
        tiny_home_rectangle, area, angle = find_largest_inscribed_rectangle(polygon)

        if area >= min_area:
            print(
                f"Found buildable parcel: #{parcel_num} {address} with area {area:.1f} sq meters"
            )

            # update the buildable_parcel_areas table
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE buildable_parcel_areas
                SET tiny_home_structure = %s 
                WHERE ogc_fid = %s
            """,
                (tiny_home_rectangle, parcel_num),
            )
            conn.commit()
            cursor.close()
        else:
            # no rectangle found, so we're not buildable.
            # we represent that in the DB with an empty string
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE buildable_parcel_areas
                SET tiny_home_structure = %s 
                WHERE ogc_fid = %s
            """,
                ("", parcel_num),
            )
            conn.commit()
            cursor.close()
    except Exception as e:
        return e
    finally:
        # Always return connection to pool
        connection_pool.putconn(conn)


if __name__ == "__main__":

    num_parcels, buildable_parcels, nonbuildable_parcels, missed_parcels = (
        check_parcel_buildability()
    )

    # Clean up pool at end
    connection_pool.closeall()

    num_buildable = len(buildable_parcels)

    print(
        f"Found {len(buildable_parcels)} parcels out of {num_parcels} that could fit a 350 sq ft tiny home"
    )
    print(
        f"Found {len(nonbuildable_parcels)} parcels out of {num_parcels} that could NOT fit a 350 sq ft tiny home"
    )
    print(
        f"Found {len(missed_parcels)} parcels out of {num_parcels} that where something went wrong and we didn't process them correctly"
    )

    print(
        "Analysis complete. Query the buildable_parcel_areas table of the database to find examples"
    )
