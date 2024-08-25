
import time

import numpy as np

from math import *

import colors as col


class Fractal:

	def __init__(self, fractalWidth: float, fractalHeight: float, offsetX: float = 0.0, offsetY: float = 0.0):
		self.screenWidth   = 100
		self.screenHeight  = 100
		self.fractalWidth  = fractalWidth
		self.fractalHeight = fractalHeight

		self.offsetX = offsetX
		self.offsetY = offsetY

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

	def mapX(self, x: int) -> float:
		return self.offsetX + x * self.dx
	
	def mapY(self, y: int) -> float:
		return self.offsetY + y * self.dy

	# Create matrix with mapping of screen coordinates to fractal coordinates
	def mapScreenCoordinates(self):
		self.dx = self.fractalWidth / (self.screenWidth - 1)
		self.dy = self.fractalHeight / (self.screenHeight - 1)
		dxTab = np.outer(np.ones((self.screenWidth,), dtype=np.float64), np.linspace(self.offsetX, self.offsetX+self.fractalWidth, self.screenWidth, dtype=np.float64))
		dyTab = np.outer(1j * np.linspace(self.offsetY, self.offsetY+self.fractalHeight, self.screenHeight, dtype=np.float64), np.ones((self.screenHeight,), dtype=np.complex128))
		self.cplxGrid = dxTab + dyTab

	def mapXY(self, x: int, y: int) -> complex:
		return self.cplxGrid[y,x]
		
	def mapWH(self, width: int, height: int) -> tuple:
		return self.dx * width, self.dy * height
	
	def getMaxValue(self):
		return 1
	
	def beginCalc(self, screenWidth: int, screenHeight: int) -> bool:
		self.screenWidth = screenWidth
		self.screenHeight = screenHeight
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
def calculateSlices(C: np.ndarray, P: np.ndarray, iterFnc, calcParameters: tuple) -> np.ndarray:
	return iterFnc(C, P, *calcParameters)

def getUniqueColor(L: np.ndarray) -> np.ndarray:
	bUnique = 1 if np.all(L == L[0,:]) else 0
	return np.append(L[0], bUnique)

