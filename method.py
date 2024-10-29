from BaseLineTester import BaseLineTester
from VariantGenerator import VariantGenerator
from VectorTester import VectorTester

if __name__ == "__main__":
    name = "Выстрчил Михаил Георгиевич"

    vg = VariantGenerator(name, num_points=5, count_of_base_point=2)
    # # vg.save_variant(students_group="method", create_blank_vectors_json=True)
    # eq_net = vg.solve_variant(students_group="method")
    #
    # for vector in eq_net.gnss_vectors:
    #     print(vector)

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

    vg.plot()
