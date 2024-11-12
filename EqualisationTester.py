import datetime
import os
from copy import deepcopy

import numpy as np
import pandas as pd
from tabulate import tabulate

from CONFIG import EQUALISATION_TOLERANCE, NUM_OF_SERIES, NUM_POINTS, COUNT_OF_BASE_POINTS, MIN_DISTANCE, XY_LIMITS, \
    Z_LIMITS, NUM_OF_MEASURES, D_TIME, GNSS_DISPLACEMENT, PASS_POINT_PROB
from VariantGenerator import VariantGenerator


class EqualisationTester:

    def __init__(self, student_name, tolerance=EQUALISATION_TOLERANCE, num_of_series=NUM_OF_SERIES, num_points=NUM_POINTS,
                 count_of_base_point=COUNT_OF_BASE_POINTS,
                 min_distance=MIN_DISTANCE,
                 xy_limits=XY_LIMITS,
                 z_limit=Z_LIMITS,
                 num_of_measure=NUM_OF_MEASURES,
                 d_time=D_TIME,
                 gnss_displacement=GNSS_DISPLACEMENT,
                 pass_point_prob=PASS_POINT_PROB):
        self.student_name = student_name
        self.tolerances = tolerance
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

    def _get_eq_net(self, base_path, students_group):
        eq_net = self.vg.solve_variant(base_path=base_path, students_group=students_group)
        self.eq_net = eq_net
        return eq_net

    def _init_equalization_df(self, base_path, students_group):
        self.eq_net = self._get_eq_net(base_path=base_path, students_group=students_group)
        self.equalization_df = self.eq_net.result_df
        return self.equalization_df

    def _save_check_result(self, check_df):
        dt = datetime.datetime.now()
        dt_rounded = dt.replace(microsecond=0)
        dir_path = os.path.join("Результаты проверки", "Проверка_уравнивания_и_оценки_точности")
        os.makedirs(dir_path, exist_ok=True)
        path = os.path.join(dir_path,
                            f"{str(dt_rounded)}_Проверка_уравнивания_"
                            f"{self.group}_{self.student_name}.txt")
        with open(path, "w") as file:
            tab = tabulate(check_df, headers='keys', tablefmt='pretty')
            print(self.student_name)
            print(tab)
            file.write(tab)

    # def _get_diff_df(self, base_path):
    #     correct_vectors_df = deepcopy(self.vectors_df)
    #     file_path = os.path.join(base_path, f"ММОМГИ_КР_{datetime.datetime.now().year}",
    #                              "Базовые линии", "Заполненные шаблоны",
    #                              f"Base_lines_{self.group}_{self.student_name}.xlsx")
    #     student_vector_df = pd.read_excel(file_path, index_col=0)
    #     df_diff = correct_vectors_df - student_vector_df
    #     return df_diff

    def _check_diff_df_with_tolerance(self, diff_df):
        def is_less_than(value, tolerance):
            if pd.isna(value):
                return np.nan
            return abs(value) < tolerance
        df_check = diff_df.apply(lambda col: col.apply(lambda x: is_less_than(x, self.tolerances[col.name])))
        return df_check

    def check_equalization(self, base_path):
        diff_df = self._get_diff_df(base_path=base_path)
        check_df = self._check_diff_df_with_tolerance(diff_df)
        self._save_check_result(check_df)

    # def _create_blank_equalization_df(self, base_path, students_group):
    #     if self.vectors_df is None:
    #         self._init_vectors_df(base_path, students_group)
    #     blank_df = deepcopy(self.vectors_df)
    #     blank_df = blank_df.applymap(lambda x: np.nan)
    #     return blank_df

    def _create_blank_equalization_excel_table(self, path, student,
                                          base_path, students_group=""):
        blank_df = self._create_blank_equalization_df(base_path=base_path, students_group=students_group)
        path = os.path.join(path, f"Base_lines_{students_group}_{student}.xlsx")
        blank_df.to_excel(path, sheet_name='Лист1', index=True)