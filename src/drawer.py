
from colors import *
from graphics import *
from fractal import *


class Drawer:

	HORIZONTAL = 0
	VERTICAL = 1

	def __init__(self, graphics: Graphics, fractal: Fractal, minLen: int = -1, maxLen: int = -1):
		self.bDrawing = False
		self.graphics = graphics
		self.fractal = fractal
		self.minLen = minLen
		self.maxLen = maxLen

	# Iterate a line from x, y
	# orientation: 0 = horizontal, 1 = vertical
	def calculateLine(self, x: int, y: int, xy: int, orientation: int) -> ColorLine:
		cLine = ColorLine()
		r = range(x, xy+1) if orientation == 0 else range(y, xy+1)

		for v in r:
			result = self.fractal.iterate(v, y) if orientation == 0 else self.fractal.iterate(x, v)
			color = self.graphics.colors.getMapColor(result[0], self.fractal.getMaxValue())
			cLine += color.rgb

		return cLine
	
	# Draw a color line from (x, y)
	# orientaion: 0 = horizontal, 1 = vertical
	def drawColorLine(self, cLine: ColorLine, x: int, y: int, orientation: int):
		self.graphics.moveTo(x, y)
		curColor = cLine[0]
		d = len(cLine)

		if orientation == 0:
			v = x
			lineTo = self.graphics.horzLineTo
		else:
			v = y 
			lineTo = self.graphics.vertLineTo

		for i in range(1, d):
			if cLine[i] != curColor:
				self.graphics.setColor(intColor = curColor)
				lineTo(v + i)
				curColor = cLine[i]

		self.graphics.setColor(intColor = curColor)
		lineTo(v + d)

	def beginDraw(self, width: int, height: int) -> bool:
		if self.bDrawing == False:
			if self.graphics.beginDraw(width, height) == False: return False
			if self.fractal.beginCalc(width, height) == False: return False
			self.bDrawing = True
		return self.bDrawing
	
	def endDraw(self) -> float:
		if self.bDrawing == True:
			calcTime = self.fractal.endCalc()
			self.graphics.endDraw()
			self.bDrawing = False
			return calcTime
		else:
			return 0.0

	def drawFractal(self, x: int, y: int, width: int, height: int):
		self.maxLen = max(int(min(width, height)/2), 16)
		self.minLen = min(max(int(min(width, height)/8), 16), self.maxLen)

		if self.beginDraw(width, height) == False:
			return False

		self.drawLineByLine(x, y, x+width-1, y+width-1)

		calcTime = self.endDraw()
		print(f"{calcTime} seconds")

		return True

	def drawLineByLine(self, x1: int, y1: int, x2: int, y2: int):
		for y in range(y1, y2+1):
			cLine = self.calculateLine(x1, y, x2, Drawer.HORIZONTAL)
			self.drawColorLine(cLine, x1, y, Drawer.HORIZONTAL)
		
		return True
	
	def drawSquareEstimation (self, x1: int, y1: int, x2: int, y2: int,
							top: ColorLine, bottom: ColorLine, left: ColorLine, right: ColorLine):

		width  = x2-x1+1
		height = y2-y1+1
		minLen = min(width, height)
		if minLen < 2:
			return	# Nothing else to draw
		
		# Calculate missing color lines of rectangle
		if len(top)    == 0: top    = self.calculateLine(x1, y1, x2, Drawer.HORIZONTAL)
		if len(bottom) == 0: bottom = self.calculateLine(x1, y2, x2, Drawer.HORIZONTAL)
		if len(left)   == 0: left   = self.calculateLine(x1, y1, y2, Drawer.VERTICAL)
		if len(right)  == 0: right  = self.calculateLine(x2, y1, y2, Drawer.VERTICAL)

		# Fill rectangle if all sides have the same unique color
		if minLen < self.maxLen and top.isUnique() and top == bottom and left == right and left == top:
			self.graphics.setColor(intColor = top[0])
			self.graphics.fillRect(x1+1, y1+1, x2, y2)	# Rectangle doesn't include x2, y2

		elif minLen < self.minLen:
			# Draw line by line
			return self.drawLineByLine (x1+1, y1+1, x2-1, y2-1)

		else:
			# Split into child rectangles

			# Calculate middle lines
			midX = x1+int(width/2)
			midY = y1+int(height/2)
			midH = self.calculateLine(x1+1, midY, x2-1, Drawer.HORIZONTAL)
			midV = self.calculateLine(midX, y1+1, y2-1, Drawer.VERTICAL)

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
			clList = []
			for cl in (top, bottom, left, right, midH, midV):
				clList.extend(cl.split())
			
			# Coordinates of child rectangles
			coList = [
				[ x1, y1, midX, midY ],	# R1
				[ midX, y1, x2, midY ],	# R2
				[ x1, midY, midX, y2 ],	# R3
				[ midX, midY, x2, y2 ]	# R4
			]

			# Color line indices for child rectangles
			clRectIdx = [
				[ 0, 8, 4, 10 ],	# R1
				[ 1, 9, 10, 6 ],	# R2
				[ 8, 2, 5, 11 ],	# R3
				[ 9, 3, 11, 7 ]		# R4
			]

			# Recursively call the function for R1-4
			for cr in range(0, 4):
				self.drawSquareEstimation(*coList[cr],
					clList[clRectIdx[cr][0]], clList[clRectIdx[cr][1]], clList[clRectIdx[cr][2]], clList[clRectIdx[cr][3]]
				)

