import time
import numpy as np
import matplotlib.pyplot as plt

# Setting parameters (these values can be changed)
x_domain, y_domain = np.linspace(-2, 1, 500), np.linspace(-1.5, 1.5, 500)
bound = 4
max_iterations = 50  # any positive integer value
colormap = "nipy_spectral"  # set to any matplotlib valid colormap

refPoint = complex(-0.5, 0.0)
Z = complex(0.0, 0.0)
refOrbit = np.zeros(500, dtype=complex)

# Calculate reference orbit
for i in range(500):
	refOrbit[i] = Z
	Z = Z * Z + refPoint
	nZ = Z.real * Z.real + Z.imag * Z.imag

	if nZ > 4.0:
		break

refOrbit.resize(i)
refOrbit2 = refOrbit * 2.0
maxRefIter = i

func = lambda z, p, c: z**p + c

# Computing 2D array to represent the Mandelbrot set
iteration_array = []
st = time.time()
for y in y_domain:
    row = []
    for x in x_domain:
        Z = 0
        c = complex(x, y)
        
        for i in range(max_iterations):

            Z = Z * Z + c
            nZ = Z.real * Z.real + Z.imag * Z.imag
		    # Check for bailout
            if nZ > 4.0:
                row.append(i)
                break

        else:
            row.append(0)

    iteration_array.append(row)

et = time.time()
print(f"Computed in {et - st:.2f} seconds")

# Plotting the data
ax = plt.axes()
ax.set_aspect("equal")
graph = ax.pcolormesh(x_domain, y_domain, iteration_array, cmap=colormap)
plt.colorbar(graph)
plt.xlabel("Real-Axis")
plt.ylabel("Imaginary-Axis")
plt.show()