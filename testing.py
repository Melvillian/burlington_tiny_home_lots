import unittest
from shapely.geometry import Polygon
from main import find_largest_inscribed_rectangle


class TestLargestInscribedRectangle(unittest.TestCase):
    def test_square_polygon(self):
        # A 10x10 square should fit a 10x10 rectangle
        square = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
        rectangle, area, angle = find_largest_inscribed_rectangle(square, precision=1.0)
        self.assertAlmostEqual(area, 100.0, places=1)

    def test_rectangle_polygon(self):
        # A 20x10 rectangle should fit a rectangle of area 200
        rectangle = Polygon([(0, 0), (20, 0), (20, 10), (0, 10)])
        result_rect, area, angle = find_largest_inscribed_rectangle(
            rectangle, precision=1.0
        )
        self.assertAlmostEqual(area, 200.0, places=1)

    def test_triangle_polygon(self):
        # Right triangle with base 10 and height 10
        triangle = Polygon([(0, 0), (10, 0), (0, 10)])
        rectangle, area, angle = find_largest_inscribed_rectangle(
            triangle, precision=1.0
        )
        # The largest rectangle in a right triangle should be smaller than the triangle area (50)
        self.assertLess(area, 50.0)
        self.assertGreater(area, 0.0)

    def test_irregular_polygon(self):
        # L-shaped polygon
        l_shape = Polygon([(0, 0), (10, 0), (10, 5), (5, 5), (5, 10), (0, 10)])
        rectangle, area, angle = find_largest_inscribed_rectangle(
            l_shape, precision=1.0
        )
        self.assertGreater(area, 0.0)

    def test_minimum_area_requirement(self):
        # Test with a polygon too small to meet minimum requirements
        small_square = Polygon([(0, 0), (5, 0), (5, 5), (0, 5)])
        rectangle, area, angle = find_largest_inscribed_rectangle(
            small_square,
            precision=1.0,
            minimum_are_needed=100,  # Requiring larger area than possible
        )
        self.assertLess(area, 100.0)

    def test_rotated_case(self):
        # Diamond shape (square rotated 45 degrees)
        diamond = Polygon([(5, 0), (10, 5), (5, 10), (0, 5)])
        rectangle, area, angle = find_largest_inscribed_rectangle(
            diamond, precision=1.0
        )
        self.assertGreater(area, 0.0)

    def test_invalid_polygon(self):
        # Test with an invalid polygon (less than 3 points)
        invalid_polygon = Polygon([(0, 0), (1, 1)])
        with self.assertRaises(Exception):
            find_largest_inscribed_rectangle(invalid_polygon)


if __name__ == "__main__":
    unittest.main()
