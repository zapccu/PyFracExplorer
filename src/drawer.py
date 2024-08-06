
from numba import jit

import colors as col

from graphics import *
from fractal import *


class Drawer:

	def __init__(self, app: object, width: int, height: int):
		self.app      = app
		self.bDrawing = False
		self.cancel   = False
		self.width    = width
		self.height   = height
		self.minLen   = -1
		self.maxLen   = -1
		self.colorMapping  = app.getSetting('colorMapping')
		self.drawMode      = app.getSetting('drawMode')
		self.palette       = app.colorTable[app.getSetting('colorPalette')]

		self.colorFnc = {
			'Linear': col.mapValueLinear,
			'Modulo': col.mapValueModulo,
			'RGB':    col.mapValueRGB
		}

		self.drawFnc = {
			'LineByLine': self.drawLineByLine,
			'SquareEstimation': self.drawSquareEstimation
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

	# Map iteration result to color, return numpy RGB array	
	def mapColor(self, maxIter, i) -> np.ndarray:
		if self.colorMapping in self.colorFnc:
			return self.colorFnc[self.colorMapping](value=i, maxValue=maxIter)
		else:
			return self.palette.getDefColor()

	# Iterate point, return mapped color
	def calculatePoint(self, x: int, y: int) -> np.ndarray:
		maxIter, i, Z, diameter, dst, potential = self.fractal.iterate(self.fractal.mapXY(x, y), *self.fractal.calcParameters)

		if diameter >= 0:
			self.statOrbits += 1
			self.minDiameter = min(self.minDiameter, diameter)
			self.maxDiameter = max(self.maxDiameter, diameter)
		#	colors = len(self.palette)
		#	return self.palette[colors-diameter*8-1]
		#else:
		return self.mapColor(maxIter, i)

	@staticmethod
	def getLineColor(coordinates: np.ndarray, imageMap: np.ndarray, flipY: bool = False) -> np.ndarray:
		x1, y1, x2, y2 = coordinates
		y11 = y1
		y21 = y2
		if flipY:
			w, h, d = imageMap.shape
			y11 = h-y2-1
			y21 = h-y1-1

		bUnique = 2
		if y1 == y2 and all(np.all(imageMap[y11, x1:x2+1] == imageMap[y11,x1,:], axis = 1)):
			bUnique = 1
		if x1 == x2 and all(np.all(imageMap[y11:y21+1, x1] == imageMap[y11,x1,:], axis = 1)):
			bUnique = 1
		
		# Return [ red, green, blue, bUnique ] of start point of line
		return np.append(imageMap[y21, x1], bUnique)

	def drawFractal(self, fractal: object, x: int, y: int, width: int, height: int, onStatus=None):
		self.fractal = fractal
		self.onStatus = onStatus
		self.drawMode = self.app.getSetting('drawMode')
		self.colorMapping = self.app.getSetting('colorMapping')
		self.maxLen = max(int(min(width, height)/2), 16)
		self.minLen = min(max(int(min(width, height)/64), 16), self.maxLen)
		self.minLen = 16
		self.maxSplit = 10000

		x2 = x + width -1
		y2 = y + width -1

		if self.bDrawing == False:
			if self.graphics.beginDraw() == False:
				return False
			if self.fractal.beginCalc(self.width, self.height) == False:
				return False
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

		self.drawFnc[self.drawMode](x, y, x2, y2, updateProgress=False)

		print(f"statCalc={self.statCalc} statFill={self.statFill} statSplit={self.statSplit} statOrbits={self.statOrbits}")
		print(f"minDiameter={self.minDiameter} maxDiameter={self.maxDiameter}")

		self.calcTime = self.fractal.endCalc()
		self.graphics.endDraw()
		self.bDrawing = False
		print(f"{self.calcTime} seconds")

		return True

	def drawLineByLine(self, x1: int, y1: int, x2: int, y2: int, updateProgress: bool = False):
		progress = 0
		
		calcParameters = self.fractal.getCalcParameters()

		for y in range(y1, y2+1):
			if updateProgress and self.onStatus is not None:
				newProgress = int(y/(y2-y1+1)*100)
				if newProgress > progress+2:
					progress = newProgress
					self.onStatus({ 'progress': progress })
			if self.cancel: break
			Fractal.calculateLine(
				self.graphics.imageMap, Mandelbrot.iterate, col.mapValueLinear, self.palette,
				x1, y, x2, y, self.fractal.mapXY(x1, y), complex(self.fractal.dx, self.fractal.dy),
				calcParameters, flipY = True
			)
		return True
	
	def drawSquareEstimation (self, x1: int, y1: int, x2: int, y2: int,
			colors = np.zeros((4, 4), dtype=np.uint8), updateProgress=False):

		width  = x2-x1+1
		height = y2-y1+1
		minLen = min(width, height)
		if minLen < 2: return	# Nothing else to draw
		
		# if self.statSplit == 3: return

		# Calculate missing color lines of rectangle
		# Start/end points are calculated twice

		"""
		clcoList = np.array([
			[ x1, y1, x2, y1 ],
			[ x1, y2, x2, y2 ],
			[ x1, y1, x1, y2 ],
			[ x2, y1, x2, y2 ]
		], dtype=int)
		"""
		clcoList = [
			[ x1, y1, x2, y1 ],
			[ x1, y2, x2, y2 ],
			[ x1, y1, x1, y2 ],
			[ x2, y1, x2, y2 ]
		]

		i = 0
		for c in colors:
			if c[3] == 0:
				colors[i] = Fractal.calculateLine(self.graphics.imageMap, Mandelbrot.iterate, col.mapValueLinear, self.palette,
									 clcoList[i], self.fractal.mapXY)
				colors[i] = self.calculateLine(self.graphics.imageMap, Mandelbrot.iterate, *clcoList[i], flipY=True, detectColor=True)
			i += 1

		# Fill rectangle if all sides have the same unique color
		if minLen < self.maxLen and colors[0,3] == 1 and all(np.all(colors == colors[0,:], axis = 1)):
			self.statFill += 1
			self.graphics.setColor(rgb=colors[0,0:3])
			self.graphics.fillRect(x1+1, y1+1, x2, y2)

		elif minLen < self.minLen or self.statSplit >= self.maxSplit:
			# Draw line by line
			# Do not draw the surrounding rectangle (already drawn)
			self.drawLineByLine (x1+1, y1+1, x2-1, y2-1)
			self.statCalc += 1

		else:
			# Split rectangle into child rectangles
			self.statSplit += 1

			# Calculate middle lines
			midX = x1+int(width/2)
			midY = y1+int(height/2)
			self.calculateLine(self.graphics.imageMap, Mandelbrot.iterate, x1, midY, x2, midY, flipY=True, detectColor=False)
			self.calculateLine(self.graphics.imageMap, Mandelbrot.iterate, midX, y1, midX, y2, flipY=True, detectColor=False)

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
			"""
			lcoList = np.array([
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
			], dtype=int)

			# print("get line colors")
			clList = np.apply_along_axis(Drawer.getLineColor, 1, lcoList, self.graphics.imageMap, flipY=True)
			"""
			
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

			clList = [[0, 0, 0, 0]] * 12
			i = 0
			for lco in lcoList:
				clList[i] = Drawer.getLineColor(lco, self.graphics.imageMap, flipY=True)
				i += 1
			
			"""
			# Coordinates of child rectangles
			rcoList = np.array([
				[ x1, y1, midX, midY, 0, 8, 4, 10 ],	# R1
				[ midX, y1, x2, midY, 1, 9, 10, 6 ],	# R2
				[ x1, midY, midX, y2, 8, 2, 5, 11 ],	# R3
				[ midX, midY, x2, y2, 9, 3, 11, 7 ]		# R4
			], dtype=int)
			"""

			rcoList = [
				[ x1, y1, midX, midY, 0, 8, 4, 10 ],	# R1
				[ midX, y1, x2, midY, 1, 9, 10, 6 ],	# R2
				[ x1, midY, midX, y2, 8, 2, 5, 11 ],	# R3
				[ midX, midY, x2, y2, 9, 3, 11, 7 ]		# R4
			]			

			# Recursively call the function for R1-4
			for cr in rcoList:
				self.drawSquareEstimation(*cr[0:4], np.array([clList[i] for i in cr[4:8]]))
				# self.drawSquareEstimation(*cr[0:4], clList[cr[4:8]])
