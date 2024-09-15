
import time

import numpy as np
import tkconfigure as tkc

from math import *

import colors as col


class Fractal:

	def __init__(self, fractalWidth: float, fractalHeight: float, offsetX: float = 0.0, offsetY: float = 0.0):
		self.settings = tkc.TKConfigure({
			"Fractal": {
				"corner": {
					"inputtype": "complex",
					"initvalue": complex(offsetX, offsetY),
					"widget":    "TKCEntry",
					"label":     "Corner",
					"width":     20
				},
				"size": {
					"inputtype": "complex",
					"initvalue": complex(fractalWidth, fractalHeight),
					"widget":    "TKCEntry",
					"label":     "Size",
					"width":     20
				}
			}
		})

		self.fractalWidth  = fractalWidth
		self.fractalHeight = fractalHeight
		self.offsetX       = offsetX
		self.offsetY       = offsetY

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
		self.settings.set('corner', complex(offsetX, offsetY), sync=True)
		self.settings.set('size', complex(fractalWidth, fractalHeight), sync=True)

	def dx(self, imageWidth: int) -> float:
		return self.fractalWidth / (imageWidth - 1)
	
	def dy(self, imageHeight: int) -> float:
		return self.fractalHeight / (imageHeight - 1)

	def mapX(self, x: int, imageWidth: int) -> float:
		return self.offsetX + x * self.dx(imageWidth)
	
	def mapY(self, y: int, imageHeight: int) -> float:
		return self.offsetY + y * self.dy(imageHeight)

	def mapXY(self, x: int, y: int, imageWidth: int, imageHeight: int) -> complex:
		return complex(self.mapX(x, imageWidth), self.mapY(y, imageHeight))
		
	def mapWH(self, width: int, height: int, imageWidth: int, imageHeight: int) -> complex:
		return complex(self.dx(imageWidth) * width, self.dy(imageHeight) * height)
	
	# Create matrix with mapping of screen coordinates to fractal coordinates
	def mapScreenCoordinates(self, imageWidth: int, imageHeight: int):
		dxTab = np.outer(np.ones((imageWidth,), dtype=np.float64),
				   np.linspace(self.offsetX, self.offsetX+self.fractalWidth, imageWidth, dtype=np.float64))
		dyTab = np.outer(1j * np.linspace(self.offsetY, self.offsetY+self.fractalHeight, imageHeight, dtype=np.float64),
				   np.ones((imageHeight,), dtype=np.complex128))
		self.cplxGrid = dxTab + dyTab

	def getMaxValue(self):
		return 1
	
	def updateParameters(self):
		pass
	
	def beginCalc(self, screenWidth: int, screenHeight: int) -> bool:
		self.updateParameters()
		self.mapScreenCoordinates(screenWidth, screenHeight)
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

