
class Fractal:

	def mapPoint(self, x, y):
		return (x, y)


class Mandelbrot(Fractal):

	corner = complex(-1.5, -1.5)
	size = complex(3.0, 3.0)
	maxIter = 100
	limit = 8.0

	def __init__(self, corner: complex, size: complex, maxIter = 100, limit = 8.0):
		self.corner = corner
		self.size = size
		self.maxIter = maxIter
		self.limit = limit

	def iterate(self, C: complex):
		Z = C
		i = 1

		while i<self.maxIter and abs(Z) < self.limit:
			Z = Z*Z+C
			i += 1

		return (i, Z)

