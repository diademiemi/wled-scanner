import math
import os

import cv2
import numpy as np
import sympy as smpy


def compute(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

    (minVal, maxVal, minLoc, (x, y)) = cv2.minMaxLoc(image)

    return x, y, maxVal


class Point:
    def __init__(self, index):
        self.index = index

        self.image_0 = cv2.imread(f'images/0/{index}.png')
        self.image_90 = cv2.imread(f'images/90/{index}.png')
        self.image_180 = cv2.imread(f'images/180/{index}.png')
        self.image_270 = cv2.imread(f'images/270/{index}.png')

        self.x = None
        self.y = None
        self.z = None

        self.image_0_x = None
        self.image_0_y = None
        self.image_0_weight = None

        self.image_90_x = None
        self.image_90_y = None
        self.image_90_weight = None

        self.image_180_x = None
        self.image_180_y = None
        self.image_180_weight = None

        self.image_270_x = None
        self.image_270_y = None
        self.image_270_weight = None

        self.dist_to_prev = None
        self.dist_to_next = None

    def compute_all(self):
        self.set_coordinates(0, *compute(self.image_0))
        self.set_coordinates(90, *compute(self.image_90))
        self.set_coordinates(180, *compute(self.image_180))
        self.set_coordinates(270, *compute(self.image_270))

    def set_coordinates(self, angle, x, y, weight):
        setattr(self, f"image_{angle}_x", x)
        setattr(self, f"image_{angle}_y", y)
        setattr(self, f"image_{angle}_weight", weight)

    def adjust_to_bounds(self, min_x, min_y):
        for angle in [0, 90, 180, 270]:
            if getattr(self, f"image_{angle}_x") is not None:
                x = getattr(self, f"image_{angle}_x")
                y = getattr(self, f"image_{angle}_y")

                x = x - min_x
                y = y - min_y

                self.set_coordinates(angle, x, y, getattr(self, f"image_{angle}_weight"))

    def flip_opposites(self, min_x, max_x):
        for angle in [180, 270]:
            if getattr(self, f"image_{angle}_x") is not None:
                x = getattr(self, f"image_{angle}_x")
                y = getattr(self, f"image_{angle}_y")

                x = -x + max_x

                self.set_coordinates(angle, x, y, getattr(self, f"image_{angle}_weight"))

    def compute_3d_estimate(self, angle_1, angle_2):
        x_1 = getattr(self, f"image_{angle_1}_x")
        y_1 = getattr(self, f"image_{angle_1}_y")

        x_2 = getattr(self, f"image_{angle_2}_x")
        y_2 = getattr(self, f"image_{angle_2}_y")

        if x_1 is None or y_1 is None or x_2 is None or y_2 is None:
            return None, None, None

        # When seeing the point from it's side (angle_2), the x position is the depth (z) and the y position is the height
        x = x_1
        y = (y_1 + y_2) / 2
        z = x_2

        return x, y, z

    def compute_3d(self):
        estimate_1 = self.compute_3d_estimate(0, 90)
        estimate_2 = self.compute_3d_estimate(180, 270)

        if estimate_1[0] is None or estimate_1[1] is None or estimate_1[2] is None:
            return estimate_2

        if estimate_2[0] is None or estimate_2[1] is None or estimate_2[2] is None:
            return estimate_1

        if estimate_1[0] is None or estimate_1[1] is None or estimate_1[2] is None and estimate_2[0] is None or \
                estimate_2[1] is None or estimate_2[2] is None:
            return None, None, None

        x = (estimate_1[0] + estimate_2[0]) / 2
        y = (estimate_1[1] + estimate_2[1]) / 2
        z = (estimate_1[2] + estimate_2[2]) / 2

        return x, y, z

    def set_3d(self):
        x, y, z = self.compute_3d()
        self.x = x
        self.y = y
        self.z = z
