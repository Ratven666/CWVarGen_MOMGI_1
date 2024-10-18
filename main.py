from BaseLineTester import BaseLineTester
from VariantGenerator import create_variants_for_students_file
from VectorTester import VectorTester

def start_checking(students_file="ГГ-21.csv",
                   students_file_with_good_vectors="Good_Vectors_ГГ-21.csv",
                   base_path=r"/Users/mikhail_vystrchil/Downloads"):
    # Проверка векторов
    VectorTester.check_vectors_for_students_group(students_file=students_file,
                                                  students_file_with_good_vectors=students_file_with_good_vectors,
                                                  base_path=base_path)
    BaseLineTester.check_base_lines_for_students_group(students_file=students_file,
                                                  students_file_with_good_vectors=students_file_with_good_vectors,
                                                  base_path=base_path)


if __name__ == "__main__":
    # Создание вариантов
    # create_variants_for_students_file("ГГ-21.csv", create_blank_vectors_json=True, plot_gnss_net=False)

    # Проверка векторов
    start_checking(students_file="ГГ-21.csv",
                   students_file_with_good_vectors="Good_Vectors_ГГ-21.csv",
                   base_path=r"/Users/mikhail_vystrchil/Downloads")
    # VectorTester.check_vectors_for_students_group(students_file="ГГ-21.csv",
    #                                               students_file_with_good_vectors="Good_Vectors_ГГ-21.csv",
    #                                               base_path=r"/Users/mikhail_vystrchil/Downloads")
    # BaseLineTester.check_base_lines_for_students_group(students_file="ГГ-21.csv",
    #                                               students_file_with_good_vectors="Good_Vectors_ГГ-21.csv",
    #                                               base_path=r"/Users/mikhail_vystrchil/Downloads")
