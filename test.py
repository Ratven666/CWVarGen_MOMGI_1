import matplotlib.pyplot as plt
import numpy as np

# Создаем массив чисел
numbers = np.linspace(0, 1, 3)

# Выбираем цветовую карту (например, 'viridis')
cmap = plt.get_cmap('Set1')

# Получаем цвета для каждого числа
colors = cmap(numbers)

print(colors)
# Выводим цвета
for number, color in zip(numbers, colors):
    print(f"Число: {number}, Цвет: {color}")

# Пример использования цветов для рисования графика
plt.scatter(numbers, np.zeros_like(numbers), c=colors, s=100)
plt.colorbar()
plt.show()