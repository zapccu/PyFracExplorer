
from tkinter import *
from gui import *
from drawer import *

class Application:

	def __init__(self, width: int, height: int, title: str):

		# GUI
		self.gui = GUI(self, title, width, height)

		# Define selection handler
		self.gui.setSelectionHandler(self.onPointSelected, self.onAreaSelected)

		# Default fractal
		# self.fractal = Mandelbrot(complex(-2.0, -1.5), complex(3.0, 3.0))
		self.fractal = Mandelbrot(complex(-0.42125, -1.21125), complex(0.62249, 0.62249), maxIter=500)

	def run(self):
		self.gui.mainWindow.mainloop()

	#
	# Screen selection handling
	#

	def onPointSelected(self, x, y):
		print(f"Selected point {x}, {y}")

	def onAreaSelected(self, x1, y1, x2, y2):
		print(f"Selected area: {x1},{y1} - {x2},{y2}")

	#
	# Command handling
	#
	
	def onDraw(self):
		palette = ColorTable()
		palette.createSinusTable(self.fractal.getMaxValue(), theta=[0, 0, 0])
		# palette.createLinearTable(self.fractal.getMaxValue(), Color(0, 0, 0), Color(255, 255, 255))

		draw = Drawer(self.gui.drawFrame.canvas, 800, 800)
		draw.setPalette(palette)

		draw.drawFractal(self.fractal, 0, 0, 800, 800, Drawer.DRAW_METHOD_RECT)
		# draw.drawFractal(0, 0, 800, 800, Drawer.DRAW_METHOD_LINE)
