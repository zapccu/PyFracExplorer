
from typing import Type

from numba import njit, prange

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
			'Mandelbrot': man.iterate
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

	@staticmethod
	@njit(cache=True)
	def getLineColor(x1: int, y1: int, x2: int, y2: int, imageMap: np.ndarray, flipY: bool = True) -> np.ndarray:
		y11 = y1
		y21 = y2
		if flipY:
			w, h, d = imageMap.shape
			y11 = h-y2-1
			y21 = h-y1-1

		bUnique = 2
		if y1 == y2 and np.all(imageMap[y11, x1:x2+1] == imageMap[y11,x1,:]):
			bUnique = 1
		if x1 == x2 and np.all(imageMap[y11:y21+1, x1] == imageMap[y11,x1,:]):
			bUnique = 1
		
		# Return [ red, green, blue, bUnique ] of start point of line
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
		self.maxSplit = 10000

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

	def drawLineByLine(self, x1: int, y1: int, x2: int, y2: int, iterFnc, colorMapping, calcParameters: tuple):
		for y in range(y1, y2+1):
			frc.calculateLine(
				self.graphics.imageMap, iterFnc, colorMapping, self.palette,
				x1, y, x2, y, self.fractal.cplxGrid , calcParameters
			)

	def drawSquareEstimation (self, x1: int, y1: int, x2: int, y2: int, iterFnc, colorMapping, calcParameters: tuple, 
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

		for i in range(4):
			if colors[i,3] == 0:
				x11, y11, x21, y21 = clcoList[i]
				colors[i] = frc.calculateLine(
					self.graphics.imageMap, iterFnc, colorMapping, self.palette,
					x11, y11, x21, y21, self.fractal.cplxGrid, calcParameters, detectColor=True
				)

		# Fill rectangle if all sides have the same unique color
		if minLen < self.maxLen and np.all(colors == colors[0]):
			self.statFill += 1
			self.graphics.setColor(colors[0,0:3])
			self.graphics.fillRect(x1+1, y1+1, x2, y2)

		elif minLen < self.minLen or self.statSplit >= self.maxSplit:
			# Draw line by line
			# Do not draw the surrounding rectangle (already drawn)
			self.drawLineByLine (x1+1, y1+1, x2-1, y2-1, iterFnc, colorMapping, calcParameters)
			self.statCalc += 1

		else:
			# Split rectangle into child rectangles
			self.statSplit += 1

			# Calculate middle lines
			midX = x1+int(width/2)
			midY = y1+int(height/2)

			frc.calculateLine(
				self.graphics.imageMap, iterFnc, colorMapping, self.palette,
				x1, midY, x2, midY, self.fractal.cplxGrid, calcParameters
			)
			frc.calculateLine(
				self.graphics.imageMap, iterFnc, colorMapping, self.palette,
				midX, y1, midX, y2, self.fractal.cplxGrid, calcParameters
			)

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

			clList = np.zeros((12, 4), dtype=np.uint8)
			i = 0
			for lco in lcoList:
				x11, y11, x21, y21 = lco
				clList[i] = Drawer.getLineColor(x11, y11, x21, y21, self.graphics.imageMap)
				i += 1

			rcoList = [
				[ x1, y1, midX, midY, 0, 8, 4, 10 ],	# R1
				[ midX, y1, x2, midY, 1, 9, 10, 6 ],	# R2
				[ x1, midY, midX, y2, 8, 2, 5, 11 ],	# R3
				[ midX, midY, x2, y2, 9, 3, 11, 7 ]		# R4
			]			

			# Recursively call the function for R1-4
			#for cr in rcoList:
			#	x11, y11, x21, y21 = cr[0:4]
			#	self.drawSquareEstimation(x11, y11, x21, y21, iterFnc, colorMapping, calcParameters, clList[cr[4:8]])

			self.drawSquareEstimation(x1, y1, midX, midY, iterFnc, colorMapping, calcParameters, clList[[0, 8, 4, 10] ])
			self.drawSquareEstimation(midX, y1, x2, midY, iterFnc, colorMapping, calcParameters, clList[[1, 9, 10, 6] ])
			self.drawSquareEstimation(x1, midY, midX, y2, iterFnc, colorMapping, calcParameters, clList[[8, 2, 5, 11] ])
			self.drawSquareEstimation(midX, midY, x2, y2, iterFnc, colorMapping, calcParameters, clList[[9, 3, 11, 7] ])

			
