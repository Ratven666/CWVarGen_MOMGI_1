class GnssPoint:
    def __init__(self, x, y, z, name, point_type):
        """
        Инициализация объекта GnssPoint.

        :param x: Координата x (например, широта)
        :param y: Координата y (например, долгота)
        :param z: Координата z (например, высота)
        :param name: Название точки
        :param point_type: Тип точки ('base' или 'rover')
        """
        self.x = x
        self.y = y
        self.z = z
        self.name = name
        self.point_type = point_type
        self.mse = None
        self.measure_data = {}

    def __iter__(self):
        return iter(self.measure_data.items())

    def __str__(self):
        """
        Возвращает строковое представление объекта.
        """
        return f"GnssPoint(name={self.name}, type={self.point_type}, x={self.x:.3f}, y={self.y:.3f}, z={self.z:.3f})"

    def __repr__(self):
        """
        Возвращает строковое представление объекта для отладки.
        """
        return self.__str__()

    def is_base(self):
        """
        Проверяет, является ли точка базовой.

        :return: True, если точка базовая, иначе False
        """
        return self.point_type == 'base'

    def is_rover(self):
        """
        Проверяет, является ли точка ровером.

        :return: True, если точка ровер, иначе False
        """
        return self.point_type == 'rover'


if __name__ == "__main__":
    # Пример использования класса
    base_point = GnssPoint(40.7128, -74.0060, 10.0, "Base Station", "base")
    rover_point = GnssPoint(40.7130, -74.0062, 12.0, "Rover 1", "rover")

    print(base_point)
    print(rover_point)

    print(f"Is base_point a base station? {base_point.is_base()}")
    print(f"Is rover_point a rover? {rover_point.is_rover()}")