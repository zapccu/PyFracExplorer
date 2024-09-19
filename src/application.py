
from tkinter import *
from gui import *

import colors as col
import fractal as frc
import mandelbrot as man
import julia as jul

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
					'initvalue': 800,
					'widget':    'TKCSpinbox',
					'label':     'Width',
					'width':     8,
					'row':       0,
					'column':    0
				},
				"imageHeight": {
					'inputtype': 'int',
					'valrange':  (100, 4096, 100),
					'initvalue': 800,
					'widget':    'TKCSpinbox',
					'label':     'Height',
					'width':     8,
					'row':       0,
					'column':    1
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
					},
					'notify':    self.onFractalTypeChanged
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
		self.fractalRow = self.settings.createMask(self.gui.controlFrame, startrow=self.gui.controlFrame.nextRow(), padx=2, pady=5)
		self.fractal.settings.createMask(self.gui.controlFrame, startrow=self.fractalRow, padx=2, pady=5)

		# We want to be notified if fractal type selection changed
		# self.settings.notify(onchange=self.onSettingsChanged)

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
	
	# Apply button pressed
	def onApply(self):
		imageWidth = self.settings['imageWidth']
		imageHeight = self.settings['imageHeight']

		if self.gui.selection.isAreaSelected():
			# Zoom in
			x1, y1, x2, y2 = self.gui.selection.getArea()
			size = self.fractal.mapWH(x2-x1+1, y2-y1+1, imageWidth, imageHeight)
			corner = self.fractal.mapXY(x1, y1, imageWidth, imageHeight)
			self.fractal.setDimensions(size.real, size.imag, corner.real, corner.imag)
		elif self.gui.selection.isPointSelected():
			if self.settings['fractalType'] == 'Mandelbrot Set':
				# Calculate Julia set at selected point
				x, y = self.gui.selection.getPoint()
				point = self.fractal.mapXY(x, y, imageWidth, imageHeight)
				self.settings.set('fractalType', 'Julia Set', sync=True)
				self.fractal.settings.deleteMask()
				self.fractal = jul.Julia(point=point)
				self.fractal.settings.createMask(self.gui.controlFrame, startrow=self.fractalRow, padx=2, pady=5)
		else:
			self.settings.apply()
			self.fractal.settings.apply()

	# Draw button pressed
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

	# Cancel button pressed
	def onCancel(self):
		self.draw.cancel = True

	def onColorEdit(self):
		ce = ColorEditor(self.gui.mainWindow)
		return

	#
	# Event handling
	#

	# Settings changed
	def onFractalTypeChanged(self, oldValue, newValue):
		self.fractal.settings.deleteMask()
		if newValue == 'Mandelbrot Set':
			self.fractal = man.Mandelbrot()
		else:
			self.fractal = jul.Julia()
		self.fractal.settings.createMask(self.gui.controlFrame, startrow=self.fractalRow, padx=2, pady=5)

	# Status updates
	def onStatusUpdate(self, statusInfo: dict):
		if 'drawing' in statusInfo:
			self.gui.statusFrame.setFieldValue('drawing', statusInfo['drawing'])
		if 'progress' in statusInfo:
			self.gui.statusFrame.setFieldValue('progress', statusInfo['progress'])
			# self.gui.statusFrame.setProgress(statusInfo['progress'])
		if 'update' not in statusInfo or statusInfo['update'] == True:
			self.gui.mainWindow.update()
