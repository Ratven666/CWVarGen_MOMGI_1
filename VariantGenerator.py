import hashlib
import json
import os
import random
from copy import deepcopy
import datetime

from CONFIG import NUM_POINTS, COUNT_OF_BASE_POINTS, MIN_DISTANCE, XY_LIMITS, Z_LIMITS, NUM_OF_SERIES, D_TIME, \
    NUM_OF_MEASURES, GNSS_DISPLACEMENT, BASE_PATH, PASS_POINT_PROB
from EqualisedNetwork import EqualisedNetwork
from GnssMasureGenerator import GnssMeasureGenerator
from GnssNetGenerator import GnssNetGenerator
from GnssVector import GnssVector


class VariantGenerator:

    def __init__(self, student_name: str, num_of_series=NUM_OF_SERIES):
        self.student_name = student_name.strip()
        self.num_of_series = num_of_series
        random.seed(self._get_hash())
        self.base_gnss_net = GnssNetGenerator(num_points=NUM_POINTS,
                                              count_of_base_point=COUNT_OF_BASE_POINTS,
                                              min_distance=MIN_DISTANCE,
                                              xy_limits=XY_LIMITS,
                                              z_limit=Z_LIMITS).create_gnss_net()
        self.measured_gnss_nets = []
        self._create_measures()
        self.eq_net = None

    def _get_hash(self):
        hash_ = int(hashlib.sha256(self.student_name.encode("UTF-8")).hexdigest(), 16)
        # hash_ = int(hashlib.sha256(self.name.encode("UTF-8")).hexdigest(), 16) % 10 ** 8
        return hash_

    def _get_start_measure_month_day(self):
        current_time = datetime.datetime.now()
        month = random.randint(1, current_time.month - 1)
        day = random.randint(1, 28 - self.num_of_series)
        return month, day

    def _create_measures(self):
        month, day = self._get_start_measure_month_day()
        for series in range(self.num_of_series):
            gnss_net_copy = deepcopy(self.base_gnss_net)
            gmg = GnssMeasureGenerator(gnss_net_copy,
                                       d_time=D_TIME,
                                       num_of_measure=NUM_OF_MEASURES,
                                       gnss_displacement=GNSS_DISPLACEMENT,
                                       pass_point_prob=PASS_POINT_PROB,
                                       month=month,
                                       day=day)
            self.measured_gnss_nets.append(gnss_net_copy)
            day += 1

    def _create_blank_vectors_json(self, vectors_path):
        blank_vectors_dict = {}
        for series in range(self.num_of_series):
            key = str(series + 1)
            blank_vectors = [["####", "####"] for _ in range(NUM_POINTS - 1)]
            blank_vectors_dict[key] = blank_vectors
        with open(os.path.join(vectors_path, f"Vectors_{self.student_name}.json"), "w") as file:
            file.write(json.dumps(blank_vectors_dict, sort_keys=True, indent=4))

    def save_variant(self, base_path=BASE_PATH, students_group="", create_blank_vectors_json=False):
        variant_path = os.path.join(base_path, f"ММОМГИ_КР_{datetime.datetime.now().year}", students_group,
                                    "Вариант", self.student_name)
        os.makedirs(variant_path, exist_ok=True)
        vectors_path = os.path.join(base_path, f"ММОМГИ_КР_{datetime.datetime.now().year}", students_group,
                                             "Векторы", self.student_name)
        os.makedirs(vectors_path, exist_ok=True)
        if create_blank_vectors_json:
            self._create_blank_vectors_json(vectors_path)
        for idx, net in enumerate(self.measured_gnss_nets):
            series_path = os.path.join(variant_path, f"Серия_{idx + 1}")
            os.makedirs(series_path, exist_ok=True)
            for point in net:
                with open(os.path.join(series_path, f"{point.name}.txt"), "a", encoding="UTF-8") as file:
                    file.write(f"DATE_TIME,X,Y,Z\n")
                for time, measure in point:
                    with open(os.path.join(series_path, f"{point.name}.txt"), "a", encoding="UTF-8") as file:
                        file.write(f"{time},{measure["x"]},{measure["y"]},{measure["z"]}\n")
        with open(os.path.join(variant_path, "Base_points.txt"), "a", encoding="UTF-8") as file:
            file.write(f"Point_name,X,Y,Z\n")
            for point in self.base_gnss_net:
                if point.is_base():
                    file.write(f"{point.name},{point.x},{point.y},{point.z}\n")

    def solve_variant(self, base_path=BASE_PATH, students_group=""):
        vector_path = os.path.join(base_path, f"ММОМГИ_КР_{datetime.datetime.now().year}", students_group,
                                   "Векторы", self.student_name, f"Vectors_{self.student_name}.json")
        with open(vector_path, 'r', encoding='utf-8') as file:
            vectors_dict = json.load(file)

        self.eq_net = EqualisedNetwork()
        for series, vectors in vectors_dict.items():
            series = int(series)
            color = "r" if series == 1 else "b"
            for vector in vectors:
                v = GnssVector(self.measured_gnss_nets[series - 1], point_0_name=vector[0],
                               point_1_name=vector[1], color=color)
                self.eq_net.add_gnss_vector(v)
        self.eq_net.calculate()
        return self.eq_net

    def plot(self):
        if self.eq_net is None:
            self.base_gnss_net.plot_net()
        else:
            self.eq_net.plot_eq_net()


def create_variants_for_students_file(students_file, base_path=BASE_PATH,
                                      create_blank_vectors_json=False,
                                      plot_gnss_net=False):
    with (open(os.path.join(base_path, students_file), "rt", encoding="UTF-8") as file):
        for student in file:
            student_name, student_group = student.strip().split(";")
            vg = VariantGenerator(student_name)
            vg.save_variant(students_group=student_group,
                            create_blank_vectors_json=create_blank_vectors_json)
            print(student_name, student_group)
            if plot_gnss_net:
                vg.plot()

if __name__ == "__main__":
    name = "Выстрчил Михаил Георгиевич"

    vg = VariantGenerator(name)
    vg.solve_variant()
    print(vg.eq_net.result_df)
    # vg.save_variant(create_blank_vectors_json=True)
    # vg.plot()
    # vg.save_variant(students_group="ГГ-21-1", create_blank_vectors_json=True)
    # vg.solve_variant(students_group="ГГ-21-1")

    # print(vg.eq_net.result_df)
    # vg.plot()
    # print(vg.eq_net.gnss_vectors)
    # print(vg._get_hash())
    # vg.plot()

    # create_variants_for_students_file("ГГ-21.csv", create_blank_vectors_json=True, plot_gnss_net=False)


