import numpy as np

a = np.empty((4, 4, 3), dtype=np.uint8)

for i in range(4):
	a[i,:] = np.array([i, i, i], dtype=np.uint8)
	print("Line ", i, " = ", a[i,:])

a = np.delete(a, 2, 0)
print(a)
