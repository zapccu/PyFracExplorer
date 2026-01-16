
import time

import numpy as np
from numba import jit, config
from numba import types
from numba.typed import Dict, List

from math import *


# Convert key-value-pairs to numba dictionary
@jit(nopython=True)
def createDict(keys, values):
	d = Dict.empty(
		key_type=types.unicode_type,
		value_type=types.float64
	)
	for i in range(len(keys)):
		d[keys[i]] = float(values[i])
	return d

@jit(nopython=True)
def norm(c: complex) -> float:
	return c.real*c.real + c.imag*c.imag


class Fractal:

	def __init__(self, fractalWidth: float, fractalHeight: float, offsetX: float = 0.0, offsetY: float = 0.0, flip: bool = False):
		self.screenWidth   = 100
		self.screenHeight  = 100
		self.fractalWidth  = fractalWidth
		self.fractalHeight = fractalHeight

		self.offsetX = offsetX
		self.offsetY = offsetY

		self.flip = False

		self.mapScreenCoordinates()

		self.startTime = 0
		self.calcTime  = 0

		self.parameters = { }	# Parameters depending on fractal type

	def setDimensions(self, fractalWidth: float, fractalHeight: float, offsetX: float = 0.0, offsetY: float = 0.0):
		self.fractalWidth  = fractalWidth
		self.fractalHeight = fractalHeight
		self.offsetX = offsetX
		self.offsetY = offsetY
		self.mapScreenCoordinates()

	def mapX(self, x) -> float:
		return self.offsetX + x * self.dx
	
	def mapY(self, y) -> float:
		return self.offsetY + y * self.dy

	# Create tables with mapping of screen coordinates to fractal coordinates
	def mapScreenCoordinates(self):
		self.dx = self.fractalWidth / (self.screenWidth - 1)
		self.dy = self.fractalHeight / (self.screenHeight - 1)

		self.dxTab = list(map(self.mapX, range(self.screenWidth)))
		self.dyTab = list(map(self.mapY, range(self.screenHeight)))

	def mapXY(self, x, y):
		return self.dxTab[x], self.dyTab[y]
	
	# Overwrite existing parameters
	def setParameters(self, parameters: dict):
		self.parameters = parameters

	# Merge parameters
	def updateParameters(self, parameters: dict):
		self.parameters |= parameters

	# Set or query single parameter
	def par(self, name: str, value = None, default = None):
		if value is None:
			if name in self.parameters:
				return self.parameters[name]
			else:
				return default
		else:
			self.parameters[name] = value
	
	# Map screen coordinates to fractal coordinates
	def __getitem__(self, index):
		return self.mapXY(*index)
	
	def mapWH(self, width: int, height: int):
		return self.dx * width, self.dy * height
	
	def getMaxValue(self):
		return 1
	
	def beginCalc(self, screenWidth: int, screenHeight: int, flip: bool = False) -> bool:
		self.screenWidth = screenWidth
		self.screenHeight = screenHeight
		self.flip = flip
		self.mapScreenCoordinates()
		self.startTime = time.time()
		return True

	def endCalc(self) -> float:
		self.endTime = time.time()
		self.calcTime = self.endTime-self.startTime+1
		return self.calcTime
	
	def result(self, **kwargs):
		return kwargs


class Mandelbrot(Fractal):

	AUTO_ITER = -1	# Estimate maximum iterations

	defMaxIter = 100
	defCorner  = complex(-2.0, -1.5)
	defSize    = complex(3.0, 3.0)

	def __init__(self, corner: complex, size: complex, maxIter = 100, flip = False):
		super().__init__(size.real, size.imag, corner.real, corner.imag, flip)

		# Zoom factor
		self.zoom = max(Mandelbrot.defSize.real / size.real, Mandelbrot.defSize.imag / size.imag)
		
		# Calculate
		if maxIter == -1:
			maxIter = max(int(abs(1000 * log(1 / sqrt(self.zoom)))), Mandelbrot.defMaxIter)

		self.setParameters({
			'bailout': 2.0,
			'maxIter': float(maxIter),
			'cornerr': corner.real,
			'corneri': corner.imag,
			'sizer': size.real,
			'sizei': size.imag,
			'orbits.diameter': 0.0,
			'orbits.tolerance': 1e-10,
			'calcPotential': 0.0,
			'calcDistance': 0.0
		})

	def setDimensions(self, corner: complex, size: complex):
		super().setDimensions(size.real, size.imag, corner.real, corner.imag)
		self.updateParameters({
			'corner': corner,
			'size': size
		})

	def setPeriodicityParameters(self, maxDiameter: int, tolerance: float):
		self.updateParameters({
			'orbits.diameter': float(maxDiameter),
			'orbits.tolerance': tolerance
		})

	def mapXY(self, x, y):
		return complex(self.dxTab[x], self.dyTab[y])
	
	# Iterate screen point
	def iterate(self, x: int, y: int):
		kl = list(self.parameters.keys())
		vl = list(self.parameters.values())
		d = createDict(kl, vl)
		return self.iterateComplex(self.mapXY(x, y), d)
	
	# Iterate complex point
	# Return dictionary with results
	@staticmethod
	@jit(nopython=True)
	def iterateComplex(C: complex, P):
		Z = C
		i = 1

		bailout = 100.0 if P['calcPotential'] else P['bailout']
		bailout *= bailout
		maxIter = 4096.0 if P['calcDistance'] else P['maxIter']

		# Orbits: Array for norm(Z) values
		orbit = [0.0] * int(maxIter)

		distance = complex(1.0)

		nZ = norm(Z)
		orbit[0] = nZ
		orbitCount = maxIter
		dst = 0.0
		potential = 1.0

		while i<maxIter and nZ < bailout:
			Z = Z * Z + C

			if P['calcDistance']:
				distance = Z * distance * 2.0 + 1

			nZ = norm(Z)

			if P['orbits.diameter'] > 0 and i >= P['orbits.diameter']:
				for n in range(i-1, i-P['orbits.diameter'], -1):
					if abs(orbit[n] - nZ) < P['tolerance']:
						orbitCount = float(i-n)
			
			orbit[i] = nZ
			i += 1

		if P['calcDistance']:
			aZ = abs(Z)
			dst = sqrt(aZ / abs(distance)) * 0.5 * log(aZ)
			# From https://github.com/makeyourownmandelbrot/Second_Edition/blob/main/DEM_Mandelbrot.ipynb
			# distance = aZ / abs(distance) * 2.0 * log(aZ)
			# Convert to value between 0 and 1:
			# np.tanh(distance*resolution/size)

		if i < maxIter and P['calcPotential']:
			potential = min(max(0.5*log(nZ)/pow(2.0,float(i)), 0.0), 1.0)

		return createDict(['maxIter', 'iterations', 'Zr', 'Zi', 'orbit', 'distance', 'potential'],
					[maxIter, float(i), Z.real, Z.imag, orbitCount, dst, potential])
	
	def getMaxValue(self):
		return int(self.par('maxIter'))

