
import time

import numpy as np
# from numba import jit

class Fractal:

	screenWidth  = 0
	screenHeight = 0
	fractalWidth  = 0.0
	fractalHeight = 0.0

	dx = 1.0
	dy = 1.0
	dxTab = []
	dyTab = []

	startTime = 0
	calcTime = 0

	def __init__(self, screenWidth: int, screenHeight: int, fractalWidth: float, fractalHeight: float):
		self.setDimensions(screenWidth, screenHeight, fractalWidth, fractalHeight)

	def setDimensions(self, screenWidth: int, screenHeight: int, fractalWidth: float, fractalHeight: float):
		self.screenWidth = screenWidth
		self.screenHeight = screenHeight
		self.fractalWidth = fractalWidth
		self.fractalHeight = fractalHeight
		
		self.dx = self.fractalWidth / self.screenWidth
		self.dy = self.fractalHeight / self.screenHeight
		self.mapScreenCoordinates()

	def mapX(self, x):
		return x * self.dx
	
	def mapY(self, y):
		return y * self.dy

	def mapScreenCoordinates(self):
		self.dxTab = list(map(self.mapX, range(self.screenWidth)))
		self.dyTab = list(map(self.mapY, range(self.screenHeight)))

	def mapXY(self, x, y):
		return (self.dxTab[x], self.dyTab[y])
	
	def iterate(self, x: int, y: int):
		return 1
	
	def getMaxValue(self):
		return 1
	
	def beginCalc(self):
		self.startTime = time.time()
	def endCalc(self):
		endTime = time.time()
		self.calcTime = endTime-self.startTime+1
		return self.calcTime
	
	@staticmethod
	def norm(c: complex):
		return c.real*c.real + c.imag*c.imag


class Mandelbrot(Fractal):

	corner  = complex(-2.0, -1.5)
	size    = complex(3.0, 3.0)
	maxIter = 100
	limit   = 8.0
	radius  = 5

	def __init__(self, screenWidth: int, screenHeight: int, corner: complex, size: complex, maxIter = 100, limit = 8.0):
		super().__init__(screenWidth, screenHeight, size.real, size.imag)

		self.corner  = corner
		self.size    = size
		self.maxIter = maxIter
		self.limit   = limit
		self.orbit = [0.0] * self.radius

	def setParameters(self, screenWidth: int, screenHeight: int, corner: complex, size: complex, maxIter = 100, limit = 8.0):
		super().setDimensions(screenWidth, screenHeight, size.real, size.imag)
		
		self.corner  = corner
		self.size    = size
		self.maxIter = maxIter
		self.limit   = limit
	
	def mapX(self, x):
		return self.corner.real + x * self.dx
	
	def mapY(self, y):
		return self.corner.imag + y * self.dy
	
	def findOrbit(self, i: int, nZ: float):
		for o in range(i-1, -1, -1):
			if self.orbit[o] == nZ:
				return o
		return -1

	def iterate(self, x: int, y: int):
		ca, cb = self.mapXY(x, y)
		return self.iterateComplex(complex(ca, cb))
	
	def iterateComplex(self, C: complex):
		Z = C
		i = 1
		nZ = Fractal.norm(Z)

		while i<self.maxIter and nZ < self.limit:
			Z = Z*Z+C
			nZ = Fractal.norm(Z)

			if self.radius > 0 and i >= self.radius:
				pn = i % self.radius
				if nZ in self.orbit:
					po = self.orbit.index(nZ)
					if pn > po:
						d = pn-po
					else:
						d = self.radius-po+pn

					return (self.maxIter, Z, d)
				else:
					self.orbit[pn] = nZ

			i += 1

		return (i, Z)
	
	def getMaxValue(self):
		return self.maxIter

