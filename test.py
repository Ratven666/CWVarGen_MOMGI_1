import matplotlib.pyplot as plt
import numpy as np

# Начальные точки векторов
x0 = [0, 1, 2]
y0 = [0, 1, 2]

# Компоненты векторов
u = [1, -1, 0.5]
v = [2, 0.5, -1]

# Создаем график
plt.figure()

# Рисуем векторы
plt.quiver(1, 0, 1, 1, angles='xy', scale_units='xy', scale=1)

# Устанавливаем границы осей
plt.xlim(-1, 3)
plt.ylim(-1, 3)

# Добавляем сетку
plt.grid()

# Показываем график
plt.show()