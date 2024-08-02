
import time

import numpy as np

from numba import jit, prange
from math import *

"""
statCalc=0 statFill=0 statSplit=0 statOrbits=79818
1.8109090328216553 seconds
"""

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

		self.calcParameters = []

	def getDefaults(self):
		return ()
	
	def getParameterNames(self):
		return ()
	
	def getParameters(self) -> list:
		return self.parameters
	
	def getCalcParameters(self) -> list:
		return []

	def _getParIndex(self, parName: str) -> int:
		parNames = self.getParameterNames()
		try:
			i = parNames.index(parName)
			return i
		except ValueError:
			return -1

	def setDefaults(self):
		defaultValues = self.getDefaults()
		for default in defaultValues:
			setattr(self, default[0], default[1])

	def getDefaultValue(self, parName: str):
		i = self._getParIndex(parName)
		if i >= 0:
			defValues = self.getDefaults()
			return defValues[i][1]
		else:
			return None

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

		self.dxTab = np.linspace(self.offsetX, self.offsetX+self.fractalWidth, self.screenWidth)
		self.dyTab = np.linspace(self.offsetY, self.offsetY+self.fractalHeight, self.screenHeight)

	def mapXY(self, x, y):
		return self.dxTab[x], self.dyTab[y]
		
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


class Mandelbrot(Fractal):

	_defaults = (
		('calcPotential', False),
		('calcDistance', False),
		('bailout', 2.0),
		('maxIter', 256),
		('corner', complex(-2.0, -1.5)),
		('size', complex(3.0, 3.0)),
		('maxDiameter', 3),
		('tolerance', 1e-10),
	)

	_parameterNames = ( 'calcPotential', 'calcDistance', 'bailout', 'maxIter', 'corner', 'size', 'maxDiameter' )
	_resultNames    = ( 'maxIter', 'iterations', 'Z', 'distance', 'potential' )

	def __init__(self, corner: complex = complex(-2.0, -1.5) , size: complex = complex(3.0, 3.0), maxIter: int = 256, flip = False):
		super().__init__(size.real, size.imag, corner.real, corner.imag, flip)

		self.calcDistance  = False
		self.calcPotential = False
		self.bailout       = 2.0
		self.maxDiameter   = 10
		self.tolerance     = 1e-10

		# Calculate zoom factor
		defSize = self.getDefaultValue('size')
		self.zoom = max(defSize.real / size.real, defSize.imag / size.imag)

		if maxIter == -1:
			self.maxIter = max(int(abs(1000 * log(1 / sqrt(self.zoom)))), 256)
		else:
			self.maxIter = maxIter

	def getDefaults(self) -> tuple:
		return Mandelbrot._defaults
	
	def getParameterNames(self) -> tuple:
		return Mandelbrot._parameterNames
	
	def getCalcParameters(self) -> list:
		return [ self.calcPotential, self.calcDistance, self.bailout, self.maxIter, self.maxDiameter, self.tolerance ]

	def mapXY(self, x, y):
		return complex(self.dxTab[x], self.dyTab[y])

	def beginCalc(self, screenWidth: int, screenHeight: int, flip: bool = False) -> bool:
		maxIter = 4096 if self.calcDistance else self.maxIter
		bailout = 100.0 if self.calcPotential else self.bailout

		self.calcParameters = self.getCalcParameters()

		return super().beginCalc(screenWidth, screenHeight, flip)

	# @jit(nopython=True, cache=True, parallel=True):
	# def calculatePoint(imageMap, x: int, y: int,)
	@jit(nopython=True, cache=True, parallel=True)
	def calculateLine(imageMap, x: int, y: int, xy: int, orientation: int,
				   fncMapCoordindates, fncIterate, fncMapColor,
				   corner: complex, delta: complex, calcParameter):
		C = corner
		lineColor = None
		uniqueColor = False
		if orientation == 0:
			for v in prange(x, xy+1):
				C = fncMapCoordindates(v, y)
				maxIter, i, Z, diameter, dst, potential = fncIterate(, *calcParameter)
				color = fncMapColor(i, maxIter)
				if lineColor is None:
					lineColor = color
					uniqueColor = True
				else:
					if not np.array_equal(lineColor, color):
						uniqueColor = False
				imageMap[y, v] = color
				corner += complex(delta.real, 0)
		else:
			for v in range(y, xy+1):
				maxIter, i, Z, diameter, dst, potential = Mandelbrot.iterate(
					C, calcPotential: bool, calcDistance: bool, bailout: float, maxIter: int, maxDiameter: int, tolerance: float)
				color = mapColor(i, maxIter)
				imageMap[v, x] = color
				corner += complex(0, delta.imag)

		return x, y, uniqueColor, lineColor

	# Iterate complex point
	# Return tuple with results
	@staticmethod
	@jit(nopython=True, cache=True)
	def iterate(initValues: tuple, calcPars: tuple):

		dst       = 0		# Default distance
		diameter  = -1		# Default orbit diameter
		potential = 1.0		# Default potential

		# Set initial values for calculation
		distance  = complex(1.0)
		# C = initValues[0]
		# calcPotential, calcDistance, bailout, maxIter, maxDiameter, tolerance = calcPars
		Z = C
		i = 1

		orbit = np.zeros(maxIter, dtype=np.float64)
		nZ = Z.real*Z.real+Z.imag*Z.imag
		orbit[0] = nZ

		while i<maxIter and nZ < bailout:
			Z = Z * Z + C
			nZ = Z.real*Z.real+Z.imag*Z.imag

			if calcDistance:
				distance = Z * distance * 2.0 + 1

			if maxDiameter > 0:
				orbIdx = i % maxDiameter
				startIdx = maxDiameter-1 if i>= maxDiameter else orbIdx-1
				for n in range(startIdx, -1, -1):
					if abs(orbit[n] - nZ) < tolerance:
						diameter = orbIdx-n if orbIdx > n else orbIdx+maxDiameter-n
						i = maxIter-1
						break
				orbit[i] = nZ

			i += 1

		if calcDistance:
			aZ = abs(Z)
			dst = sqrt(aZ / abs(distance)) * 0.5 * log(aZ)
			# From https://github.com/makeyourownmandelbrot/Second_Edition/blob/main/DEM_Mandelbrot.ipynb
			# distance = aZ / abs(distance) * 2.0 * log(aZ)
			# Convert to value between 0 and 1:
			# np.tanh(distance*resolution/size)

		if i < maxIter and calcPotential:
			potential = min(max(0.5*log(nZ)/pow(2.0,float(i)), 0.0), 1.0)

		return maxIter, i, Z, diameter, dst, potential
	
	def getMaxValue(self):
		return self.maxIter

