
from typing import Type
from PIL import Image as Img
from PIL import ImageTk

import numpy as np
import numba as nb

import colors as col
import fractal as frc
import mandelbrot as man
import julia as jul


class Drawer:

	def __init__(self, app: object, width: int, height: int):
		self.app      = app
		self.bDrawing = False
		self.cancel   = False
		self.width    = width
		self.height   = height
		self.minLen   = -1
		self.maxLen   = -1
		self.image    = None

		# Create color table
		palette = col.colorTables[app.palette]
		fnc = col.paletteFunctions[palette['type']]
		self.palette = fnc(palette['size'], **palette['par'])

		self.iterFnc = {
			'Mandelbrot': man.calculateVectorZ2,
			'Julia': jul.calculateVectorZ2
		}

		self.drawFnc = {
			'Vectorized': self.drawVectorized,
			'SQEM Recursive': self.drawSquareEstimationRec,
			'SQEM Linear': self.drawSquareEstimation
		}

		self.canvas = app.gui.drawFrame.canvas

		# Adjust canvas size
		if width != self.canvas.winfo_reqwidth() or height != self.canvas.winfo_reqheight():
			self.canvas.configure(width=width, height=height, scrollregion=(0, 0, width, height))

		# Create graphics environment
		self.imageMap = np.zeros([height, width, 3], dtype=np.uint8)

	# Set drawing color palette
	def setPalette(self, palette: np.ndarray):
		self.palette = palette

	@staticmethod
	@nb.njit(cache=False)
	def getLineColor(x1: int, y1: int, x2: int, y2: int, imageMap: np.ndarray) -> np.ndarray:
		bUnique = 2
		if y1 == y2 and np.all(imageMap[y1, x1:x2+1] == imageMap[y1,x1,:]):
			bUnique = 1
		elif x1 == x2 and np.all(imageMap[y1:y2+1, x1] == imageMap[y1,x1,:]):
			bUnique = 1
		
		# Return [ red, green, blue, bUnique ] of start point of line
		return np.append(imageMap[y1, x1], bUnique)

	def showImage(self, scale: int):
		if self.image is not None:
			maxImageRes = max(self.width, self.height)
			minFrameRes = min(self.app.gui.drawFrame.winfo_width(), self.app.gui.drawFrame.winfo_height())
			if scale == 1 and maxImageRes > minFrameRes:
				# Reduce image size to fit in drawing frame if autoScale=1
				self.scaleFactor = minFrameRes / maxImageRes
				newWidth = int(self.width * self.scaleFactor)
				newHeight = int(self.height * self.scaleFactor)
				self.canvas.configure(width=newWidth, height=newHeight, scrollregion=(0, 0, newWidth, newHeight))
				self.zoomImage = self.image.resize((newWidth, newHeight))
				self.tkImage = ImageTk.PhotoImage(self.zoomImage)
			else:
				self.scaleFactor = 1.0
				self.canvas.configure(width=self.width, height=self.height, scrollregion=(0, 0, self.width, self.height))
				self.tkImage = ImageTk.PhotoImage(self.image)
			self.canvas.create_image(0, 0, image=self.tkImage, state='normal', anchor='nw')
			self.canvas.update()

	def drawFractal(self, fractal: Type[frc.Fractal], x: int, y: int, width: int = -1, height: int = -1, onStatus=None):
		self.fractal = fractal
		self.onStatus = onStatus

		# Get drawing and calculation methods
		drawFnc = self.drawFnc[self.app['drawMode']]
		iterFnc = self.iterFnc[self.app['fractalType']]

		if width == -1:
			width = self.width
		else:
			self.width = width
		if height == -1:
			height = self.height
		else:
			self.height = height

		oversampling = max(1, min(3, fractal.settings['oversampling']))
		print(f"oversampling={oversampling}")
		
		oWidth = width * oversampling
		oHeight = height * oversampling

		self.maxLen = max(int(min(oWidth, oHeight)/2), 16)
		self.minLen = min(max(int(min(oWidth, oHeight)/8), 16), self.maxLen)

		x2 = x + oWidth -1
		y2 = y + oHeight -1

		if self.bDrawing == False:
			if self.fractal.beginCalc(oWidth, oHeight) == False: return False
			self.cancel = False
			self.bDrawing = True
		else:
			return False

		self.statFill = 0
		self.statCalc = 0
		self.statSplit = 0
		self.statOrbits = 0

		calcParameters = self.fractal.getCalcParameters()

		self.fractal.settings.dumpConfig()
		print("Calc parameters=", calcParameters)

		# Prepare image map for oversampling
		if oversampling > 1:
			self.imageMap = np.resize(self.imageMap, (oHeight, oWidth, 3))
			
		drawFnc(x, y, x2, y2, iterFnc, calcParameters)

		# Reduce image map to original size
		if oversampling > 1:
			self.imageMap = self.imageMap.reshape((height, oversampling, width, oversampling, 3)).mean(3).mean(1).astype(np.uint8)

		print(f"statCalc={self.statCalc} statFill={self.statFill} statSplit={self.statSplit} statOrbits={self.statOrbits}")

		self.calcTime = self.fractal.endCalc()
		self.bDrawing = False

		# Full size image
		self.image = Img.fromarray(self.imageMap, 'RGB').transpose(Img.Transpose.FLIP_TOP_BOTTOM)

		# Show image
		self.showImage(self.app['autoScale'])

		print(f"{self.calcTime} seconds")

		return True
	
	def drawVectorized(self, x1: int, y1: int, x2: int, y2: int, iterFnc, calcParameters: tuple):
		self.imageMap[y1:y2+1,x1:x2+1] = iterFnc(self.fractal.cplxGrid[y1:y2+1,x1:x2+1], self.palette, *calcParameters)

	def drawLineByLine(self, x1: int, y1: int, x2: int, y2: int, iterFnc, calcParameters: tuple):
		for y in range(y1, y2+1):
			self.imageMap[y,x1:x2+1] = man.calculateSlices(self.fractal.cplxGrid[y,x1:x2+1], self.palette, iterFnc, calcParameters)
	
	# Calculate and draw a line, detect unique color
	def drawLine(self, C, x1, y1, x2, y2, iterFnc, calcParameters):
		if y1 == y2:
			self.imageMap[y1,x1:x2+1] = frc.calculateSlices(self.fractal.cplxGrid[y1,x1:x2+1], self.palette, iterFnc, calcParameters)
			bUnique = 1 if np.all(self.imageMap[y1, x1:x2+1] == self.imageMap[y1,x1,:]) else 0
		else:
			self.imageMap[y1:y2+1,x1] = frc.calculateSlices(self.fractal.cplxGrid[y1:y2+1,x1], self.palette, iterFnc, calcParameters)
			bUnique = 1 if np.all(self.imageMap[y1:y2+1, x1] == self.imageMap[y1,x1,:]) else 0
		return np.append(self.imageMap[y1,x1], bUnique)

	def drawGrid(self, x1: int, y1: int, x2: int, y2: int, iterFnc, calcParameters: tuple):
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
				vColorLines[y,x] = self.drawLine(self.fractal.cplxGrid[y1:y2+1,x1], x1, y1, x1, y2, iterFnc, calcParameters)
		for y in range(len(yc)):
			for x in range(xr):
				x1 = xc[x]
				x2 = xc[x+1]
				y1 = yc[y]
				hColorLines[y,x] = self.drawLine(self.fractal.cplxGrid[y1,x1:x2+1], x1, y1, x1, y2, iterFnc, calcParameters)

		"""
		for y in range(yr):
			for x in range(xr):
				if (np.array_equal(hColorLines[y,x], hColorLines[y+1,x]) and
				   np.array_equal(vColorLines[y,x], vColorLines[y,x+1]) and
				   np.array_equal(hColorLines[y,x], vColorLines[y,x])):
					self.graphics.setColor(hColorLines[y,x])
					self.graphics.fillRect(x1+1, y1+1, x2, y2)
				else:
					self.drawLineByLine(x1+1, y1+1, x2-1, y2-1, iterFnc, colorMapping, calcParameters)
		"""

	def drawSquareEstimationRec(self, x1: int, y1: int, x2: int, y2: int, iterFnc, calcParameters: tuple, 
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
				colors[i] = self.drawLine(self.fractal.cplxGrid, *clcoList[i], iterFnc, calcParameters)

		# Fill rectangle if all sides have the same unique color
		if minLen < self.maxLen and np.all(colors == colors[0]):
			self.statFill += 1
			self.imageMap[y1+1:y2, x1+1:x2] = colors[0,0:3]

		elif minLen < self.minLen:
			# Draw line by line
			# Do not draw the surrounding rectangle (already drawn)
			self.drawVectorized(x1+1, y1+1, x2-1, y2-1, iterFnc, calcParameters)
			self.statCalc += 1

		else:
			# Split rectangle into child rectangles
			self.statSplit += 1

			# Calculate middle lines
			midX = x1+int(width/2)
			midY = y1+int(height/2)

			self.drawLine(self.fractal.cplxGrid, x1, midY, x2, midY, iterFnc, calcParameters)
			self.drawLine(self.fractal.cplxGrid, midX, y1, midX, y2, iterFnc, calcParameters)

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
				clList[i] = Drawer.getLineColor(*lcoList[i], self.imageMap)

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

			# Recursively call the function for rectangles R1-4
			for i, coord in enumerate(rcoList):
				self.drawSquareEstimationRec(*coord, iterFnc, calcParameters, clList[clnoList[i]])

	def drawSquareEstimation(self, x1: int, y1: int, x2: int, y2: int, iterFnc, calcParameters: tuple):

		tColor = self.drawLine(self.fractal.cplxGrid, x1, y1, x2, y1, iterFnc, calcParameters)
		bColor = self.drawLine(self.fractal.cplxGrid, x1, y2, x2, y2, iterFnc, calcParameters)
		lColor = self.drawLine(self.fractal.cplxGrid, x1, y1, x1, y2, iterFnc, calcParameters)
		rColor = self.drawLine(self.fractal.cplxGrid, x2, y1, x2, y2, iterFnc, calcParameters)
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
				self.imageMap[y1+1:y2, x1+1:x2] = lineColorList[0,0:3]

			elif rectLen < self.minLen:
				# Draw line by line
				# Do not draw the surrounding rectangle (already drawn)
				self.drawVectorized (x1+1, y1+1, x2-1, y2-1, iterFnc, calcParameters)
				self.statCalc += 1

			else:
				# Split rectangle into child rectangles
				self.statSplit += 1

				# Calculate middle lines
				midX = x1+int(width/2)
				midY = y1+int(height/2)

				self.drawLine(self.fractal.cplxGrid, x1, midY, x2, midY, iterFnc, calcParameters)
				self.drawLine(self.fractal.cplxGrid, midX, y1, midX, y2, iterFnc, calcParameters)

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
					clList[i] = Drawer.getLineColor(*lco, self.imageMap)

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

