
from typing import Type

import numba as nb

import colors as col

from graphics import *
import fractal as frc
import mandelbrot as man


class Drawer:

	def __init__(self, app: object, width: int, height: int):
		self.app      = app
		self.bDrawing = False
		self.cancel   = False
		self.width    = width
		self.height   = height
		self.minLen   = -1
		self.maxLen   = -1
		self.palette  = app.colorTable[app.getSetting('colorPalette')]
		self.iterFnc = {
			'Mandelbrot': man.calculateVectorZ2
		}

		self.drawFnc = {
			'Vectorized': self.drawVectorized,
			'SQEM Recursive': self.drawSquareEstimationRec,
			'SQEM Linear': self.drawSquareEstimation
		}

		canvas = app.gui.drawFrame.canvas

		# Adjust canvas size
		if width != canvas.winfo_reqwidth() or height != canvas.winfo_reqheight():
			canvas.configure(width=width, height=height, scrollregion=(0, 0, width, height))

		# Create graphics environment
		self.graphics = Graphics(canvas, flipY=True)

	# Set drawing color palette
	def setPalette(self, palette: np.ndarray):
		self.palette = palette

	@staticmethod
	@nb.njit(cache=True)
	def getLineColor(x1: int, y1: int, x2: int, y2: int, imageMap: np.ndarray) -> np.ndarray:
		h = imageMap.shape[1]
		y11 = h-y2-1
		y21 = h-y1-1

		bUnique = 2
		if y1 == y2 and np.all(imageMap[y11, x1:x2+1] == imageMap[y11,x1,:]):
			bUnique = 1
		elif x1 == x2 and np.all(imageMap[y11:y21+1, x1] == imageMap[y11,x1,:]):
			bUnique = 1
		
		# Return [ red, green, blue, bUnique ] of start point of line
		return np.append(imageMap[y21, x1], bUnique)

	@staticmethod
	@nb.njit(cache=True)
	def setLineColor(R: np.ndarray, imageMap: np.ndarray, x1: int, y1: int, x2: int, y2: int, detectColor: bool = False) -> np.ndarray:
		h = imageMap.shape[1]
		y11 = h-y2-1
		y21 = h-y1-1
		bUnique = 2

		if y1 == y2:
			imageMap[y11,x1:x2+1] = R
			if detectColor and np.all(imageMap[y11, x1:x2+1] == imageMap[y11,x1,:]): bUnique = 1
		elif x1 == x2:
			imageMap[y11:y21+1, x1] = R
			if detectColor and np.all(imageMap[y11:y21+1, x1] == imageMap[y11,x1,:]): bUnique = 1

		return np.append(imageMap[y21, x1], bUnique)

	def drawFractal(self, fractal: Type[frc.Fractal], x: int, y: int, width: int, height: int, onStatus=None):
		self.fractal = fractal
		self.onStatus = onStatus

		# Get drawing and calculation methods
		drawFnc = self.drawFnc[self.app.getSetting('drawMode')]
		iterFnc = self.iterFnc[self.app.getSetting('fractalType')]
		colorMapping = self.app.getSetting('colorMapping')

		self.maxLen = max(int(min(width, height)/2), 16)
		self.minLen = min(max(int(min(width, height)/64), 16), self.maxLen)
		self.minLen = 16

		x2 = x + width -1
		y2 = y + width -1

		if self.bDrawing == False:
			if self.graphics.beginDraw() == False: return False
			if self.fractal.beginCalc(self.width, self.height) == False: return False
			self.cancel = False
			self.bDrawing = True
		else:
			return False

		self.statFill = 0
		self.statCalc = 0
		self.statSplit = 0
		self.statOrbits = 0
		self.minDiameter = 256
		self.maxDiameter = -1

		calcParameters = self.fractal.getCalcParameters()
		drawFnc(x, y, x2, y2, iterFnc, colorMapping, calcParameters)

		print(f"statCalc={self.statCalc} statFill={self.statFill} statSplit={self.statSplit} statOrbits={self.statOrbits}")
		print(f"minDiameter={self.minDiameter} maxDiameter={self.maxDiameter}")

		self.calcTime = self.fractal.endCalc()
		self.graphics.endDraw()
		self.bDrawing = False
		print(f"{self.calcTime} seconds")

		return True
	
	def drawVectorized(self, x1: int, y1: int, x2: int, y2: int, iterFnc, colorMapping, calcParameters: tuple):
		self.graphics.imageMap[y1:y2+1,x1:x2+1] = np.flip(iterFnc(self.fractal.cplxGrid[y1:y2+1,x1:x2+1], self.palette, *calcParameters), axis=0)
		
	"""
	def drawLineByLine(self, x1: int, y1: int, x2: int, y2: int, iterFnc, colorMapping, calcParameters: tuple):
		for y in range(y1, y2+1):
			self.graphics.imageMap[y,x1:x2+1] = man.calculateSlices(self.fractal.cplxGrid[y,x1:x2+1], self.palette, iterFnc, calcParameters)
	"""
	
	def drawLine(self, C, x1, y1, x2, y2, iterFnc, colorMapping, calcParameters):
		h = self.graphics.imageMap.shape[1]

		# Flip start and end point of vertical line
		y11 = h-y2-1
		y21 = h-y1-1

		if y1 == y2:
			self.graphics.imageMap[y11,x1:x2+1] = frc.calculateSlices(self.fractal.cplxGrid[y1,x1:x2+1], self.palette, iterFnc, calcParameters)
			bUnique = 1 if np.all(self.graphics.imageMap[y11, x1:x2+1] == self.graphics.imageMap[y11,x1,:]) else 0
		else:
			self.graphics.imageMap[y11:y21+1,x1] = np.flip(frc.calculateSlices(self.fractal.cplxGrid[y1:y2+1,x1], self.palette, iterFnc, calcParameters), 0)
			bUnique = 1 if np.all(self.graphics.imageMap[y11:y21+1, x1] == self.graphics.imageMap[y11,x1,:]) else 0
		return np.append(self.graphics.imageMap[y11,x1], bUnique)

	def drawGrid(self, x1: int, y1: int, x2: int, y2: int, iterFnc, colorMapping, calcParameters: tuple):
		width  = x2-x1+1
		height = y2-y1+1
		recSize = 16
		rectangles = int(min(width, height)/recSize)

		xc = np.linspace(x1, x2, rectangles, dtype=np.int32)
		yc = np.linspace(y1, y2, rectangles, dtype=np.int32)
		xr = len(xc)-1
		yr = len(yc)-1

		"""
		for y in yc:
			self.drawLine(self.fractal.cplxGrid[y,x1:x2+1], x1, y, x2, y, iterFnc, colorMapping, calcParameters)
		for x in xc:
			self.drawLine(self.fractal.cplxGrid[y1:y2+1,x], x, y1, x, y2, iterFnc, colorMapping, calcParameters)
		"""

		vColorLines = np.empty((yr,len(xc),4), dtype=np.uint8)
		hColorLines = np.empty((len(yc),xc,4), dtype=np.uint8)

		for y in range(yr):
			for x in range(len(xc)):
				x1 = xc[x]
				y1 = yc[y]
				y2 = yc[y+1]
				vColorLines[y,x] = self.drawLine(self.fractal.cplxGrid[y1:y2+1,x1], x1, y1, x1, y2, iterFnc, colorMapping, calcParameters)
		for y in range(len(yc)):
			for x in range(xr):
				x1 = xc[x]
				x2 = xc[x+1]
				y1 = yc[y]
				hColorLines[y,x] = self.drawLine(self.fractal.cplxGrid[y1,x1:x2+1], x1, y1, x1, y2, iterFnc, colorMapping, calcParameters)

		for y in range(yr):
			for x in range(xr):
				if (np.array_equal(hColorLines[y,x], hColorLines[y+1,x]) and
				   np.array_equal(vColorLines[y,x], vColorLines[y,x+1]) and
				   np.array_equal(hColorLines[y,x], vColorLines[y,x])):
					self.graphics.setColor(hColorLines[y,x])
					self.graphics.fillRect(x1+1, y1+1, x2, y2)
				else:
					self.drawLineByLine(x1+1, y1+1, x2-1, y2-1, iterFnc, colorMapping, calcParameters)

	def drawSquareEstimationRec(self, x1: int, y1: int, x2: int, y2: int, iterFnc, colorMapping, calcParameters: tuple, 
			colors: np.ndarray = np.zeros((4, 4), dtype=np.uint8)):

		width  = x2-x1+1
		height = y2-y1+1
		minLen = min(width, height)
		if minLen < 2: return	# Nothing else to draw

		# Calculate missing color lines of rectangle
		# Start/end points are calculated twice
		clcoList = [
			[ x1, y1, x2, y1 ],
			[ x1, y2, x2, y2 ],
			[ x1, y1, x1, y2 ],
			[ x2, y1, x2, y2 ]
		]

		for i, c in enumerate(colors):
			if c[3] != 1:
				colors[i] = self.drawLine(self.fractal.cplxGrid, *clcoList[i], iterFnc, colorMapping, calcParameters)

		# Fill rectangle if all sides have the same unique color
		if minLen < self.maxLen and np.all(colors == colors[0]):
			self.statFill += 1
			self.graphics.setColor(colors[0,0:3])
			self.graphics.fillRect(x1+1, y1+1, x2, y2)

		elif minLen < self.minLen:
			# Draw line by line
			# Do not draw the surrounding rectangle (already drawn)
			self.drawVectorized(x1+1, y1+1, x2-1, y2-1, iterFnc, colorMapping, calcParameters)
			self.statCalc += 1

		else:
			# Split rectangle into child rectangles
			self.statSplit += 1

			# Calculate middle lines
			midX = x1+int(width/2)
			midY = y1+int(height/2)

			self.drawLine(self.fractal.cplxGrid, x1, midY, x2, midY, iterFnc, colorMapping, calcParameters)
			self.drawLine(self.fractal.cplxGrid, midX, y1, midX, y2, iterFnc, colorMapping, calcParameters)

			# Split color lines
			#
			#  +---0---+---1---+
			#  |       |       |
			#  4   R1  10  R2  6
			#  |       |       |
			#  +---8---+---9---+
			#  |       |       |
			#  5   R3  11  R4  7
			#  |       |       |
			#  +---2---+---3---+
			#
			# Line coordinates			
			lcoList = [
				[x1, y1, midX, y1],
				[midX, y1, x2, y1],
				[x1, y2, midX, y2],
				[midX, y2, x2, y2],
				[x1, y1, x1, midY],
				[x1, midY, x1, y2],
				[x2, y1, x2, midY],
				[x2, midY, x2, y2],
				[x1, midY, midX, midY],
				[midX, midY, x2, midY],
				[midX, y1, midX, midY],
				[midX, midY, midX, y2]
			]

			clList = np.empty((12, 4), dtype=np.uint8)
			for i in range(12):
				clList[i] = Drawer.getLineColor(*lcoList[i], self.graphics.imageMap)

			rcoList = [
				[ x1, y1, midX, midY ],	# R1
				[ midX, y1, x2, midY ],	# R2
				[ x1, midY, midX, y2 ],	# R3
				[ midX, midY, x2, y2 ]	# R4
			]

			clnoList = [
				[ 0, 8, 4, 10 ],
				[ 1, 9, 10, 6 ],
				[ 8, 2, 5, 11 ],
				[ 9, 3, 11, 7 ]
			]		

			# Recursively call the function for R1-4
			for i, coord in enumerate(rcoList):
				self.drawSquareEstimationRec(*coord, iterFnc, colorMapping, calcParameters, clList[clnoList[i]])

	def drawSquareEstimation(self, x1: int, y1: int, x2: int, y2: int, iterFnc, colorMapping, calcParameters: tuple):

		tColor = self.drawLine(self.fractal.cplxGrid, x1, y1, x2, y1, iterFnc, colorMapping, calcParameters)
		bColor = self.drawLine(self.fractal.cplxGrid, x1, y2, x2, y2, iterFnc, colorMapping, calcParameters)
		lColor = self.drawLine(self.fractal.cplxGrid, x1, y1, x1, y2, iterFnc, colorMapping, calcParameters)
		rColor = self.drawLine(self.fractal.cplxGrid, x2, y1, x2, y2, iterFnc, colorMapping, calcParameters)
		colors = np.array([tColor, bColor, lColor, rColor], dtype=np.uint8)

		areaStack = [
			[ x1, y1, x2, y2, colors]
		]

		while len(areaStack) > 0:
			area = areaStack.pop()
			lineColorList = area.pop()
			x1, y1, x2, y2 = area

			width  = x2-x1+1
			height = y2-y1+1
			rectLen = min(width, height)
			if rectLen < 2:
				continue

			# Fill rectangle if all sides have the same unique color
			if rectLen < self.maxLen and np.all(lineColorList == lineColorList[0]):
				self.statFill += 1
				self.graphics.setColor(lineColorList[0,0:3])
				self.graphics.fillRect(x1+1, y1+1, x2, y2)

			elif rectLen < self.minLen:
				# Draw line by line
				# Do not draw the surrounding rectangle (already drawn)
				self.drawVectorized (x1+1, y1+1, x2-1, y2-1, iterFnc, colorMapping, calcParameters)
				self.statCalc += 1

			else:
				# Split rectangle into child rectangles
				self.statSplit += 1

				# Calculate middle lines
				midX = x1+int(width/2)
				midY = y1+int(height/2)

				self.drawLine(self.fractal.cplxGrid, x1, midY, x2, midY, iterFnc, colorMapping, calcParameters)
				self.drawLine(self.fractal.cplxGrid, midX, y1, midX, y2, iterFnc, colorMapping, calcParameters)

				# Split color lines
				#
				#  +---0---+---1---+
				#  |       |       |
				#  4   R1  10  R2  6
				#  |       |       |
				#  +---8---+---9---+
				#  |       |       |
				#  5   R3  11  R4  7
				#  |       |       |
				#  +---2---+---3---+
				#
				# Line coordinates			
				lcoList = [
					[x1, y1, midX, y1],
					[midX, y1, x2, y1],
					[x1, y2, midX, y2],
					[midX, y2, x2, y2],
					[x1, y1, x1, midY],
					[x1, midY, x1, y2],
					[x2, y1, x2, midY],
					[x2, midY, x2, y2],
					[x1, midY, midX, midY],
					[midX, midY, x2, midY],
					[midX, y1, midX, midY],
					[midX, midY, midX, y2]
				]

				clList = np.empty((12, 4), dtype=np.uint8)
				for i, lco in enumerate(lcoList):
					clList[i] = Drawer.getLineColor(*lco, self.graphics.imageMap)

				rcoList = [
					[ x1, y1, midX, midY ],	# R1
					[ midX, y1, x2, midY ],	# R2
					[ x1, midY, midX, y2 ],	# R3
					[ midX, midY, x2, y2 ]	# R4
				]

				clnoList = [
					[ 0, 8, 4, 10 ],
					[ 1, 9, 10, 6 ],
					[ 8, 2, 5, 11 ],
					[ 9, 3, 11, 7 ]
				]

				for i, coord in enumerate(rcoList):
					areaStack.append([ *coord, clList[clnoList[i]] ])

