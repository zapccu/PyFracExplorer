
import time

# import numpy as np
# from numba import jit

from math import *


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
	
	@staticmethod
	def norm(c: complex):
		return c.real*c.real + c.imag*c.imag
	
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

		# Orbits: Array for norm(Z) values
		self.orbit = [0.0] * maxIter

		self.setParameters({
			'bailout': 2.0,
			'maxIter': maxIter,
			'corner': corner,
			'size': size,
			'orbits.diameter': 0,
			'orbits.tolerance': 1e-10,
			'calcPotential': False,
			'calcDistance': False
		})

	def setDimensions(self, corner: complex, size: complex):
		super().setDimensions(size.real, size.imag, corner.real, corner.imag)
		self.updateParameters({
			'corner': corner,
			'size': size
		})

	def setPeriodicityParameters(self, maxDiameter: int, tolerance: float):
		self.updateParameters({
			'orbits.diameter': maxDiameter,
			'orbits.tolerance': tolerance
		})

	def mapXY(self, x, y):
		return complex(self.dxTab[x], self.dyTab[y])
	
	# Find orbit, return diameter or -1
	def findOrbit(self, i: int, nZ: float) -> int:
		for n in range(i-1, i-self.par('orbits.diameter'), -1):
			if abs(self.orbit[n] - nZ) < self.par('orbits.tolerance'):
				return i-n
		return -1

	# Iterate screen point
	def iterate(self, x: int, y: int) -> dict:
		return self.iterateComplex(self.mapXY(x, y))
	
	# Iterate complex point
	# Return dictionary with results
	def iterateComplex(self, C: complex) -> dict:
		Z = C
		i = 1

		bailout = 100.0 if self.par('calcPotential', default=False) else self.par('bailout')
		bailout *= bailout
		maxIter = 4096 if self.par('calcDistance', default=False) else self.par('maxIter')

		distance = complex(1.0)

		nZ = Fractal.norm(Z)
		self.orbit[0] = nZ

		while i<maxIter and nZ < bailout:
			Z = Z * Z + C

			if self.par('calcDistance', default=False):
				distance = Z * distance * 2.0 + 1

			nZ = Fractal.norm(Z)

			if self.par('orbits.diameter') > 0 and i >= self.par('orbits.diameter'):
				diameter = self.findOrbit(i, nZ)
				if diameter > -1:
					return self.result(maxIter=maxIter, iterations=maxIter, Z=Z, orbit=diameter)
			
			self.orbit[i] = nZ
			i += 1

		if self.par('calcDistance', default=False):
			aZ = abs(Z)
			distance = sqrt(aZ / abs(distance)) * 0.5 * log(aZ)
			# From https://github.com/makeyourownmandelbrot/Second_Edition/blob/main/DEM_Mandelbrot.ipynb
			# distance = aZ / abs(distance) * 2.0 * log(aZ)
			# Convert to value between 0 and 1:
			# np.tanh(distance*resolution/size)

		if i < maxIter and self.par('calcPotential', default=False):
			potential = min(max(0.5*log(nZ)/pow(2.0,float(i)), 0.0), 1.0)
		else:
			potential = 1.0

		return self.result(maxIter=maxIter, iterations=i, Z=Z,
					 orbit=0, distance=distance, potential=potential)
	
	def getMaxValue(self):
		return self.par('maxIter')

