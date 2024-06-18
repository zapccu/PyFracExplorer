
class Fractal:

	screenWidth = 0
	screenHeight = 0
	fractalWidth = 0.0
	fractalHeight = 0.0

	dx = 0.0
	dy = 0.0

	def __init__(self, screenWidth: int, screenHeight: int, fractalWidth: float, fractalHeight: float):
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


class Mandelbrot(Fractal):

	corner = complex(-1.5, -1.5)
	size = complex(3.0, 3.0)
	maxIter = 100
	limit = 8.0

	def __init__(self, screenWidth: int, screenHeight: int, corner: complex, size: complex, maxIter = 100, limit = 8.0):
		super.__init__(screenWidth, screenHeight, size.real(), size.imag())

		self.corner = corner
		self.size = size
		self.maxIter = maxIter
		self.limit = limit

	def mapX(self, x):
		return self.corner.real() + x * self.dx
	
	def mapX(self, x):
		return self.corner.real() + x * self.dx

	def iterate(self, C: complex):
		Z = C
		i = 1

		while i<self.maxIter and abs(Z) < self.limit:
			Z = Z*Z+C
			i += 1

		return (i, Z)

