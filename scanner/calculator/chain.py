import os

from matplotlib import pyplot as plt

import main
from scanner import config
from scanner.calculator.point import Point


class Chain:
    def __init__(self, length):
        self.image_x_min = None
        self.image_x_max = None

        self.image_y_min = None
        self.image_y_max = None

        self.points = []

        for i in range(1, length + 1):
            self.points.append(Point(i))

    def compute_points(self):
        for point in self.points:
            point.compute_all()

        self.remove_incorrect_points()
        self.calculate_min_max()

        for point in self.points:
            point.adjust_to_bounds(self.image_x_min, self.image_y_min)
            point.flip_opposites(self.image_x_min, self.image_x_max)

        if main.args.debug:
            self.show_graphs()

        for point in self.points:
            point.set_3d()

        if main.args.debug:
            self.show_3d_graphs()

        self.fix_incorrect_points_3d()

        if main.args.debug:
            self.show_3d_graphs()

        if os.path.exists("coords.txt"):
            os.remove("coords.txt")
        with open("coords.txt", "a") as file:
            for point in self.points:
                file.write(f"[{point.x}, {point.z}, {point.y}] \n")

    def remove_incorrect_points(self):
        for angle in [0, 90, 180, 270]:
            # Get the average distance between points
            distances = []
            for i in range(1, len(self.points)):
                distance_x = getattr(self.points[i], f"image_{angle}_x") - getattr(self.points[i - 1],
                                                                                   f"image_{angle}_x")
                distance_y = getattr(self.points[i], f"image_{angle}_y") - getattr(self.points[i - 1],
                                                                                   f"image_{angle}_y")

                distances.append((distance_x ** 2 + distance_y ** 2) ** 0.5)
            avg_distance = sum(distances) / len(distances)

            # If a point isn't as bright as this, remove it
            # A properly lit LED should be 255, so this is a decent threshold
            assumed_brightness = config.get_config().get('brightness_threshold')

            # Calculate the min and max values for the x and y coordinates
            for point in self.points:
                x = getattr(point, f"image_{angle}_x")
                y = getattr(point, f"image_{angle}_y")
                weight = getattr(point, f"image_{angle}_weight")

                # Find the previous point that wasn't already removed
                previous_not_none = None
                for i in range(point.index - 1, 0, -1):
                    if getattr(self.points[i], f"image_{angle}_x") is not None:
                        previous_not_none = self.points[i]
                        break

                next_not_none = None
                for i in range(point.index + 1, len(self.points)):
                    if getattr(self.points[i], f"image_{angle}_x") is not None:
                        next_not_none = self.points[i]
                        break

                # The first point can't be removed
                if point.index == 1:
                    previous_not_none = point

                if point.index >= len(self.points) - 1:
                    next_not_none = point

                # Get the distance to the previous point
                distance_prev_x = getattr(point, f"image_{angle}_x") - getattr(previous_not_none, f"image_{angle}_x")
                distance_prev_y = getattr(point, f"image_{angle}_y") - getattr(previous_not_none, f"image_{angle}_y")
                distance_prev = (distance_prev_x ** 2 + distance_prev_y ** 2) ** 0.5

                # Get the distance to the next point
                distance_next_x = getattr(point, f"image_{angle}_x") - getattr(next_not_none, f"image_{angle}_x")
                distance_next_y = getattr(point, f"image_{angle}_y") - getattr(next_not_none, f"image_{angle}_y")
                distance_next = (distance_next_x ** 2 + distance_next_y ** 2) ** 0.5

                # If the distance is too far, or the brightness isn't high enough, remove the point
                if distance_prev > (avg_distance * config.get_config().get('confidence')) or distance_next > (avg_distance * config.get_config().get('confidence')) or weight < assumed_brightness:
                    setattr(point, f"image_{angle}_x", None)
                    setattr(point, f"image_{angle}_y", None)
                    setattr(point, f"image_{angle}_weight", None)

    def correct_chain(self, incorrect):
        correcting = []
        for i in range(1, len(self.points)):
            if self.points[i] in incorrect:
                j = 0
                while self.points[i + j] in incorrect:
                    correcting.append(self.points[i + j])
                    j += 1
                break
        previous_correct = self.points[correcting[0].index - 2]
        next_correct = self.points[correcting[-1].index]

        i = 0
        while i < len(correcting):
            correcting[i].x = previous_correct.x + (next_correct.x - previous_correct.x) / (len(correcting) + 1) * (
                    i + 1)
            correcting[i].y = previous_correct.y + (next_correct.y - previous_correct.y) / (len(correcting) + 1) * (
                    i + 1)
            correcting[i].z = previous_correct.z + (next_correct.z - previous_correct.z) / (len(correcting) + 1) * (
                    i + 1)
            i += 1
        for point in correcting:
            incorrect.remove(point)
        return incorrect

    def fix_incorrect_points_3d(self):
        incorrect = []
        for point in self.points:
            if point.x is None:
                incorrect.append(point)
        while incorrect is not None and len(incorrect) > 0:
            incorrect = self.correct_chain(incorrect)

    def calculate_min_max(self):
        for angle in [0, 90, 180, 270]:
            for point in self.points:
                x = getattr(point, f"image_{angle}_x")
                y = getattr(point, f"image_{angle}_y")
                if x is not None and y is not None:
                    if self.image_x_min is None or x < self.image_x_min:
                        self.image_x_min = x

                    if self.image_x_max is None or x > self.image_x_max:
                        self.image_x_max = x

                    if self.image_y_min is None or y < self.image_y_min:
                        self.image_y_min = y

                    if self.image_y_max is None or y > self.image_y_max:
                        self.image_y_max = y

    def show_graphs(self):
        for angle in [0, 90, 180, 270]:
            x = []
            y = []
            for point in self.points:
                if getattr(point, f"image_{angle}_x") is not None:
                    x.append(getattr(point, f"image_{angle}_x"))
                    y.append(getattr(point, f"image_{angle}_y"))

            plt.plot(x, y, 'o')

        plt.show()

    def show_3d_graphs(self):
        x = []
        y = []
        z = []
        for point in self.points:
            if point.x is not None and point.y is not None and point.z is not None:
                x.append(point.x)
                y.append(point.y)
                z.append(point.z)

        print(len(x))
        ax = plt.axes(projection='3d')
        ax.scatter3D(x, y, z, c=z, cmap='Greens')
        plt.show()
