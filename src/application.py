
from tkinter import *
from gui import *
from drawer import *

class Application:

	def __init__(self, width: int, height: int, title: str):

		# Settings
		self.settings = {
			'colorMapping': {
				'values': [ 'Linear', 'Modulo', 'RGB' ],
				'current': 'Linear',
				'default': 'Linear'
			},
			'drawMode': {
				'values': [ 'LineByLine', 'SquareEstimation' ],
				'current': 'LineByLine',
				'default': 'LineByLine'
			},
			'colorPalette': {
				'values': [ 'Grey', 'Sinus', 'SinusCosinus' ],
				'current': 'Grey',
				'default': 'Grey'
			}
		}

		# GUI
		self.gui = GUI(self, title, width, height, 50, 250)

		# Define selection handler
		self.gui.setSelectionHandler(self.onPointSelected, self.onAreaSelected)

		# Default fractal
		# self.fractal = Mandelbrot(complex(-2.0, -1.5), complex(3.0, 3.0))
		self.fractal = Mandelbrot(complex(-0.42125, -1.21125), complex(0.62249, 0.62249), maxIter=500)

		self.colorTable = {
			'Grey': ColorTable.createLinearTable(self.fractal.getMaxValue(), Color(0, 0, 0), Color(255, 255, 255)),
			'Sinus': ColorTable.createSinusTable(self.fractal.getMaxValue(), theta=[0, 0, 0]),
			'SinusCosinus': ColorTable.createSinusCosinusTable(self.fractal.getMaxValue())
		}

	def run(self):
		self.gui.mainWindow.mainloop()

	def update(self):
		self.gui.mainWindow.update()

	def getSetting(self, parName: str) -> str:
		if parName in self.settings:
			return self.settings[parName]['current']
		else:
			return self.settings[parName]['default']
		
	def setSetting(self, parName: str, value):
		if parName in self.settings:
			self.settings[parName]['current'] = value
		
	def getSettingValues(self, parName: str) -> list[str]:
		if parName in self.settings:
			return self.settings[parName]['values']
		else:
			return []

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
		self.draw = Drawer(self, 800, 800)
		self.draw.drawFractal(self.fractal, 0, 0, 800, 800)

	def onCancel(self):
		self.draw.cancel = True