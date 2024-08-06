
import time

import numpy as np

from numba import njit, prange
from math import *

"""
statCalc=0 statFill=0 statSplit=0 statOrbits=79818
1.8109090328216553 seconds
"""

_F_POTENTIAL = 1
_F_DISTANCE  = 2

class Fractal:

	def __init__(self, fractalWidth: float, fractalHeight: float, offsetX: float = 0.0, offsetY: float = 0.0, flip: bool = False):
		self.screenWidth   = 100
		self.screenHeight  = 100
		self.fractalWidth  = fractalWidth
		self.fractalHeight = fractalHeight

		self.offsetX = offsetX
		self.offsetY = offsetY

		self.flip = False
		self.flags = 0

		self.mapScreenCoordinates()

		self.startTime = 0
		self.calcTime  = 0

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

	# Iterate a line from (x, y) to xy (horizontal or vertical, depending on 'orientation')
	# orientation: 0 = horizontal, 1 = vertical
	# Calculated line includes endpoint xy
	# Returns colorline
	@staticmethod
	@njit(nopython=True, cache=True, parallel=True)
	def calculateLine(imageMap: np.ndarray, fncIterate, fncMapColor, palette: np.ndarray,
			x1: int, y1: int, x2: int, y2: int, dxTab: np.ndarray, dyTab: np.ndarray, calcParameters: tuple,
			flipY: bool = True, detectColor: bool = False) -> np.ndarray:

		w, h, d = imageMap.shape
		bUnique = 2
		y11 = y1
		y21 = y2

		# Flip start and end point of vertical line
		if flipY:
			y11 = h-y2-1
			y21 = h-y1-1

		if y1 == y2:
			# Horizontal line
			for x in prange(x1, x2+1):
				C = complex(dxTab[x], dyTab[y1])
				maxIter, i, Z, diameter, dst, potential = fncIterate(C, *calcParameters)
				imageMap[y11, x] = fncMapColor(palette, i, maxIter)
			if detectColor and np.all(imageMap[y11, x1:x2+1] == imageMap[y11,x1,:]): bUnique = 1
		elif x1 == x2:
			# Vertical line
			for y in prange(y1, y2+1):
				C = complex(dxTab[x1], dyTab[y])
				maxIter, i, Z, diameter, dst, potential = fncIterate(C, *calcParameters)
				yy = h-y-1 if flipY else y
				imageMap[yy, x1] = fncMapColor(palette, i, maxIter)
			if detectColor and np.all(imageMap[y11:y21+1, x1] == imageMap[y11,x1,:]): bUnique = 1

		# Return [ red, green, blue, bUnique ] of start point of line
		return np.append(imageMap[y21, x1], bUnique)

class Mandelbrot(Fractal):

	_defaults = (
		('flags', 0),
		('bailout', 2.0),
		('maxIter', 256),
		('corner', complex(-2.0, -1.5)),
		('size', complex(3.0, 3.0)),
		('maxDiameter', 10),
		('tolerance', 1e-10),
	)

	_parameterNames = ( 'flags', 'bailout', 'maxIter', 'corner', 'size', 'maxDiameter' )
	_resultNames    = ( 'maxIter', 'iterations', 'Z', 'distance', 'potential' )

	def __init__(self, corner: complex = complex(-2.0, -1.5) , size: complex = complex(3.0, 3.0), maxIter: int = 256, flip = False):
		super().__init__(size.real, size.imag, corner.real, corner.imag, flip)

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
	
	def getCalcParameters(self) -> tuple:
		maxIter = 4096 if self.flags & _F_DISTANCE else self.maxIter
		bailout = 100.0 if self.flags & _F_POTENTIAL else self.bailout
		return (self.flags, bailout*bailout, maxIter, self.maxDiameter, self.tolerance)

	def mapXY(self, x, y):
		return complex(self.dxTab[x], self.dyTab[y])

	# Iterate complex point
	# Return tuple with results
	@staticmethod
	@njit(nopython=True, cache=True)
	def iterate(C, flags, bailout, maxIter, maxDiameter, tolerance):
		dst       = 0		# Default distance
		diameter  = -1		# Default orbit diameter
		potential = 1.0		# Default potential

		# Set initial values for calculation
		distance  = complex(1.0)
		Z = C
		i = 1

		nZ = Z.real*Z.real+Z.imag*Z.imag
		if maxDiameter > 0:
			orbit = np.zeros(maxIter, dtype=np.float64)
			# orbit = [0.0] * maxDiameter
			orbit[0] = nZ

		while i<maxIter and nZ < bailout:
			Z = Z * Z + C
			nZ = Z.real*Z.real+Z.imag*Z.imag

			if flags & _F_DISTANCE:
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

		if flags & _F_DISTANCE:
			aZ = abs(Z)
			dst = sqrt(aZ / abs(distance)) * 0.5 * log(aZ)
			# From https://github.com/makeyourownmandelbrot/Second_Edition/blob/main/DEM_Mandelbrot.ipynb
			# distance = aZ / abs(distance) * 2.0 * log(aZ)
			# Convert to value between 0 and 1:
			# np.tanh(distance*resolution/size)

		if i < maxIter and flags & _F_POTENTIAL:
			potential = min(max(0.5*log(nZ)/pow(2.0,float(i)), 0.0), 1.0)

		return maxIter, i, Z, diameter, dst, potential
	
	def getMaxValue(self):
		return self.maxIter

