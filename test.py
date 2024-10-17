import pandas as pd


data = {
    'Имя': ['Алексей', 'Мария', 'Иван', 'Ольга'],
    'Возраст': [25, 30, 22, 28],
    'Город': ['Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург']
}

df = pd.DataFrame(data)

print(df)

# Экспорт в Excel с использованием openpyxl
df.to_excel('output.xlsx', sheet_name='Лист1', index=True)

df = pd.read_excel('output.xlsx', index_col=0)
print(df)