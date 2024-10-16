from VariantGenerator import create_variants_for_students_file
from VectorTester import VectorTester

if __name__ == "__main__":
    # Создание вариантов
    # create_variants_for_students_file("ГГ-21.csv", create_blank_vectors_json=True, plot_gnss_net=False)

    # Проверка векторов
    VectorTester.check_vectors_for_students_group(students_file="ГГ-21.csv",
                                                  students_file_with_good_vectors="Good_Vectors_ГГ-21.csv",
                                                  base_path=r"/Users/mikhail_vystrchil/Downloads")
