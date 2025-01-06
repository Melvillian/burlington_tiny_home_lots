from shapely.geometry import Polygon, box
from shapely.affinity import rotate
import numpy as np
import psycopg2
from shapely import wkb
from shapely.wkt import loads

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
                                # Rotate rectangle back to original orientation
                                best_rectangle = rotate(test_rect, -angle)
                                best_angle = angle

                                # speed up the process by short circuiting if the area is large enough
                                if area >= minimum_are_needed:
                                    return best_rectangle, area, best_angle

    return best_rectangle, max_area, best_angle


def check_parcel_buildability(
    conn, min_area=MINIMUM_SIZE_OF_SECONDARY_UNIT_METERS
):  # 350 sq ft in sq meters
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

    num_parcels = 0
    for address, geom_wkt in cursor:
        num_parcels += 1
        # print(f"Checking {address}")
        polygon = loads(geom_wkt)
        rectangle, area, angle = find_largest_inscribed_rectangle(polygon)

        if area >= min_area:
            print(
                f"Found buildable parcel: #{num_parcels} {address} with area {area:.1f} sq meters"
            )

            buildable_parcels.append(
                {
                    "num_parcel": num_parcels,
                    "address": address,
                    "area": area,
                    "angle": angle,
                }
            )
            with open("buildable_parcels.txt", "a") as f:
                f.write(f"#{num_parcels} {address}: {area:.2f} square meters\n")

    return buildable_parcels, num_parcels


if __name__ == "__main__":
    conn = psycopg2.connect(
        "host=localhost dbname=postgres user=postgres password=postgres port=6543"
    )

    buildable, num_parcels = check_parcel_buildability(conn)
    num_buildable = len(buildable)

    print(
        f"Found {num_buildable} parcels out of {num_parcels} that could fit a 350 sq ft tiny home"
    )
    print(f"Sample of buildable parcels:")
    for parcel in buildable[:5]:
        print(
            f"Address: {parcel['address']}, Buildable Area: {parcel['area']:.1f} sq meters"
        )
