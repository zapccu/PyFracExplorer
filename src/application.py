
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
			"Image parameters": {
				"imageWidth": {
					'inputtype': 'int',
					'valrange':  (100, 4096, 100),
					'initvalue': 1000,
					'widget':    'TKCSpinbox',
					'label':     'Width',
					'width':     8
				},
				"imageHeight": {
					'inputtype': 'int',
					'valrange':  (100, 4096, 100),
					'initvalue': 1000,
					'widget':    'TKCSpinbox',
					'label':     'Height',
					'width':     8
				}
			},
			"Fractal selection": {
				"fractalType": {
					'inputtype': 'str',
					'valrange':  [
						'Mandelbrot Set', 'Julia Set'
					],
					'initvalue': 'Mandelbrot Set',
					'widget':    'TKCListbox',
					'label':     'Fractal type:',
					'width':     15,
					'widgetattr': {
						'justify': 'left'
					}
				},
				"drawMode": {
					'inputtype': 'str',
					'valrange':  [
						'Vectorized', 'SQEM Recursive', 'SQEM Linear'
					],
					'initvalue': 'Vectorized',
					'widget':    'TKCListbox',
					'label':     'Draw mode:',
					'width':     15,
					'widgetattr': {
						'justify': 'left'
					},
				},
				'colorPalette': {
					'inputtype': 'str',
					'valrange':  [
						'Monochrome', 'Grey', 'Sinus', 'SinusCosinus', 'RedGreenBlue', 'BlueGrey'
					],
					'initvalue': 'Grey',
					'widget':    'TKCListbox',
					'label':     'Color palette:',
					'width':     15,
					'widgetattr': {
						'justify': 'left'
					}
				}
			}
		})

		# Default fractal
		self.fractal = man.Mandelbrot(complex(-2.25, -1.5), complex(3.0, 3.0))
		# self.fractal = man.Mandelbrot(complex(-0.42125, -1.21125), complex(0.62249, 0.62249), maxIter=500)

		# Create GUI
		self.gui = GUI(self, title, width, height, statusHeight=50, controlWidth=300)

		# Create settings widgets
		row = self.settings.createMask(self.gui.controlFrame, startrow=self.gui.controlFrame.nextRow(), padx=2, pady=5)
		self.fractal.settings.createMask(self.gui.controlFrame, startrow=row, padx=2, pady=5)

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

	def __getitem__(self, index: str):
		return self.settings.get(index)
	
	def run(self):
		self.gui.mainWindow.mainloop()

	def update(self):
		self.gui.mainWindow.update()

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
	
	def onApply(self):
		if self.gui.selection.isAreaSelected():
			x1, y1, x2, y2 = self.gui.selection.getArea()
			imageWidth = self.settings['imageWidth']
			imageHeight = self.settings['imageHeight']
			size = self.fractal.mapWH(x2-x1+1, y2-y1+1, imageWidth, imageHeight)
			corner = self.fractal.mapXY(x1, y1, imageWidth, imageHeight)
			self.fractal.setDimensions(size.real, size.imag, corner.real, corner.imag)
		else:
			self.settings.apply()
			self.fractal.settings.apply()

	def onDraw(self):

		self.gui.drawFrame.clearCanvas()
		self.gui.selection.reset()

		self.gui.statusFrame.setFieldValue('drawing', 'Drawing ...')
		self.onStatusUpdate({'drawing': 'Drawing ...'})
		w = self.settings['imageWidth']
		h = self.settings['imageHeight']
		print(f"Image size = {w} x {h}")
		self.draw = Drawer(self, w, h)
		self.draw.drawFractal(self.fractal, 0, 0, w, h, onStatus=self.onStatusUpdate)
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
