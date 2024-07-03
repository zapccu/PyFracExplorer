
from colors import *
from graphics import *
from fractal import *

class Drawer:

	HORIZONTAL = 0
	VERTICAL = 1

	# Draw methods
	DRAW_METHOD_LINE = 1
	DRAW_METHOD_RECT = 2

	# Color mapping modes
	COLOR_MAPPING_LINEAR = 1	# Linear mapping of iterations to canvas color palette
	COLOR_MAPPING_MODULO = 2	# Mapping to canvas color palette by modulo division
	COLOR_MAPPING_RGB    = 2	# Linear mapping of iterations to RGB color space


	def __init__(self, graphics: Graphics, fractal: Fractal, width: int, height: int,
			  minLen: int = -1, maxLen: int = -1, mapping = 1, debug = False):
		self.bDrawing = False
		self.graphics = graphics
		self.fractal  = fractal
		self.width    = width
		self.height   = height
		self.minLen   = minLen
		self.maxLen   = maxLen
		self.mapping  = mapping
		self.defColor = 0				# Black
		self.palette  = ColorTable()	# White (1 entry)
		self.debug    = debug

	# Set drawing color palette
	def setPalette(self, colors: ColorTable = ColorTable()):
		self.palette = colors

	# Map iteration result to color	
	def mapColor(self, result) -> int:
		color = Color.NOCOLOR

		if self.mapping == Drawer.COLOR_MAPPING_LINEAR:
			color = self.palette[int(len(self.palette) / result['maxIter'] * result['iterations'])]
		elif self.mapping == Drawer.COLOR_MAPPING_MODULO:
			color = self.palette[result['iterations'] % len(self.palette)]
		elif self.mapping == Drawer.COLOR_MAPPING_RGB:
			color = int(result['iterations'] * Color.MAXCOLOR / result['maxIter'])
		
		return self.defColor if color == Color.NOCOLOR else color

	# Iterate point, return mapped color
	def caclulatePoint(self, x: int, y: int) -> int:
		result = self.fractal.iterate(x, y)
		return self.mapColor(result)

	# Iterate a line from (x, y) to xy (horizontal or vertical, depending on 'orientation')
	# orientation: 0 = horizontal, 1 = vertical
	# Calculated line includes endpoint xy
	# Returns colorline
	def calculateLine(self, x: int, y: int, xy: int, orientation: int) -> ColorLine:
		if orientation == Drawer.HORIZONTAL:
			return ColorLine(list(map(
				lambda v: self.caclulatePoint(v, y), range(x, xy+1)
			)))
		else:
			return ColorLine(list(map(
				lambda v: self.caclulatePoint(x, v), range(y, xy+1)
			)))
	
	# Draw a color line from (x, y) to xy (horizontal or vertical, depending on 'orientation')
	# orientaion: 0 = horizontal, 1 = vertical
	# Line includes endpoint xy
	# Returns colorline
	def drawColorLine(self, x: int, y: int, xy: int, orientation: int, cLine: ColorLine = ColorLine()) -> ColorLine:
		if cLine.isEmpty():
			cLine = self.calculateLine(x, y, xy, orientation)
		self.graphics.moveTo(x, y)
		curColor = cLine[0]
		d = len(cLine)

		if orientation == Drawer.HORIZONTAL:
			v = x
			lineToFnc = self.graphics.horzLineTo
		else:
			v = y 
			lineToFnc = self.graphics.vertLineTo

		for i in range(1, d):
			if cLine[i] != curColor:
				self.graphics.setColor(intColor = curColor)
				lineToFnc(v + i)
				curColor = cLine[i]

		if orientation == Drawer.HORIZONTAL and self.graphics.x <= xy or orientation == Drawer.VERTICAL and self.graphics.y <= xy:
			self.graphics.setColor(intColor = curColor)
			lineToFnc(xy+1)
			# lineToFnc(v + d)

		return cLine

	def beginDraw(self) -> bool:
		if self.bDrawing == False:
			if self.graphics.beginDraw(self.width, self.height) == False: return False
			self.bDrawing = True
		return self.bDrawing
	
	def endDraw(self):
		if self.bDrawing == True:
			self.graphics.endDraw()
			self.bDrawing = False

	def drawFractal(self, x: int, y: int, width: int, height: int, method: int):
		self.maxLen = max(int(min(width, height)/2), 16)
		self.minLen = min(max(int(min(width, height)/64), 16), self.maxLen)
		self.minLen = 4

		x2 = x + width -1
		y2 = y + width -1
		
		if self.beginDraw() == False: return False
		if self.fractal.beginCalc(width, height) == False: return False

		if method == Drawer.DRAW_METHOD_LINE:
			self.drawLineByLine(x, y, x2, y2)
		elif method == Drawer.DRAW_METHOD_RECT:
			self.statFill = 0
			self.statCalc = 0
			self.statSplit = 0
			self.drawSquareEstimation(x, y, x2, y2)
			print(f"statCalc={self.statCalc} statFill={self.statFill} statSplit={self.statSplit}")

		calcTime = self.fractal.endCalc()
		self.endDraw()
		print(f"{calcTime} seconds")

		return True

	def drawLineByLine(self, x1: int, y1: int, x2: int, y2: int):
		for y in range(y1, y2+1):
			self.drawColorLine(x1, y, x2, Drawer.HORIZONTAL)

		return True
	
	def drawSquareEstimation (self, x1: int, y1: int, x2: int, y2: int,
		top: ColorLine = ColorLine(), bottom: ColorLine = ColorLine(),
		left: ColorLine = ColorLine(), right: ColorLine = ColorLine()):

		width  = x2-x1+1
		height = y2-y1+1
		minLen = min(width, height)
		if minLen < 2:
			return	# Nothing else to draw
		
		# Calculate missing color lines of rectangle
		# Start/end points are calculated twice
		if len(top)    == 0: top    = self.drawColorLine(x1, y1, x2, Drawer.HORIZONTAL)
		if len(bottom) == 0: bottom = self.drawColorLine(x1, y2, x2, Drawer.HORIZONTAL)
		if len(left)   == 0: left   = self.drawColorLine(x1, y1, y2, Drawer.VERTICAL)
		if len(right)  == 0: right  = self.drawColorLine(x2, y1, y2, Drawer.VERTICAL)

		# Fill rectangle if all sides have the same unique color
		if minLen < self.maxLen and top.isUnique() and top == bottom and left == right and left == top:
			self.statFill += 1
			self.graphics.setColor(intColor = top[0])
			self.graphics.fillRect(x1+1, y1+1, x2, y2)

		elif minLen < self.minLen or self.debug:
			# Draw line by line
			self.statCalc += 1
			# Do not draw the surrounding rectangle (already drawn)
			# self.graphics.setColor(intColor = 0xFF0000)
			# self.graphics.fillRect(x1+1, y1+1, x2, y2)
			self.drawLineByLine (x1+1, y1+1, x2-1, y2-1)

		else:
			# Split rectangle into child rectangles
			self.statSplit += 1

			# Calculate middle lines
			midX = x1+int(width/2)
			midY = y1+int(height/2)
			midH = self.drawColorLine(x1, midY, x2, Drawer.HORIZONTAL)
			midV = self.drawColorLine(midX, y1, y2, Drawer.VERTICAL)

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
				# Mid point belongs to both child lines
				clList.extend(cl.split(overlap=1))
			
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

