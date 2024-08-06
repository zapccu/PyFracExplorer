
from tkinter import *
from gui import *

import colors as col

from drawer import *
from coloreditor import *


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
		self.gui = GUI(self, title, width, height, 50, 200)

		# Define selection handler
		self.gui.setSelectionHandler(self.onPointSelected, self.onAreaSelected)

		# Default fractal
		self.fractal = Mandelbrot(complex(-2.0, -1.5), complex(3.0, 3.0))
		# self.fractal = Mandelbrot(complex(-0.42125, -1.21125), complex(0.62249, 0.62249), maxIter=500)

		self.colorTable = {
			'Grey':         col.createLinearPalette(self.fractal.getMaxValue(), (30, 30, 30), (255, 255, 255), defColor=(0, 0, 0)),
			'Sinus':        col.createSinusPalette(self.fractal.getMaxValue(), defColor=(0, 0, 0)),
			'SinusCosinus': col.createSinusCosinusPalette(self.fractal.getMaxValue(), defColor=(0, 0, 0))
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
		width, height = self.fractal.mapWH(x2-x1+1, y2-y1+1)
		corner = self.fractal.mapXY(x1, y1)
		print(f"Complex = {corner} {width},{height}")
		self.fractal = Mandelbrot(corner, complex(width, height))

	#
	# Command handling
	#
	
	def onDraw(self):
		self.gui.drawFrame.clearCanvas()
		self.gui.selection.reset()

		self.gui.statusFrame.setFieldValue('drawing', 'Drawing ...')
		self.onStatusUpdate({'drawing': 'Drawing ...'})
		self.draw = Drawer(self, 800, 800)
		self.draw.drawFractal(self.fractal, 0, 0, 800, 800, onStatus=self.onStatusUpdate)
		self.onStatusUpdate({'drawing': "{:.2f} s".format(self.draw.calcTime)})
		
		self.gui.selection.enable()

	def onCancel(self):
		self.draw.cancel = True

	def onColorEdit(self):
		ce = ColorEditor(self.gui.mainWindow)
		return

	#
	# Event handling
	#

	# Status updates
	def onStatusUpdate(self, statusInfo: dict):
		if 'drawing' in statusInfo:
			self.gui.statusFrame.setFieldValue('drawing', statusInfo['drawing'])
		if 'progress' in statusInfo:
			self.gui.statusFrame.setFieldValue('progress', statusInfo['progress'])
			# self.gui.statusFrame.setProgress(statusInfo['progress'])
		if 'update' not in statusInfo or statusInfo['update'] == True:
			self.gui.mainWindow.update()
