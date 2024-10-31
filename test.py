import pandas as pd

# Пример DataFrame
data = {
    'A': [1, 2, 3, 4],
    'B': [5, 6, 7, 8],
    'C': [9, 10, 11, 12]
}

diff_df = pd.DataFrame(data)

# Допуски для каждого столбца
tolerances = {
    'A': 2,
    'B': 3,
    'C': 4
}

# Функция для проверки соответствия допуску
def is_less_than(value, tolerance):
    return abs(value) <= tolerance

# Применение функции к каждому столбцу
df_check = diff_df.apply(lambda col: col.apply(lambda x: is_less_than(x, tolerances[col.name])))

print(df_check)