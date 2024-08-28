
from tkinter import *
from gui import *

import colors as col
import fractal as frc
import mandelbrot as man

from drawer import *
from coloreditor import *

import tkconfigure as tkc

class Application:

	def __init__(self, width: int, height: int, title: str):

		# Settings
		self.settings = tkc.TKConfigure({
			"Fractal selection": {
				"fractalType": {
					'inputType': 'int',
					'valRange':  [
						'Mandelbrot Set', 'Julia Set'
					],
					'initValue': 0,
					'widget':    'TKCListbox',
					'label':     'Fractal type:',
					'width':     15,
					'widgetAttr': {
						'justify': 'left'
					}
				},
				"drawMode": {
					'inputType': 'int',
					'valRange':  [
						'Vectorized', 'SQEM Recursive', 'SQEM Linear'
					],
					'initValue': 0,
					'widget':    'TKCListbox',
					'label':     'Draw mode:',
					'width':     15,
					'widgetAttr': {
						'justify': 'left'
					},
				},
				'colorPalette': {
					'inputType': 'int',
					'valRange':  [
						'Monochrome', 'Grey', 'Sinus', 'SinusCosinus', 'RedGreenBlue', 'BlueGrey'
					],
					'initValue': 0,
					'widget':    'TKCListbox',
					'label':     'Color palette:',
					'width':     15,
					'widgetAttr': {
						'justify': 'left'
					}
				}
			}
		})

		# Default fractal
		self.fractal = man.Mandelbrot(complex(-2.0, -1.5), complex(3.0, 3.0))
		# self.fractal = man.Mandelbrot(complex(-0.42125, -1.21125), complex(0.62249, 0.62249), maxIter=500)

		# GUI
		self.gui = GUI(self, title, width, height, 50, 200)

		# Define selection handler
		self.gui.setSelectionHandler(self.onPointSelected, self.onAreaSelected)

		maxValue = self.fractal.getMaxValue()
		self.colorTable = {
			'Monochrome':   col.createLinearPalette(self.fractal.getMaxValue()),
			'Grey':         col.createLinearPalette(self.fractal.getMaxValue(), [(80,80,80), (255,255,255)], defColor=(0, 0, 0)),
			'Sinus':        col.createSinusPalette(self.fractal.getMaxValue(), defColor=(0, 0, 0)),
			'SinusCosinus': col.createSinusCosinusPalette(self.fractal.getMaxValue(), defColor=(0, 0, 0)),
			'RedGreenBlue': col.createLinearPalette(self.fractal.getMaxValue(), [(125,30,0),(30,255,30),(0,30,125)]),
			'BlueGrey':     col.createLinearPalette(maxValue, [(100,100,100),(200,200,200),(0,0,255)])
		}

	def run(self):
		self.gui.mainWindow.mainloop()

	def update(self):
		self.gui.mainWindow.update()

	def getSetting(self, parName: str) -> str:
		return self.settings[parName]['current']
		
	def setSetting(self, parName: str, value):
		if parName in self.settings:
			if value is not None and value in self.settings[parName]['values']:
				self.settings[parName]['current'] = value
			else:
				self.settings[parName]['current'] = self.settings[parName]['default']
		
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
		if self.gui.selection.isAreaSelected():
			x1, y1, x2, y2 = self.gui.selection.getArea()
			width, height = self.fractal.mapWH(x2-x1+1, y2-y1+1)
			corner = self.fractal.mapXY(x1, y1)
			self.fractal = man.Mandelbrot(corner, complex(width, height), -1)

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
