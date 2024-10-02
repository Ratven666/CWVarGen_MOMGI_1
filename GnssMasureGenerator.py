import datetime
import random
from copy import deepcopy

from GnssNet import GnssNet


class GnssMeasureGenerator:

    def __init__(self, gnss_net: GnssNet, d_time=15, num_of_measure=100,
                 gnss_displacement=15, month=None, day=None, random_seed=None):
        self.random_seed = random_seed
        self.gnss_net = gnss_net
        self.d_time = datetime.timedelta(seconds=d_time)
        self.num_of_measure = num_of_measure
        self.gnss_displacement = gnss_displacement
        self.month = month
        self.day = day
        if random_seed is not None:
            random.seed(random_seed)
        self.start_time, self.end_time = self.init_times_border()
        self.total_displacement = self.get_total_displacement()
        self.init_gnss_point_measure_data()

    def init_times_border(self):
        current_time = datetime.datetime.now()

        if self.month is None:
            self.month = random.randint(1, current_time.month - 1)
        if self.day is None:
            self.day = random.randint(1, 28)

        start_time = datetime.datetime(current_time.year, self.month, self.day,
                                       random.randint(8, 20),
                                       random.randint(0, 59),
                                       random.randint(0, 59))
        end_time = start_time + self.num_of_measure * self.d_time
        return start_time, end_time

    def get_total_displacement(self):
        def get_disp():
            return {"x": round(random.random() * self.gnss_displacement - self.gnss_displacement / 2, 3),
                    "y": round(random.random() * self.gnss_displacement - self.gnss_displacement / 2, 3),
                    "z": round(random.random() * self.gnss_displacement - self.gnss_displacement / 2, 3),
                    }

        total_displacement = {
            self.start_time + i * self.d_time: get_disp() for i in range(self.num_of_measure)
        }
        return total_displacement

    def init_custom_point_error(self):
        farthest_point = self.gnss_net.find_farthest_point()

        def get_norm_value(count=12):
            norm_val = sum([random.random() for _ in range(count)]) - count / 2
            return norm_val

        for point in self.gnss_net:
            distance = ((point.x - farthest_point.x) ** 2 + (point.y - farthest_point.y) ** 2) ** 0.5
            vector_mse = (self.gnss_net.accuracy["a"] + self.gnss_net.accuracy["b"] * distance / 1000) / 1000
            for time, measure in point:
                measure["x"] += get_norm_value() * vector_mse
                measure["y"] += get_norm_value() * vector_mse
                measure["z"] += get_norm_value() * vector_mse * 10

    def init_gnss_point_measure_data(self):
        for point in self.gnss_net:
            point.measure_data = deepcopy(self.total_displacement)
            for time, measure in point:
                measure["x"] += point.x
                measure["y"] += point.y
                measure["z"] += point.z
        self.init_custom_point_error()
        self.crop_measure_from_time()

    def crop_measure_from_time(self, crop_perc=0.10):
        for point in self.gnss_net:
            start_time = self.start_time + random.randint(0, int(crop_perc * self.num_of_measure)) * self.d_time
            end_time = self.end_time - random.randint(0, int(crop_perc * self.num_of_measure)) * self.d_time
            point.measure_data = {k: v for k, v in point.measure_data.items() if start_time <= k <= end_time}


if __name__ == "__main__":
    from GnssNetGenerator import GnssNetGenerator

    gnss_net = GnssNetGenerator(random_seed=42, num_points=5).create_gnss_net()

    gmg = GnssMeasureGenerator(gnss_net, random_seed=42, num_of_measure=100)

    gnss_net.plot_net()
    # print(gmg.start_time, gmg.end_time)
    #
    # print(gmg.total_displacement)
    # #
    # for point in gnss_net:
    #     print(point)
    #
    for point in gnss_net:
        for measure in point:
            print(measure)
        print("#" * 100)