import math

import numpy as np
import pandas as pd
from tabulate import tabulate

from BaseLineTester import BaseLineTester
from VariantGenerator import VariantGenerator
from VectorTester import VectorTester

if __name__ == "__main__":
    name = "Выстрчил Михаил Георгиевич"

    vg = VariantGenerator(name, num_points=5, count_of_base_point=2)
    # vg.save_variant(students_group="method", create_blank_vectors_json=True)
    eq_net = vg.solve_variant(students_group="method")


    # print(eq_net._get_base_coord_ds())
    # for vector in eq_net.gnss_vectors:
    #     print(vector)
    # print(vg.eq_net.result_df)

    # print(tabulate(vg.eq_net._get_a_coefficients_df(), headers='keys', tablefmt='pretty'))
    # print(tabulate(vg.eq_net._get_a_coefficients_df().round(5), headers='keys', tablefmt='pretty'))
    # print(tabulate(vg.eq_net.get_p_coefficients_df(), headers='keys', tablefmt='pretty'))
    # print(vg.eq_net._get_l_ds())
    # print(tabulate(vg.eq_net.get_p_coefficients_df().applymap(lambda x: np.format_float_scientific(x, precision=3, exp_digits=1)), headers='keys', tablefmt='pretty'))

    # eq_net.plot_eq_net()

    a = eq_net._get_a_coefficients_df()
    point_idx = a.columns
    a = a.to_numpy()
    p = eq_net.get_p_coefficients_df().to_numpy()
    l = eq_net._get_l_ds().to_numpy()
    n = a.T @ p @ a

    atpl = a.T @ p @ l
    q = pd.DataFrame(np.linalg.inv(n), index=point_idx, columns=point_idx)
    mu = eq_net.get_mu()
    k = (mu ** 2) * q
    # print(pd.Series(atpl, index=point_idx))
    # print(tabulate(pd.DataFrame(n, index=point_idx, columns=point_idx).round(3), headers='keys', tablefmt='pretty'))
    # print(tabulate(q.round(10), headers='keys', tablefmt='pretty'))
    print(tabulate(k.round(10), headers='keys', tablefmt='pretty'))
    # print(q["NJYN_x"].loc["NJYN_x"])
    # WLTU_y = mu * q["NJYN_x"].loc["NJYN_x"] ** 0.5
    # print(WLTU_y)
    theta = (2 * k["WLTU_x"].loc["WLTU_y"]) / (k["WLTU_x"].loc["WLTU_x"] - k["WLTU_y"].loc["WLTU_y"])
    q_ = ((k["WLTU_x"].loc["WLTU_x"] - k["WLTU_y"].loc["WLTU_y"]) ** 2 + 4 * k["WLTU_x"].loc["WLTU_y"] ** 2) ** 0.5
    a_ = ((k["WLTU_x"].loc["WLTU_x"] + k["WLTU_y"].loc["WLTU_y"] - q_) / 2) ** 0.5
    print(a_)
    # print(theta)
    # print(math.atan(theta) / 2)
    # print(math.degrees(math.atan(theta) / 2))
    print(q_)

    # print(eq_net.get_v_ds())

    # print(eq_net.get_mu())
    #
    print(eq_net.result_df)

    students_file = "method.csv"
    students_file_with_good_vectors = "good_method.csv"
    base_path = r""

    # VectorTester.check_vectors_for_students_group(students_file=students_file,
    #                                               students_file_with_good_vectors=students_file_with_good_vectors,
    #                                               base_path=base_path,
    #                                               num_points=5, count_of_base_point=2)
    # BaseLineTester.check_base_lines_for_students_group(students_file=students_file,
    #                                                    students_file_with_good_vectors=students_file_with_good_vectors,
    #                                                    base_path=base_path,
    #                                                    num_points=5, count_of_base_point=2)

    # vg.plot()
