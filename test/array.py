
import numpy as np

arr = np.array([1, 2, 3])
scale = lambda x: x * 2

a = list(map(scale, arr))

print(a)
