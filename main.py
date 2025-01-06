from shapely.geometry import Polygon, box
from shapely.affinity import rotate
import numpy as np
import psycopg2
from shapely import wkb
from shapely.wkt import loads


def find_largest_inscribed_rectangle(polygon, precision=1.0, angle_step=5):
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
        print(
            "angle: ",
            angle,
            "rot_minx: ",
            rot_minx,
            "rot_miny: ",
            rot_miny,
            "rot_maxx: ",
            rot_maxx,
            "rot_maxy: ",
            rot_maxy,
        )
        # Create a grid of points to test
        for x in np.arange(rot_minx, rot_maxx, precision):
            for y in np.arange(rot_miny, rot_maxy, precision):
                print("x: ", x, "y: ", y)
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
                                # Rotate rectangle back to original orientation
                                best_rectangle = rotate(test_rect, -angle)
                                best_angle = angle

    return best_rectangle, max_area, best_angle


def check_parcel_buildability(conn, min_area=32.516):  # 350 sq ft in sq meters
    cursor = conn.cursor()

    # Query setback parcels
    cursor.execute(
        """
        SELECT siteaddress, geom 
        FROM setback_parcels
        WHERE geom IS NOT NULL
    """
    )

    buildable_parcels = []

    for address, geom_wkt in cursor:
        print(f"Checking {address}")
        polygon = loads(geom_wkt)
        rectangle, area, angle = find_largest_inscribed_rectangle(polygon)

        if area >= min_area:
            print(f"Found buildable parcel: {address} with area {area:.1f} sq meters")
            buildable_parcels.append({"address": address, "area": area, "angle": angle})

    return buildable_parcels


if __name__ == "__main__":
    conn = psycopg2.connect(
        "host=localhost dbname=postgres user=postgres password=postgres port=6543"
    )

    buildable = check_parcel_buildability(conn)
    total_parcels = len(buildable)

    print(f"Found {total_parcels} parcels that could fit a 350 sq ft tiny home")
    print(f"Sample of buildable parcels:")
    for parcel in buildable[:5]:
        print(
            f"Address: {parcel['address']}, Buildable Area: {parcel['area']:.1f} sq meters"
        )
