from matplotlib import pyplot as plt

from CONFIG import MSE_B, MSE_A
from GnssPoint import GnssPoint


class GnssNet:
    def __init__(self, accuracy=None):
        """
        Инициализация объекта GnssNet.
        """
        if accuracy is None:
            accuracy = {"a": MSE_A, "b": MSE_B}
        self.accuracy = accuracy
        self.points = []

    def add_point(self, point):
        """
        Добавляет точку в сеть.

        :param point: Объект GnssPoint
        """
        if isinstance(point, GnssPoint):
            self.points.append(point)
        else:
            raise ValueError("The point must be an instance of GnssPoint")

    def remove_point(self, point):
        """
        Удаляет точку из сети.

        :param point: Объект GnssPoint
        """
        if point in self.points:
            self.points.remove(point)
        else:
            raise ValueError("The point is not in the network")

    def get_point_by_name(self, point_name: str) -> GnssPoint:
        for point in self:
            if point.name == point_name.upper():
                return point
        raise ValueError(f"Нет точки с таким именем! - {point_name}")

    def get_points(self):
        """
        Возвращает список всех точек в сети.

        :return: Список объектов GnssPoint
        """
        return self.points

    def get_base_points(self):
        """
        Возвращает список всех базовых точек в сети.

        :return: Список объектов GnssPoint
        """
        return [point for point in self.points if point.is_base()]

    def get_rover_points(self):
        """
        Возвращает список всех роверных точек в сети.

        :return: Список объектов GnssPoint
        """
        return [point for point in self.points if point.is_rover()]

    def __str__(self):
        """
        Возвращает строковое представление объекта.
        """
        points_str = "\n".join([str(point) for point in self.points])
        return f"GnssNet with points:\n{points_str}"

    def __repr__(self):
        """
        Возвращает строковое представление объекта для отладки.
        """
        return self.__str__()

    def __iter__(self):
        return iter(self.points)

    def find_farthest_point(self, reference_point=(0, 0)):
        """
        Находит самую крайнюю точку от заданной точки отсчета.

        :param reference_point: Кортеж (x, y) с координатами точки отсчета.
        :return: Объект GnssPoint, самая крайнюю точку.
        """
        if not self.points:
            raise ValueError("The network is empty")

        farthest_point = None
        max_distance = -1

        ref_x, ref_y = reference_point

        for point in self.points:
            distance = ((point.x - ref_x) ** 2 + (point.y - ref_y) ** 2) ** 0.5
            if distance > max_distance:
                max_distance = distance
                farthest_point = point

        return farthest_point

    def plot_net(self):
        """
        Визуализирует сеть в 2D.
        """
        fig, ax = plt.subplots()

        for point in self.points:
            ax.text(x=point.x,
                    y=point.y,
                    s=point.name,
                    )

        base_points = self.get_base_points()
        rover_points = self.get_rover_points()

        base_x = [point.x for point in base_points]
        base_y = [point.y for point in base_points]

        rover_x = [point.x for point in rover_points]
        rover_y = [point.y for point in rover_points]

        ax.scatter(base_x, base_y, c='r', marker='o', label='Base Points')
        ax.scatter(rover_x, rover_y, c='b', marker='^', label='Rover Points')

        ax.set_xlabel('X')
        ax.set_ylabel('Y')

        plt.legend()
        plt.show()
