
import time

import numpy as np
import numba as nb

from math import *

import colors as col


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


"""
Functions optimized by Numba
"""

# Iterate a line from (x, y) to xy (horizontal or vertical, depending on 'orientation')
# orientation: 0 = horizontal, 1 = vertical
# Calculated line includes endpoint xy
# Returns colorline
@nb.njit(cache=True, parallel=True)
def calculateLine(imageMap: np.ndarray, fncIterate, colorMapping: int, palette: np.ndarray,
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
		"""
		C = np.linspace(complex(dxTab[x1], dyTab[y1]), complex(dxTab[x2], dyTab[y1]), x2-x1+1, dtype=np.complex64)
		M, I = fncIterate(C, *calcParameters)
		p = 0
		for x in range(x1, x2+1):
			imageMap[y11, x] = col.mapColorValue(palette, I[p], M[p], colorMapping)
			p += 1
		"""
		for x in nb.prange(x1, x2+1):
			C = complex(dxTab[x], dyTab[y1])
			maxIter, i, Z, diameter, dst = fncIterate(C, *calcParameters)
			imageMap[y11, x] = col.mapColorValue(palette, i, maxIter, colorMapping)
		if detectColor and np.all(imageMap[y11, x1:x2+1] == imageMap[y11,x1,:]): bUnique = 1
	elif x1 == x2:
		# Vertical line
		for y in nb.prange(y1, y2+1):
			C = complex(dxTab[x1], dyTab[y])
			maxIter, i, Z, diameter, dst = fncIterate(C, *calcParameters)
			yy = h-y-1 if flipY else y
			imageMap[yy, x1] = col.mapColorValue(palette, i, maxIter, colorMapping)
		if detectColor and np.all(imageMap[y11:y21+1, x1] == imageMap[y11,x1,:]): bUnique = 1

	# Return [ red, green, blue, bUnique ] of start point of line
	return np.append(imageMap[y21, x1], bUnique)

