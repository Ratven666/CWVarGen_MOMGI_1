import math
import os
from copy import deepcopy

import numpy as np
import pandas as pd

from CONFIG import BASE_PATH
from VariantGenerator import VariantGenerator


class BaseLineTester:

    def __init__(self, student_name):
        self.student_name = student_name
        self.vg = VariantGenerator(student_name)
        self.eq_net = None
        self.vectors_list = None
        self.vectors_df = None

    @classmethod
    def check_base_lines_for_students_group(cls,
                                         students_file,
                                         students_file_with_good_vectors,
                                         base_path=BASE_PATH,
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
                    blt = cls(student_name=student)
                    blt.create_base_lines_file_structures(students_file_with_good_vectors=students_file_with_good_vectors,
                                                          base_path=base_path)

    def _is_student_done_vectors_part(self, students_file_with_good_vectors):
        with open(students_file_with_good_vectors, "rt", encoding="UTF-8") as file:
            for students_line in file:
                student, group = students_line.strip().split(";")
                if student == self.student_name:
                    return student, group


    def create_base_lines_file_structures(self, students_file_with_good_vectors="Good_Vectors_ГГ-21.csv",
                                          base_path=BASE_PATH):
        result = self._is_student_done_vectors_part(students_file_with_good_vectors)
        if result is not None:
            student, group = result
        else:
            return
        path_0 = os.path.join("Базовые линии", "Шаблоны таблиц", str(group), str(student))
        path_1 = os.path.join("Базовые линии", "Заполненные шаблоны")
        os.makedirs(path_0, exist_ok=True)
        os.makedirs(path_1, exist_ok=True)
        self._create_blank_vectors_excel_table(str(path_0), student=student,
                                    base_path=base_path, students_group=group)
        return student, group

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
        blank_df.to_excel('output.xlsx', sheet_name='Лист1', index=True)
        return blank_df

    def _create_blank_vectors_excel_table(self, path, student,
                                          base_path=BASE_PATH, students_group=""):
        blank_df = self._create_blank_vectors_df(base_path=base_path, students_group=students_group)
        path = os.path.join(path, f"Base_lines_{students_group}_{student}.xlsx")
        blank_df.to_excel(path, sheet_name='Лист1', index=True)

    def check_base_lines(self, base_path=BASE_PATH, students_group=""):
        pass

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


