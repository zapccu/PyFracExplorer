


import time

# import numpy as np
from numba import jit, float64
from numba import types
from numba.typed import Dict

from math import *

@jit
def norm(c: complex):
	return c.real*c.real + c.imag*c.imag

@jit
def result(**kwargs):
	d = Dict.empty(
		key_type=types.unicode_type,
		value_type=types.float64
	)
	for key, value in kwargs.items():
		print(f"{key} = {value}")
		d[key] = value
	return d
	
class Mandelbrot:

	defMaxIter = 100
	defCorner  = complex(-2.0, -1.5)
	defSize    = complex(3.0, 3.0)

	def __init__(self, corner: complex, size: complex, maxIter = 100, flip = False):

		self.screenWidth   = 100
		self.screenHeight  = 100
		self.fractalWidth  = size.real
		self.fractalHeight = size.imag

		self.offsetX = corner.real
		self.offsetY = corner.imag

		self.flip = False

		self.mapScreenCoordinates()

		self.startTime = 0
		self.calcTime  = 0

		self.parameters = { }	# Parameters depending on fractal type

		# Zoom factor
		self.zoom = max(Mandelbrot.defSize.real / size.real, Mandelbrot.defSize.imag / size.imag)
		
		# Calculate
		if maxIter == -1:
			maxIter = max(int(abs(1000 * log(1 / sqrt(self.zoom)))), Mandelbrot.defMaxIter)

		# Orbits: Array for norm(Z) values

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
		self.fractalWidth  = size.real
		self.fractalHeight = size.imag
		self.offsetX = corner.real
		self.offsetY = corner.imag
		self.mapScreenCoordinates()
		self.updateParameters({
			'corner': corner,
			'size': size
		})

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

	def setPeriodicityParameters(self, maxDiameter: int, tolerance: float):
		self.updateParameters({
			'orbits.diameter': maxDiameter,
			'orbits.tolerance': tolerance
		})

	def mapXY(self, x, y):
		return complex(self.dxTab[x], self.dyTab[y])
	
	# Find orbit, return diameter or -1
	# @jit
	def findOrbit(self, i: int, nZ: float) -> int:
		for n in range(i-1, i-self.par('orbits.diameter'), -1):
			if abs(self.orbit[n] - nZ) < self.par('orbits.tolerance'):
				return i-n
		return -1

	# Iterate screen point
	# @jit(nopython=True)
	def iterate(self, x: int, y: int):
		d = Dict.empty(
    		key_type=types.unicode_type,
    		value_type=types.float64
		)
		d['maxIter'] = self.parameters['maxIter']
		d['bailout'] = self.parameters['bailout']
		return self.iterateComplex(self.mapXY(x, y), d)
	
	# Iterate complex point
	# Return dictionary with results
	@staticmethod
	@jit(nopython=True)
	def iterateComplex(C: complex, p):
		Z = C
		i = 1

		bailout = p['bailout']
		bailout *= bailout
		maxIter = p['maxIter']

		distance = complex(1.0)

		nZ = norm(Z)

		while i<maxIter and nZ < bailout:
			Z = Z * Z + C
			nZ = norm(Z)
			i += 1

		return result(iterations=float64(i)) 
	
	def getMaxValue(self):
		return self.par('maxIter')


def calc(f):
	w = 400
	f.beginCalc(w, w)
	for y in range(w):
		for x in range(w):
			f.iterate(x, y)
	return f.endCalc()

frc = Mandelbrot(complex(-2.0,-1.5), complex(3.0, 3.0), maxIter = 500)
t = calc(frc)
print(f"time = {t}")


