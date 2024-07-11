
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

	def setDimensions(self, fractalWidth: float, fractalHeight: float, offsetX: float = 0.0, offsetY: float = 0.0):
		self.fractalWidth  = fractalWidth
		self.fractalHeight = fractalHeight
		self.offsetX = offsetX
		self.offsetY = offsetY
		self.mapScreenCoordinates()

	def mapX(self, x):
		return self.offsetX + x * self.dx
	
	def mapY(self, y):
		return self.offsetY + y * self.dy

	def mapScreenCoordinates(self):
		self.dx = self.fractalWidth / self.screenWidth
		self.dy = self.fractalHeight / self.screenHeight

		self.dxTab = list(map(self.mapX, range(self.screenWidth)))
		self.dyTab = list(map(self.mapY, range(self.screenHeight)))

	def mapXY(self, x, y) -> complex:
		return complex(self.dxTab[x], self.dyTab[y])
	
	def __getitem__(self, index) -> complex:
		return self.mapXY(*index)
	
	def mapWH(self, width: int, height: int) -> complex:
		return complex(self.dx * width, self.dy * height)
	
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

	defCorner = complex(-2.0, -1.5)
	defSize   = complex(3.0, 3.0)

	def __init__(self, corner: complex, size: complex, maxIter = 100, flip = False):
		super().__init__(size.real, size.imag, corner.real, corner.imag, flip)

		self.corner  = corner
		self.size    = size

		self.zoom = max(self.defSize.real / size.real, self.defSize.imag / size.imag)
		
		if maxIter == -1:
			self.maxIter = int(abs(1000 * log(1 / sqrt(self.zoom))))
		else:
			self.maxIter = maxIter

		self.diameter  = 0		# Maximum diameter for orbits, 0 = off
		self.tolerance = 1e-10	# Tolerance for orbit calculation

		self.calcDistance = False
		self.calcPotential = False

		# Allocate array for norm(Z) values
		self.orbit = [0.0] * self.maxIter

	def setParameters(self, corner: complex, size: complex, maxIter = 100):
		super().setDimensions(size.real, size.imag, corner.real, corner.imag)
		
		self.corner  = corner
		self.size    = size
		self.maxIter = maxIter

	def setPeriodicityParameters(self, maxDiameter: int, tolerance: float):
		self.diameter = maxDiameter
		self.tolerance = tolerance
	
	# Find orbit, return diameter or -1
	def findOrbit(self, i: int, nZ: float) -> int:
		for n in range(i-1, i-self.diameter, -1):
			if abs(self.orbit[n] - nZ) < self.tolerance:
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

		limit    = 10000.0 if self.calcPotential else 4.0
		distance = complex(1.0)

		nZ = Fractal.norm(Z)
		self.orbit[0] = nZ

		while i<self.maxIter and nZ < limit:
			Z = Z * Z + C

			if self.calcDistance:
				distance = Z * distance * complex(2.0) + complex(1.0)

			nZ = Fractal.norm(Z)

			if self.diameter > 0 and i >= self.diameter:
				diameter = self.findOrbit(i, nZ)
				if diameter > -1:
					return self.result(maxIter=self.maxIter, iterations=self.maxIter, Z=Z, orbit=diameter)
			
			self.orbit[i] = nZ
			i += 1

		if self.calcDistance:
			distance = sqrt(nZ/abs(d)*0.5*log(sqrt(nZ)))

		if i < self.maxIter and self.calcPotential:
			potential = min(max(0.5*log(nZ)/pow(2.0,float(i)), 0.0), 1.0)
		else:
			potential = 1.0

		return self.result(maxIter=self.maxIter, iterations=i, Z=Z,
					 orbit=0, distance=distance, potential=potential)
	
	def getMaxValue(self):
		return self.maxIter

