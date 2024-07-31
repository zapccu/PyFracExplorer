
# from multiprocessing import Process
from colors import *
from graphics import *
from fractal import *

HORIZONTAL = 0
VERTICAL = 1

class ColorLine:

	def __init__(self, graphics: Graphics, x: int, y: int, length: int, orientation: int, unique: bool = False):
		self.graphics = graphics

		self.x = x
		self.y = y

		self.orientation = orientation

		if length > 0:
			if orientation == 0:
				self.length = min(length, graphics.width)
			else:
				self.length = min(length, graphics.height)

			self.checkUnique()
		else:
			self.length = 0
			self.unique = False

	def __repr__(self) -> str:
		if self.orientation == 0:
			x2 = self.x+self.length-1
			return f"H: {self.x},{self.y} -> {self.length} -> {x2},{self.y}"
		else:
			y2 = self.y+self.length-1
			return f"V: {self.x},{self.y} -> {self.length} -> {self.x},{y2}"

	def __len__(self):
		return self.length
	
	# Append color to color line. Consider image dimensions
	def append(self, color: np.ndarray):
		if self.orientation == 0 and self.length < self.graphics.width:
			# self.graphics.imageMap[self.y, self.x+self.length] = color
			self.graphics.setPixelAt(self.x+self.length, self.y, color)
		elif self.orientation == 1 and self.length < self.graphics.height:
			# self.graphics.imageMap[self.y+self.length, self.x] = color
			self.graphics.setPixelAt(self.x, self.y+self.length, color)
		else:
			return

		self.length += 1
		if self.length > 1 and self.unique == True and not np.array_equal(color, self.graphics.getPixelAt(self.x, self.y)):
			self.unique = False
		elif self.length == 1:
			self.unique = True

	def __setitem__(self, xy, color):
		if self.orientation == 0 and xy < self.length:
			self.graphics.imageMap[self.graphics.flip(self.y), xy] = color

		elif self.orientation == 1 and xy < self.length:
			self.graphics.imageMap[self.graphics.flip(xy), self.x] = color

	# Index operator. xy is an offset to x, y
	def __getitem__(self, xy):
		if 0 <= xy <= self.length:
			if self.orientation == 0:
				y = self.graphics.flip(self.y)
				return self.graphics.imageMap[y, self.x+xy]
			else:
				y = self.graphics.flip(self.y+xy)
				return self.graphics.imageMap[y, self.x]
		return None

	# Check if line has unique color
	def checkUnique(self) -> bool:
		if self.length > 0:
			if self.orientation == 0:
				self.unique = self.graphics.isUnique(self.x, self.y, self.x+self.length, self.y)
				# y = self.graphics.flip(self.y)
				# return len(np.unique(self.graphics.imageMap[y, self.x:self.x+self.length], axis = 0)) == 1
			else:
				self.unique = self.graphics.isUnique(self.x, self.y, self.x, self.y+self.length)
				# y1, y2 = self.graphics.flip2(self.y, self.y+self.length)
				# return len(np.unique(self.graphics.imageMap[y1:y2, self.x], axis = 0)) == 1
		else:
			self.unique = False
		return self.unique

	def __eq__(self, b):
		# 2 colorlines are equal, if both have the same unique color. Length doesn't care
		return self.unique and b.unique and np.array_equal(self.graphics.getPixelAt(self.x, self.y), self.graphics.getPixelAt(b.x, b.y))
		ya = self.graphics.flip(self.y)
		yb = self.graphics.flip(b.y)
		return self.unique and b.unique and np.array_equal(self.graphics.imageMap[ya, self.x], b.graphics.imageMap[yb, b.x])
		
	# Split a color line into 2 new color lines, return 2 child color lines
	def split(self):
		if self.length < 2:
			# A line of length < 2 cannot be split
			return None
		mid = int(self.length/2)
		if self.orientation == 0:
			return (
				ColorLine(self.graphics, self.x, self.y, length=mid+1, orientation=self.orientation, unique=self.unique),
				ColorLine(self.graphics, self.x+mid, self.y, length=self.length-mid, orientation=self.orientation, unique=self.unique))
		else:
			return (
				ColorLine(self.graphics, self.x, self.y, length=mid+1, orientation=self.orientation, unique=self.unique),
				ColorLine(self.graphics, self.x, self.y+mid, length=self.length-mid, orientation=self.orientation, unique=self.unique))


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
			'Linear': self.palette.mapValueLinear,
			'Modulo': self.palette.mapValueModulo,
			'RGB':    self.palette.mapValueRGB
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
	def setPalette(self, colors: ColorTable = ColorTable()):
		self.palette = colors

	# Map iteration result to color, return numpy RGB array	
	def mapColor(self, maxIter, i) -> np.ndarray:
		if self.colorMapping in self.colorFnc:
			return self.colorFnc[self.colorMapping](value=i, maxValue=maxIter)
		else:
			return self.palette.getDefColor()

	# Iterate point, return mapped color
	def calculatePoint(self, x: int, y: int) -> np.ndarray:
		maxIter, i, Z, diameter, dst, potential = self.fractal.iterate(x, y)
		if diameter >= 0:
			self.statOrbits += 1
			self.minDiameter = min(self.minDiameter, diameter)
			self.maxDiameter = max(self.maxDiameter, diameter)
		#	colors = len(self.palette)
		#	return self.palette[colors-diameter*8-1]
		#else:
		return self.mapColor(maxIter, i)

	# Iterate a line from (x, y) to xy (horizontal or vertical, depending on 'orientation')
	# orientation: 0 = horizontal, 1 = vertical
	# Calculated line includes endpoint xy
	# Returns colorline
	def calculateLine(self, x: int, y: int, xy: int, orientation: int) -> ColorLine:
		cLine = ColorLine(self.graphics, x, y, length=0, orientation=orientation)

		if orientation == HORIZONTAL:
			for v in range(x, xy+1):
				cLine.append(self.calculatePoint(v, y))
		else:
			for v in range(y, xy+1):
				cLine.append(self.calculatePoint(x, v))

		return cLine

	def drawFractal(self, fractal: object, x: int, y: int, width: int, height: int, onStatus=None):
		self.fractal = fractal
		self.onStatus = onStatus
		self.drawMode = self.app.getSetting('drawMode')
		self.colorMapping = self.app.getSetting('colorMapping')
		self.maxLen = max(int(min(width, height)/2), 16)
		self.minLen = min(max(int(min(width, height)/64), 16), self.maxLen)
		self.minLen = 8
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
		
		for y in range(y1, y2+1):
			if updateProgress and self.onStatus is not None:
				newProgress = int(y/(y2-y1+1)*100)
				if newProgress > progress+2:
					progress = newProgress
					self.onStatus({ 'progress': progress })
			if self.cancel: break
			self.calculateLine(x1, y, x2, HORIZONTAL)
		return True
	
	def drawSquareEstimation (self, x1: int, y1: int, x2: int, y2: int,
		top: ColorLine = None, bottom: ColorLine = None,
		left: ColorLine = None, right: ColorLine = None,
		updateProgress=False):

		width  = x2-x1+1
		height = y2-y1+1
		minLen = min(width, height)
		if minLen < 2: return	# Nothing else to draw
		
		# Calculate missing color lines of rectangle
		# Start/end points are calculated twice
		if top is None:    top    = self.calculateLine(x1, y1, x2, HORIZONTAL)
		if bottom is None: bottom = self.calculateLine(x1, y2, x2, HORIZONTAL)
		if left is None:   left   = self.calculateLine(x1, y1, y2, VERTICAL)
		if right is None:  right  = self.calculateLine(x2, y1, y2, VERTICAL)

		# Fill rectangle if all sides have the same unique color
		if minLen < self.maxLen and top == bottom and left == right and left == top:
			self.statFill += 1
			self.graphics.setColor(rgb=top[0])
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
			midH = self.calculateLine(x1, midY, x2, HORIZONTAL)
			midV = self.calculateLine(midX, y1, y2, VERTICAL)

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
				progress = (cr+1)*25
				if updateProgress and self.onStatus is not None:
					self.onStatus({ 'progress': progress })

