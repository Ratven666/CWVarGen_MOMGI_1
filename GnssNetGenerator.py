import math
import random
import string

from GnssNet import GnssNet
from GnssPoint import GnssPoint


class GnssNetGenerator:

    def __init__(self, num_points=15, count_of_base_point=2, min_distance=1500,
                 xy_limits=20_000, z_limit=500, random_seed=None):
        self.random_seed = random_seed
        if random_seed is not None:
            random.seed(random_seed)
        self.num_points = num_points
        self.count_of_base_point = count_of_base_point
        self.min_distance = min_distance
        self.x_range, self.y_range, self.z_range = self._gen_ranges(xy_limits, z_limit)
        self.points = self.generate_points_grid()
        self.base_points = self.find_most_distant_points()


    @staticmethod
    def _gen_ranges(xy_limits, z_limit):
        x0, y0 = [random.randint(a=40_000, b =80_000) for _ in range(2)]
        z0 = random.randint(100, 500)
        return (x0, x0 + xy_limits), (y0, y0 + xy_limits), (z0, z0 + z_limit)

    def generate_points_grid(self):
        """
        Генерирует num_points точек в заданном диапазоне x_range и y_range,
        которые находятся друг от друга на расстоянии не менее min_distance,
        используя сетку для более равномерного распределения и исключая
        появление точек в смежных ячейках, включая диагональные.

        :param num_points: количество точек для генерации
        :param min_distance: минимальное расстояние между точками
        :param x_range: диапазон значений по оси X
        :param y_range: диапазон значений по оси Y
        :param random_seed: начальное значение для генератора случайных чисел
        :return: список сгенерированных точек
        """

        width = self.x_range[1] - self.x_range[0]
        height = self.y_range[1] - self.y_range[0]
        cell_size = self.min_distance / 2 ** 0.5
        cols = int(width / cell_size)
        rows = int(height / cell_size)

        grid = [[None for _ in range(cols)] for _ in range(rows)]
        points = []

        def get_cell(point):
            col = int((point[0] - self.x_range[0]) / cell_size)
            row = int((point[1] - self.y_range[0]) / cell_size)
            return row, col

        def is_valid(point):
            row, col = get_cell(point)
            if row < 0 or row >= rows or col < 0 or col >= cols:
                return False
            if grid[row][col] is not None:
                return False
            for r in range(max(0, row - 1), min(rows, row + 2)):
                for c in range(max(0, col - 1), min(cols, col + 2)):
                    if grid[r][c] is not None and math.dist(point, grid[r][c]) < self.min_distance:
                        return False
            return True

        while len(points) < self.num_points:
            point = (random.uniform(*self.x_range), random.uniform(*self.y_range), random.uniform(*self.z_range))
            if is_valid(point):
                row, col = get_cell(point)
                grid[row][col] = point
                points.append(point)
        return points

    def find_most_distant_points(self):
        """
        Находит n самых удаленных между собой точек.

        :param points: список точек
        :param n: количество точек для выделения
        :return: список n самых удаленных точек
        """

        def min_distance_to_others(point, others):
            return min(math.dist(point, other) for other in others if other != point)

        most_distant_points = []
        remaining_points = self.points[:]

        for _ in range(self.count_of_base_point):
            if not remaining_points:
                break
            point = max(remaining_points, key=lambda p: min_distance_to_others(p, remaining_points))
            most_distant_points.append(point)
            remaining_points.remove(point)

        return most_distant_points

    @staticmethod
    def generate_unique_name():
        """
        Генерирует уникальное имя из четырех заглавных латинских букв.

        :return: уникальное имя
        """
        return ''.join(random.choices(string.ascii_uppercase, k=4))

    def create_gnss_net(self):
        gnss_net = GnssNet()

        for point in self.points:
            gnss_point = GnssPoint(x=round(point[0], 3),
                                   y=round(point[1], 3),
                                   z=round(point[2], 3),
                                   name=self.generate_unique_name(),
                                   point_type= "base" if point in self.base_points else "rover")
            gnss_net.add_point(gnss_point)

        return gnss_net
