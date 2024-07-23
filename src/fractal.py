
import time

# import numpy as np

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

		self.parameters = { }	# Parameters depend on fractal type

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
	
	def norm(self, c: complex):
		return c.real*c.real + c.imag*c.imag
	
	def result(self, **kwargs):
		return kwargs


class Mandelbrot(Fractal):

	AUTO_ITER = -1	# Estimate maximum iterations

	defaults = {
		'bailout': 2.0,
		'maxIter': 256,
		'corner': complex(-2.0, -1.5),
		'size': complex(3.0, 3.0),
		'orbits.diameter': 3,
		'orbits.tolerance': 1e-10,
		'calcPotential': False,
		'calcDistance': False
	}

	def __init__(self, corner: complex, size: complex, maxIter: int = 0, flip = False):
		super().__init__(size.real, size.imag, corner.real, corner.imag, flip)

		# Zoom factor
		self.zoom = max(Mandelbrot.defaults['size'].real / size.real, Mandelbrot.defaults['size'].imag / size.imag)

		if maxIter == -1:
			maxIter = max(int(abs(1000 * log(1 / sqrt(self.zoom)))), Mandelbrot.defaults['maxIter'])
		elif maxIter == 0:
			maxIter = self.defaults['maxIter']

		self.setParameters(Mandelbrot.defaults)
		self.updateParameters({
			'maxIter': maxIter,
			'corner': corner,
			'size': size
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

	# Iterate screen point
	def iterate(self, x: int, y: int) -> dict:
		return self.iterateComplex(self.mapXY(x, y))
	
	# Iterate complex point
	# Return dictionary with results
	def iterateComplex(self, C: complex) -> dict:
		bailout = 100.0 if self.par('calcPotential', default=False) else self.par('bailout')
		bailout *= bailout
		maxIter = 4096 if self.par('calcDistance', default=False) else self.par('maxIter')
		orbit = [0.0] * maxIter

		dst       = 0		# Default distance
		diameter  = -1		# Default orbit diameter
		potential = 1.0		# Default potential

		# Set initial values for calculation
		Z = C
		i = 1
		nZ = self.norm(Z)
		orbit[0] = nZ
		distance = complex(1.0)
		maxDiameter = self.par('orbits.diameter')
		tolerance = self.par('orbits.tolerance')

		while i<maxIter and nZ < bailout:
			Z = Z * Z + C

			if self.par('calcDistance', default=False):
				distance = Z * distance * 2.0 + 1

			nZ = self.norm(Z)

			if maxDiameter > 0 and i >= maxDiameter:
				for n in range(i-1, i-maxDiameter, -1):
					if abs(orbit[n] - nZ) < tolerance:
						diameter = i-n
						i = maxIter-1
						break
			
			orbit[i] = nZ
			i += 1

		if self.par('calcDistance', default=False):
			aZ = abs(Z)
			dst = sqrt(aZ / abs(distance)) * 0.5 * log(aZ)
			# From https://github.com/makeyourownmandelbrot/Second_Edition/blob/main/DEM_Mandelbrot.ipynb
			# distance = aZ / abs(distance) * 2.0 * log(aZ)
			# Convert to value between 0 and 1:
			# np.tanh(distance*resolution/size)

		if i < maxIter and self.par('calcPotential', default=False):
			potential = min(max(0.5*log(nZ)/pow(2.0,float(i)), 0.0), 1.0)

		return self.result(maxIter=maxIter, iterations=i, Z=Z,
			orbit=diameter, distance=dst, potential=potential)
	
	def getMaxValue(self):
		return self.par('maxIter')

