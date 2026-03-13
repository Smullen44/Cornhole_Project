import unittest
import pygame
import math

from Midterm_Code import *


class TestHelperFunctions(unittest.TestCase):

    def test_clamp_within_range(self):
        self.assertEqual(clamp(5, 0, 10), 5)

    def test_clamp_below_min(self):
        self.assertEqual(clamp(-3, 0, 10), 0)

    def test_clamp_above_max(self):
        self.assertEqual(clamp(15, 0, 10), 10)

    def test_clamp_at_boundaries(self):
        self.assertEqual(clamp(0, 0, 10), 0)
        self.assertEqual(clamp(10, 0, 10), 10)

    def test_distance_squared_same_point(self):
        self.assertEqual(distance_squared((0, 0), (0, 0)), 0)

    def test_distance_squared_known_value(self):
        self.assertEqual(distance_squared((0, 0), (3, 4)), 25)

    def test_distance_squared_negative_coords(self):
        self.assertEqual(distance_squared((-1, -1), (2, 3)), 25)


class TestBag(unittest.TestCase):

    def setUp(self):
        self.bag = Bag((100, 400), 10)

    def test_initial_position(self):
        self.assertEqual(self.bag.pos, [100, 400])
        self.assertFalse(self.bag.in_flight)

    def test_reset(self):
        self.bag.pos = [500, 200]
        self.bag.in_flight = True
        self.bag.reset()
        self.assertEqual(self.bag.pos, [100, 400])
        self.assertFalse(self.bag.in_flight)

    def test_launch_sets_in_flight(self):
        self.bag.launch(45, 10)
        self.assertTrue(self.bag.in_flight)

    def test_launch_velocity_direction(self):
        self.bag.launch(45, 10)
        self.assertGreater(self.bag.vel[0], 0)
        self.assertLess(self.bag.vel[1], 0)

    def test_launch_horizontal(self):
        self.bag.launch(0, 10)
        self.assertAlmostEqual(self.bag.vel[0], 10, places=2)
        self.assertAlmostEqual(self.bag.vel[1], 0, places=2)

    def test_update_no_movement_when_grounded(self):
        self.bag.update(0.35)
        self.assertEqual(self.bag.pos, [100, 400])

    def test_update_applies_gravity(self):
        self.bag.launch(45, 10)
        initial_vy = self.bag.vel[1]
        self.bag.update(0.35)
        self.assertGreater(self.bag.vel[1], initial_vy)


class TestBoard(unittest.TestCase):

    def setUp(self):
        pygame.init()
        self.board = Board(pygame.Rect(650, 260, 180, 200), (740, 310), 22)

    def test_bag_in_hole(self):
        pts, msg = self.board.score_bag((740, 310), 10)
        self.assertEqual(pts, 3)

    def test_bag_on_board(self):
        pts, msg = self.board.score_bag((700, 400), 10)
        self.assertEqual(pts, 1)

    def test_bag_miss(self):
        pts, msg = self.board.score_bag((100, 100), 10)
        self.assertEqual(pts, 0)

    def test_bag_on_board_edge(self):
        pts, msg = self.board.score_bag((651, 261), 10)
        self.assertEqual(pts, 1)

    def test_bag_just_outside_board(self):
        pts, msg = self.board.score_bag((649, 259), 10)
        self.assertEqual(pts, 0)


if __name__ == "__main__":
    unittest.main()