import numpy as np

a = np.empty((4, 4, 3), dtype=np.uint8)

for i in range(4):
	a[i,:] = np.array([i, i, i], dtype=np.uint8)
	print("Line ", i, " = ", a[i,:])

b = np.flip(a, 0)
for i in range(4):
	print("Line ", i, " = ", b[i,:])
