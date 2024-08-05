
from graphics import *

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

