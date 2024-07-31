
import time

import numpy as np

from numba import jit
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

		self.parameters = { }	# Parameters depend on fractal type

	def getDefaults(self):
		return ()
	
	def getParameterNames(self):
		return ()

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

		self.dxTab = list(map(self.mapX, range(self.screenWidth)))
		self.dyTab = list(map(self.mapY, range(self.screenHeight)))

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

	def mapXY(self, x, y):
		return complex(self.dxTab[x], self.dyTab[y])

	def beginCalc(self, screenWidth: int, screenHeight: int, flip: bool = False) -> bool:
		maxIter = 4096 if self.calcDistance else self.maxIter
		bailout = 100.0 if self.calcPotential else self.bailout

		self.calcParameters = (
			self.calcPotential,
			self.calcDistance,
			bailout*bailout,
			maxIter,
			self.maxDiameter,
			self.tolerance
		)

		#self.orbit = np.zeros(maxIter, dtype=np.float64)

		return super().beginCalc(screenWidth, screenHeight, flip)
	
	# Iterate screen point
	def iterate(self, x: int, y: int):
		return self.iterateComplex((self.mapXY(x, y),), self.calcParameters)
	
	# Iterate complex point
	# Return tuple with results
	@staticmethod
	@jit(nopython=True, cache=True)
	def iterateComplex(initValues: tuple, calcPars: tuple):

		dst       = 0		# Default distance
		diameter  = -1		# Default orbit diameter
		potential = 1.0		# Default potential

		# Set initial values for calculation
		distance  = complex(1.0)
		C = initValues[0]
		calcPotential, calcDistance, bailout, maxIter, maxDiameter, tolerance = calcPars
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

			first = max(i-maxDiameter, -1)
			if maxDiameter > 0:
				for n in range(i-1, first, -1):
					if abs(orbit[n] - nZ) < tolerance:
						diameter = i-n
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

