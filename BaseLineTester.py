import datetime
import math
import os
from copy import deepcopy

import numpy as np
import pandas as pd
from tabulate import tabulate

from CONFIG import BASE_PATH, NUM_OF_SERIES, NUM_POINTS, COUNT_OF_BASE_POINTS, MIN_DISTANCE, XY_LIMITS, Z_LIMITS, \
    NUM_OF_MEASURES, D_TIME, GNSS_DISPLACEMENT, PASS_POINT_PROB, BASE_LINE_TOLERANCE
from VariantGenerator import VariantGenerator


class BaseLineTester:

    def __init__(self, student_name, tolerance=BASE_LINE_TOLERANCE, num_of_series=NUM_OF_SERIES, num_points=NUM_POINTS,
                 count_of_base_point=COUNT_OF_BASE_POINTS,
                 min_distance=MIN_DISTANCE,
                 xy_limits=XY_LIMITS,
                 z_limit=Z_LIMITS,
                 num_of_measure=NUM_OF_MEASURES,
                 d_time=D_TIME,
                 gnss_displacement=GNSS_DISPLACEMENT,
                 pass_point_prob=PASS_POINT_PROB):
        self.student_name = student_name
        self.tolerance = tolerance
        self.group = None
        self.vg = VariantGenerator(student_name, num_of_series=num_of_series, num_points=num_points,
                                   count_of_base_point=count_of_base_point,
                                   min_distance=min_distance,
                                   xy_limits=xy_limits,
                                   z_limit=z_limit,
                                   num_of_measure=num_of_measure,
                                   d_time=d_time,
                                   gnss_displacement=gnss_displacement,
                                   pass_point_prob=pass_point_prob)
        self.eq_net = None
        self.vectors_list = None
        self.vectors_df = None

    @classmethod
    def check_base_lines_for_students_group(cls,
                                            students_file,
                                            students_file_with_good_vectors,
                                            base_path=BASE_PATH,
                                            tolerance=BASE_LINE_TOLERANCE,
                                            num_of_series=NUM_OF_SERIES, num_points=NUM_POINTS,
                                            count_of_base_point=COUNT_OF_BASE_POINTS,
                                            min_distance=MIN_DISTANCE,
                                            xy_limits=XY_LIMITS,
                                            z_limit=Z_LIMITS,
                                            num_of_measure=NUM_OF_MEASURES,
                                            d_time=D_TIME,
                                            gnss_displacement=GNSS_DISPLACEMENT,
                                            pass_point_prob=PASS_POINT_PROB
                                            ):
        try:
            with open(students_file_with_good_vectors, "rt", encoding="UTF-8") as sfwgv:
                good_vectors_student = sfwgv.readlines()
        except FileNotFoundError:
            with open(students_file_with_good_vectors, "w", encoding="UTF-8") as sfwgv:
                pass
            good_vectors_student = []
        with open(students_file, "rt", encoding="UTF-8") as s_file:
            for student_line in s_file:
                if student_line in good_vectors_student:
                    print(student_line)
                    student, group = student_line.strip().split(";")
                    blt = cls(student_name=student, num_of_series=num_of_series, num_points=num_points,
                              tolerance=tolerance,
                              count_of_base_point=count_of_base_point,
                              min_distance=min_distance,
                              xy_limits=xy_limits,
                              z_limit=z_limit,
                              num_of_measure=num_of_measure,
                              d_time=d_time,
                              gnss_displacement=gnss_displacement,
                              pass_point_prob=pass_point_prob)
                    blt.create_base_lines_file_structures(
                        students_file_with_good_vectors=students_file_with_good_vectors,
                        base_path=base_path)
                    if blt._is_student_put_bl_file_in_dr(base_path=base_path,
                                                         student=student, group=group):
                        blt.group = group
                        blt.check_base_lines(base_path=base_path)
                    else:
                        print(f"Нет файла {student}")


    def _is_student_done_vectors_part(self, students_file_with_good_vectors):
        with open(students_file_with_good_vectors, "rt", encoding="UTF-8") as file:
            for students_line in file:
                student, group = students_line.strip().split(";")
                if student == self.student_name:
                    return student, group

    def create_base_lines_file_structures(self, base_path,
                                          students_file_with_good_vectors,
                                          ):
        result = self._is_student_done_vectors_part(students_file_with_good_vectors)
        if result is not None:
            student, group = result
        else:
            return
        path_0 = os.path.join(base_path, f"ММОМГИ_КР_{datetime.datetime.now().year}",
                              "Базовые линии", "Шаблоны таблиц", str(group), str(student))
        path_1 = os.path.join(base_path, f"ММОМГИ_КР_{datetime.datetime.now().year}",
                              "Базовые линии", "Заполненные шаблоны")
        os.makedirs(path_0, exist_ok=True)
        os.makedirs(path_1, exist_ok=True)
        self._create_blank_vectors_excel_table(str(path_0), student=student,
                                               base_path=base_path, students_group=group)
        return student, group

    def _is_student_put_bl_file_in_dr(self, base_path, student, group):
        file_path = os.path.join(base_path, f"ММОМГИ_КР_{datetime.datetime.now().year}",
                                 "Базовые линии", "Заполненные шаблоны",
                                  f"Base_lines_{group}_{student}.xlsx")
        return os.path.isfile(file_path)

    def _init_vectors_list(self, base_path, students_group):
        if self.eq_net is None:
            self._get_eq_net(base_path=base_path, students_group=students_group)
        self.vectors_list = deepcopy(self.eq_net.gnss_vectors)
        return self.vectors_list

    def _init_vectors_df(self, base_path, students_group):
        if self.vectors_list is None:
            self._init_vectors_list(base_path, students_group)
        indexes = []
        data = {"slope_distance": [],
                "azimuth": [],
                "zenith": [],
                "mse_s_dist": [],
                "mse_azimuth": [],
                "mse_zenith": [],
                }
        for vector in self.vectors_list:
            indexes.append(f"{vector.point_0.name}-{vector.point_1.name}")
            data["slope_distance"].append(vector.s_dist)
            data["azimuth"].append(math.degrees(vector.azimuth)
                                   if
                                   vector.azimuth > 0
                                   else math.degrees(vector.azimuth) + 360)
            data["zenith"].append(math.degrees(vector.zenith))
            data["mse_s_dist"].append(vector.mse_s_dist)
            data["mse_azimuth"].append(math.degrees(vector.mse_azimuth) * 3600)
            data["mse_zenith"].append(math.degrees(vector.mse_zenith) * 3600)
        df = pd.DataFrame(data=data, index=indexes)
        self.vectors_df = df
        return df

    def _create_blank_vectors_df(self, base_path=BASE_PATH, students_group=""):
        if self.vectors_df is None:
            self._init_vectors_df(base_path, students_group)
        blank_df = deepcopy(self.vectors_df)
        blank_df = blank_df.applymap(lambda x: np.nan)
        return blank_df

    def _create_blank_vectors_excel_table(self, path, student,
                                          base_path, students_group=""):
        blank_df = self._create_blank_vectors_df(base_path=base_path, students_group=students_group)
        path = os.path.join(path, f"Base_lines_{students_group}_{student}.xlsx")
        blank_df.to_excel(path, sheet_name='Лист1', index=True)

    def check_base_lines(self, base_path, tolerance=1e-5):
        diff_df = self._get_diff_df(base_path=base_path)
        check_df = self._check_diff_df_with_tolerance(diff_df)
        self._save_check_result(check_df)

    def _get_diff_df(self, base_path):
        correct_vectors_df = deepcopy(self.vectors_df)
        file_path = os.path.join(base_path, f"ММОМГИ_КР_{datetime.datetime.now().year}",
                                 "Базовые линии", "Заполненные шаблоны",
                                 f"Base_lines_{self.group}_{self.student_name}.xlsx")
        student_vector_df = pd.read_excel(file_path, index_col=0)
        df_diff = correct_vectors_df - student_vector_df
        return df_diff

    def _check_diff_df_with_tolerance(self, diff_df):
        def is_less_than(value, tolerance):
            if pd.isna(value):
                return np.nan
            return abs(value) < tolerance

        # Применение функции к каждому элементу датафрейма
        df_check = diff_df.applymap(lambda x: is_less_than(x, self.tolerance))
        return df_check

    def _save_check_result(self, check_df):
        dt = datetime.datetime.now()
        dt_rounded = dt.replace(microsecond=0)
        dir_path = os.path.join("Результаты проверки", "Проверка_базовых_линий")
        os.makedirs(dir_path, exist_ok=True)
        path = os.path.join(dir_path,
                            f"{str(dt_rounded)}_Проверка_базовых_линий_"
                            f"{self.group}_{self.student_name}.txt")
        with open(path, "w") as file:
            tab = tabulate(check_df, headers='keys', tablefmt='pretty')
            print(self.student_name)
            print(tab)
            file.write(tab)


    def _get_eq_net(self, base_path, students_group):
        eq_net = self.vg.solve_variant(base_path=base_path, students_group=students_group)
        self.eq_net = eq_net
        return eq_net


if __name__ == "__main__":
    # name = "Савина Анастасия Викторовна"
    # 
    # blt = BaseLineTester(name)
    # 
    # blt.create_base_lines_file_structures(students_file_with_good_vectors="Good_Vectors_ГГ-21.csv",
    #                                       base_path=r"/Users/mikhail_vystrchil/Downloads")
    # 
    BaseLineTester.check_base_lines_for_students_group(students_file="ГГ-21.csv",
                                                       students_file_with_good_vectors="Good_Vectors_ГГ-21.csv",
                                                       base_path=r"/Users/mikhail_vystrchil/Downloads")
