
class Fractal:

	screenWidth  = 0
	screenHeight = 0
	fractalWidth  = 0.0
	fractalHeight = 0.0

	dx = 1.0
	dy = 1.0
	dxTab = []
	dyTab = []

	def __init__(self, screenWidth: int, screenHeight: int, fractalWidth: float, fractalHeight: float):
		self.setDimensions(screenWidth, screenHeight, fractalWidth, fractalHeight)

	def setDimensions(self, screenWidth: int, screenHeight: int, fractalWidth: float, fractalHeight: float):
		self.screenWidth = screenWidth
		self.screenHeight = screenHeight
		self.fractalWidth = fractalWidth
		self.fractalHeight = fractalHeight
		
		self.dx = self.fractalWidth / self.screenWidth
		self.dy = self.fractalHeight / self.screenHeight
		self.mapScreenCoordinates()

	def mapX(self, x):
		return x * self.dx
	
	def mapY(self, y):
		return y * self.dy

	def mapScreenCoordinates(self):
		self.dxTab = list(map(self.mapX, range(self.screenWidth)))
		self.dyTab = list(map(self.mapY, range(self.screenHeight)))

	def mapXY(self, x, y):
		return (self.dxTab[x], self.dyTab[y])
	
	def iterate(self, x: int, y: int):
		return 1
	
	def getMaxValue(self):
		return 1


class Mandelbrot(Fractal):

	corner  = complex(-2.0, -1.5)
	size    = complex(3.0, 3.0)
	maxIter = 100
	limit   = 8.0

	def __init__(self, screenWidth: int, screenHeight: int, corner: complex, size: complex, maxIter = 100, limit = 8.0):
		super().__init__(screenWidth, screenHeight, size.real, size.imag)

		self.corner  = corner
		self.size    = size
		self.maxIter = maxIter
		self.limit   = limit

	def setParameters(self, screenWidth: int, screenHeight: int, corner: complex, size: complex, maxIter = 100, limit = 8.0):
		super().setDimensions(screenWidth, screenHeight, size.real, size.imag)
		
		self.corner  = corner
		self.size    = size
		self.maxIter = maxIter
		self.limit   = limit
	
	def mapX(self, x):
		return self.corner.real + x * self.dx
	
	def mapY(self, y):
		return self.corner.imag + y * self.dy
	
	def isLimit(self, c: complex):
		return c.real*c.real + c.imag*c.imag > self.limit

	def iterate(self, x: int, y: int):
		ca, cb = self.mapXY(x, y)
		return self.iterate(complex(ca, cb))
	
	def iterate(self, C: complex):
		Z = C
		i = 1

		while i<self.maxIter and self.isLimit(Z) == False:
			Z = Z*Z+C
			i += 1

		return (i, Z)
	
	def getMaxValue(self):
		return self.maxIter

