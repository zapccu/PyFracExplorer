import numpy as np

a = np.array([
	[ 2, 2, 2, 1 ],
	[ 2, 2, 2, 1 ],
	[ 2, 2, 2, 1 ],
	[ 2, 2, 2, 1 ]
])

b = np.all(a == a[0])

print("Check if")
print(a)
print("is matching ")
print(a[0])
print(b)
