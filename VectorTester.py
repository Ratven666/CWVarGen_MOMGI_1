import json
import os
import datetime
from copy import deepcopy

import pandas as pd
from tabulate import tabulate

from CONFIG import BASE_PATH, NUM_POINTS
from EqualisedNetwork import EqualisedNetwork
from GnssNet import GnssNet, PointNameException
from GnssVector import GnssVector
from VariantGenerator import VariantGenerator


class VectorTester:

    _results = {}

    def __init__(self, student_name):
        self.student_name = student_name
        self.vg = VariantGenerator(student_name)
        self.vectors_net = []

    @classmethod
    def check_vectors_for_students_group(cls,
                                         students_file,
                                         students_file_with_good_vectors,
                                         base_path=BASE_PATH,
                                         ):
        result = {"student": [],
                  "group": [],
                  "result": []}
        students_file_with_good_vectors_list = []
        try:
            with open(students_file_with_good_vectors, "rt", encoding="UTF-8") as sfwgv:
                good_vectors_student = sfwgv.readlines()
        except FileNotFoundError:
            with open(students_file_with_good_vectors, "w", encoding="UTF-8") as sfwgv:
                pass
            good_vectors_student = []
        with open(students_file, "rt", encoding="UTF-8") as s_file:
            for student_line in s_file:
                student, group = student_line.strip().split(";")
                if student_line in good_vectors_student:
                    students_file_with_good_vectors_list.append(student_line)
                    student_result = "OK"
                else:
                    student_result = cls(student).check_vectors(base_path=base_path, students_group=group)
                    if student_result == "OK":
                        students_file_with_good_vectors_list.append(student_line)
                result["student"].append(student)
                result["group"].append(group)
                result["result"].append(student_result)
        with open(students_file_with_good_vectors, "w", encoding="UTF-8") as sfwgv:
            for student_line in students_file_with_good_vectors_list:
                sfwgv.write(student_line)

        os.makedirs(os.path.join("Результаты проверки"), exist_ok=True)
        path = os.path.join("Результаты проверки", f"Проверка_векторов_{str(datetime.datetime.now())}.txt")

        with open(path, "w") as file:
            df = pd.DataFrame(result)
            tab = tabulate(df, headers='keys', tablefmt='pretty')
            print(tab)
            file.write(tab)

    def check_vectors(self, base_path=BASE_PATH, students_group=""):
        print(self.student_name)
        try:
            vectors_dict = self._init_vectors_dict(base_path=base_path, students_group=students_group)
        except FileNotFoundError:
            result = "Нет файла c требуемым именем!"
            return result
        except json.decoder.JSONDecodeError:
            result = "Сломан шаблон файла векторов (изменена кодировка с UTF-8!)"
            return result
        if self._is_blank_vectors_dict(vectors_dict):
            result = "Файл векторов не заполнен!"
            return result
        bad_points_name = self._get_bad_points_names(vectors_dict)
        if len(bad_points_name) > 0:
            result = f"Точки c неверными названиями! {bad_points_name}"
            return result
        try:
            self._init_vectors_nets(vectors_dict)
        except PointNameException as e:
            result = f"Проблема с векторами"
            return result
        answer = self._check_vectors_doubler_between_series()
        if answer != "":
            result = answer
            return result
        answer = self._check_double_base_points_in_vectors()
        if answer != "":
            result = answer
            return result
        answer = self._check_vectors_nets_graf()
        if answer != "":
            result = answer
            return result
        answer = self._check_nets_eq_solution(base_path=base_path, students_group=students_group)
        if answer != "":
            result = answer
            return result
        return "OK"

    def _init_vectors_dict(self, base_path, students_group):
        vector_path = os.path.join(base_path, f"ММОМГИ_КР_{datetime.datetime.now().year}", students_group,
                                   "Векторы", self.student_name, f"Vectors_{self.student_name}.json")
        with open(vector_path, 'r', encoding='utf-8') as file:
            vectors_dict = json.load(file)
        return vectors_dict

    def _is_blank_vectors_dict(self, vector_dict):
        blank_vectors_dict = {}
        for series in range(self.vg.num_of_series):
            key = str(series + 1)
            blank_vectors = [["####", "####"] for _ in range(NUM_POINTS - 1)]
            blank_vectors_dict[key] = blank_vectors
        return blank_vectors_dict == vector_dict

    def _get_bad_points_names(self, vectors_dict: dict):
        bad_points_name = []
        for vectors in vectors_dict.values():
            for vector in vectors:
                try:
                    v = GnssVector(self.vg.base_gnss_net, point_0_name=vector[0],
                                   point_1_name=vector[1], is_measured_vector=False)
                except PointNameException as e:
                    bad_points_name.append(e.point_name)
        bad_points_name = list(set(bad_points_name))
        return bad_points_name

    def _init_vectors_nets(self, vectors_dict):
        for series, vectors in vectors_dict.items():
            series = int(series)
            color = "r" if series == 1 else "b"
            vectors_net = []
            for vector in vectors:
                v = GnssVector(self.vg.base_gnss_net, point_0_name=vector[0],
                               point_1_name=vector[1], color=color, is_measured_vector=True)
                vectors_net.append(v)
            self.vectors_net.append(vectors_net)

    def _check_vectors_doubler_between_series(self):
        res_str = ""
        d_vectors = []
        for vector in self.vectors_net[0]:
            if vector in self.vectors_net[1]:
                d_vectors.append(vector)
        d_vectors = list(set(d_vectors))
        for vector in d_vectors:
            res_str += f"Между сериями повторяется вектор: {repr(vector)}\n"
        return res_str

    def _check_double_base_points_in_vectors(self):
        vn_nets = deepcopy(self.vectors_net)
        vn_nets= [vector for vector_net in vn_nets for vector in vector_net]
        bad_vectors = []
        for vector in vn_nets:
            if vector.point_0.is_base() and vector.point_1.is_base():
                bad_vectors.append(vector)
        res_str = ""
        for vector in bad_vectors:
            res_str += f"Вектор {repr(vector)} опирается на две исходные точки!\n"
        return res_str

    def _check_vectors_nets_graf(self):
        vn_nets = deepcopy(self.vectors_net)
        # vn_nets.append([vector for vector_net in vn_nets for vector in vector_net])
        answers = []
        for v_net in vn_nets:
            eq = EqualisedNetwork()
            for v in v_net:
                eq.add_gnss_vector(v)
            eq.plot_eq_net()
            answers.append(input("It`s a correct Net? (Y/N): "))
        res_str = ""
        for idx, answer in enumerate(answers):
            if answer.upper() == "N":
                res_str += f"Неправильная сеть №{idx + 1}\n"
            elif answer.upper() == "Y":
                continue
            else:
                print(f"Некорректный ответ на сеть №{idx + 1}\n")
                res_str = self._check_vectors_nets_graf()
        return res_str

    def _check_nets_eq_solution(self, base_path, students_group):
        self.vg.solve_variant(base_path=base_path, students_group=students_group)
        eq = deepcopy(self.vg.eq_net.result_df).round(3)
        print(tabulate(eq, headers='keys', tablefmt='pretty'))
        answer = input("It`s normal solution? (Y/N): ")
        res_str = ""
        if answer.upper() == "N":
            res_str += "Сеть не уравнивается!\n"
        elif answer.upper() == "Y":
            return res_str
        else:
            res_str = self._check_nets_eq_solution(base_path, students_group)
        return res_str




if __name__ == "__main__":
    # name = "Савина Анастасия Викторовна"
    # name = "Джавадова Шакира Ташаккуровна"

    # vt = VectorTester(name)
    #
    #
    # vt.check_vectors(base_path=r"/Users/mikhail_vystrchil/Downloads", students_group="ГГ-21-1")

    VectorTester.check_vectors_for_students_group(students_file="ГГ-21.csv",
                                                  students_file_with_good_vectors="Good_Vectors_ГГ-21.csv",
                                                  base_path=r"/Users/mikhail_vystrchil/Downloads")
    # vt.plot_vectors()

    # vt.get_result()
