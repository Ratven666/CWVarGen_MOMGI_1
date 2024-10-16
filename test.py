a = [1, 2, 3]
b = ["q", "w", "e"]

print([item for sublist in [a, b] for item in sublist])