
from tkinter import *
from tkinter import filedialog as fd, messagebox
from gui import *

import json

import colors as col
import presets as ps
import fractal as frc
import mandelbrot as man
import julia as jul

from drawer import *

import tkconfigure.src.tkconfigure as tkc


class Application:

	def __init__(self, width: int, height: int, title: str):

		# Default fractal
		self.fractal = man.Mandelbrot()

		self.colorSettings = tkc.TKConfigure({
			"Color parameters": {
				"type": {
					'inputtype': 'str',
					'valrange':  ['Linear', 'Sinus', 'SinusCosinus'],
					'initvalue': 'Linear',
					'widget':    'TKCListbox',
					'label':     'Type',
					'width':     15
				},
				"name": {
					'inputtype': 'str',
					'initvalue': 'Grey',
					'widget':    'TKCEntry',
					'label':     'Name',
					'width':     20
				},
				"size": {
					'inputtype': 'int',
					'valrange':  (2, 4096, 50),
					'initvalue': 4096,
					'widget':    'TKCSpinbox',
					'label':     'Size',
					'width':     8
				},
				"par": {
					'inputtype': 'list',
					'initvalue': [(0.4, 0.4, 0.4), (1.0, 1.0, 1.0)],
					'widget':    'TKCList',
					'label':     'Parameters',
					'width':     20
				}
			}
		})

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
				},
				"autoScale": {
					'inputtype': 'int',
					'valrange':  (0, 1),
					'initvalue': 1,
					'widget':    'TKCCheckbox',
					'label':     'Autoscale',
					'notify':     self.onAutoscale
				}
			},
			"Fractal selection": {
				"preset": {
					'inputtype': 'str',
					'valrange':  ['None'] + list(ps.presets.keys()),
					'initvalue': 'None',
					'widget':    'TKCListbox',
					'label':     'Preset',
					'width':     15,
					'notify':    self.onPresetSelected
				},
				"fractalType": {
					'inputtype': 'str',
					'valrange':  [
						'Mandelbrot', 'Julia'
					],
					'initvalue': 'Mandelbrot',
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
					'valrange':  list(col.colorTables.keys()),
					'initvalue': 'Grey',
					'widget':    'TKCListbox',
					'label':     'Color palette:',
					'width':     15,
					'widgetattr': {
						'justify': 'left'
					},
					'notify': self.onPaletteChanged
				},
				'colorTable': {
					'inputtype': 'tkc',
					'initvalue': self.colorSettings,
					'widget':    'TKCColortable',
					'label':     'Color table',
					'width':     200,
					'notify':    self.onColorTableChanged,
					'pardef':    self.colorSettings.parDef
				},
				'defColor': {
					'inputtype': 'str',
					'valrange':  ('^#([0-9a-fA-F]{2}){3}$',),
					'initvalue': '#000000',
					'label':     'Default color',
					'widget':    'TKCColor',
					'width':     80
				}
			}
		})

		# Default color palette
		# self.palette = 'Grey'

		# Image drawer
		self.draw = None

		# Fractal definition file
		self.filename = None

		# Create GUI
		self.gui = GUI(self, title, width, height, statusHeight=50, controlWidth=400)

		# Create menu
		self.menubar = Menu(self.gui.mainWindow)

		# File menu
		self.fileMenu = Menu(self.menubar, tearoff=0)
		self.fileMenu.add_command(label="Open ...", command=self.onFileOpen)
		self.fileMenu.add_command(label="Save", command=self.onFileSave)
		self.fileMenu.add_command(label="Save as ...", command=self.onFileSaveAs)
		self.fileMenu.add_separator()
		self.fileMenu.add_command(label="Exit", command=self.gui.mainWindow.quit)
		self.menubar.add_cascade(label="File", menu=self.fileMenu)

		# Image menu
		self.imageMenu = Menu(self.menubar, tearoff=0)
		self.imageMenu.add_command(label="Save as ...", state="disabled", command=self.onImageSaveAs)
		self.menubar.add_cascade(label="Image", menu=self.imageMenu)

		self.gui.mainWindow.config(menu=self.menubar)

		# Create settings widgets
		self.fractalRow = self.settings.createMask(self.gui.controlFrame, startrow=self.gui.controlFrame.nextRow(), padx=2, pady=3, submasks=False)
		self.fractal.settings.createMask(self.gui.controlFrame, startrow=self.fractalRow, padx=2, pady=3)

		# Define selection handler
		self.gui.setSelectionHandler(self.onPointSelected, self.onAreaSelected, self.onSelectionCancelled)

	def __getitem__(self, index: str):
		return self.settings.get(index)
	
	def run(self):
		self.gui.mainWindow.mainloop()

	def update(self):
		self.gui.mainWindow.update()

	# Apply a preset, create fractal and palette, adjust input mask
	def applyPreset(self, preset: dict) -> bool:
		self.fractal.settings.deleteMask()

		if 'corner' in preset and 'size' in preset:
			corner = preset['corner']
			size   = preset['size']
		elif 'coord' in preset:
			corner = complex(preset['coord'][0], preset['coord'][2])
			size   = complex(preset['coord'][1]-preset['coord'][0], preset['coord'][3]-preset['coord'][2])
		else:
			return False

		if preset['type'] == 'Mandelbrot':
			self.fractal = man.Mandelbrot(corner, size, maxIter=preset['maxIter'], stripes=preset['stripes'],
								steps=preset['steps'], ncycle=preset['ncycle'])
		else:
			self.fractal = jul.Julia(preset['point'], corner, size, maxIter=preset['maxIter'], stripes=preset['stripes'],
								steps=preset['steps'], ncycle=preset['ncycle'])

		self.fractal.settings.setValues(colorize=preset['colorize'], colorOptions=preset['colorOptions'])

		col.colorTables['Preset'] = preset['palette']
		self.settings['colorPalette'] = 'Preset'
		# self.palette = 'Preset'
		self.settings.setValues(sync=True, colorPalette='Preset', fractalType=preset['type'])

		# colorTable = col.createPalette('Preset').tolist()
		self.settings.set('colorTable', [preset['palette'], 'Preset'], sync=True)

		self.fractal.settings.createMask(self.gui.controlFrame, startrow=self.fractalRow, padx=2, pady=3)

		return True
	
	def saveSettingsToFile(self, filename: str) -> bool:
		try:
			js = {
				'application': self.settings.getConfig(simple=True),
				'fractal':     self.fractal.settings.getConfig(simple=True)
			}

			with open(filename, "w") as outputFile:
				outputFile.write(tkc.TKConfigure.toJSON(js))
				return True
			
		except Exception as e:
			print(e)
			messagebox.showerror("Error", "Cannot save fractal settings to file")
			return False
		
	def loadSettingsFromFile(self, filename: str) -> bool:
		try:
			with open(filename, "r") as inputFile:
				js = json.load(inputFile, object_hook=tkc.TKConfigure._decodeJSON)

				for section in ('application', 'fractal'):
					if section not in js:
						raise KeyError(f"Missing section {section} in JSON")

				print("Set application parameters")
				self.settings.setConfig(js['application'], simple=True, checkmissing=True)

				if self.settings['fractalType'] not in ('Mandelbrot', 'Julia'):
					raise KeyError(f"Unknow fractal type {self.settings['fractalType']}")
				
				self.fractal.settings.deleteMask()

				if self.settings['fractalType'] == 'Mandelbrot':
					self.fractal = man.Mandelbrot()
				else:
					self.fractal = jul.Julia()

				self.fractal.settings.setConfig(js['fractal'], simple=True, checkmissing=True)
				self.fractal.settings.createMask(self.gui.controlFrame, startrow=self.fractalRow, padx=2, pady=3)

				return True

		except Exception as e:
			print("ERROR", e)
			messagebox.showerror("Error", "Cannot read fractal settings from file")
			return False
	

	###########################################################################
	# Menu command handling
	###########################################################################

	# Open fractal definition
	def onFileOpen(self):
		fileTypes = [
			('Fractal definition', '*.frc'),
			('All files', '*')
		]
		fileName = fd.askopenfilename(filetypes=fileTypes)
		if fileName is not None:
			self.loadSettingsFromFile(fileName)

	# Save fractal defintion using current filename
	def onFileSave(self):
		if self.filename is None:
			self.onFileSaveAs()
		else:
			self.saveSettingsToFile(self.filename)

	# Save fractal definition
	def onFileSaveAs(self):
		fileTypes = [
			('Fractal definition', '*.frc')
		]
		fileName = fd.asksaveasfilename(filetypes=fileTypes)
		if self.saveSettingsToFile(fileName):
			self.filename = fileName

	# Save image
	def onImageSaveAs(self):
		fileTypes = [('PNG Image', '*.png')]
		fileName = fd.asksaveasfilename(filetypes=fileTypes, initialfile="image.png", defaultextension="png")
		if fileName is not None and self.draw is not None and self.draw.image is not None:
			self.draw.image.save(fileName, "png")


	###########################################################################
	# Screen selection handling
	###########################################################################

	def onPointSelected(self, x, y):
		self.gui.controlFrame.btnApply.config(state=NORMAL)
		print(f"Selected point {x}, {y}")

	def onAreaSelected(self, x1, y1, x2, y2):
		self.gui.controlFrame.btnApply.config(state=NORMAL)
		print(f"Selected area: {x1},{y1} - {x2},{y2}")

	def onSelectionCancelled(self):
		self.gui.controlFrame.btnApply.config(state=DISABLED)


	###########################################################################
	# Command handling
	###########################################################################
	
	# Apply button pressed
	def onApply(self):
		imageWidth, imageHeight = self.settings.getValues(['imageWidth', 'imageHeight'])

		if self.gui.selection.isAreaSelected():
			# Zoom in
			x1, y1, x2, y2 = self.gui.selection.getArea()
			print(f"x1={x1}, y1={y1}, x2={x2}, y2={y2}")
			size   = self.fractal.mapWH(x2-x1+1, y2-y1+1, imageWidth, imageHeight)
			corner = self.fractal.mapXY(x1, y1, imageWidth, imageHeight)
			print("corner=", corner, "size=", size)
			self.fractal.setDimensions(corner, size)

		elif self.gui.selection.isPointSelected():
			if self.settings['fractalType'] == 'Mandelbrot':
				# Calculate Julia set at selected point
				x, y = self.gui.selection.getPoint()
				point = self.fractal.mapXY(x, y, imageWidth, imageHeight)
				self.settings.set('fractalType', 'Julia', sync=True)
				self.fractal.settings.deleteMask()
				self.fractal = jul.Julia(point=point)
				self.fractal.settings.createMask(self.gui.controlFrame, startrow=self.fractalRow, padx=2, pady=3)
		else:
			self.settings.apply()
			self.fractal.settings.apply()

	# Draw button pressed
	def onDraw(self):
		self.gui.drawFrame.clearCanvas()
		self.gui.selection.reset()

		self.gui.statusFrame.setFieldValue('drawing', 'Drawing ...')
		self.onStatusUpdate({'drawing': 'Drawing ...'})
		w, h = self.settings.getValues(['imageWidth', 'imageHeight'])
		self.draw = Drawer(self, w, h)
		self.draw.drawFractal(self.fractal, 0, 0, w, h, onStatus=self.onStatusUpdate)
		self.onStatusUpdate({'drawing': "{:.2f} s".format(self.draw.calcTime)})
		
		self.imageMenu.entryconfig('Save as ...', state="normal")
		self.gui.selection.enable(scalefactor=self.draw.scaleFactor)

	# Cancel button pressed
	def onCancel(self):
		self.draw.cancel = True


	###########################################################################
	# Widget event handling
	###########################################################################

	# Autoscale enabled/disabled
	def onAutoscale(self, oldValue, newValue):
		self.draw.showImage(scale=newValue)

	# Fractal preset selected
	def onPresetSelected(self, oldValue, newValue):
		if newValue != 'None':
			# Apply new preset
			self.applyPreset(ps.presets[newValue])

		elif oldValue != 'None':
			# Reset to default
			self.fractal.settings.deleteMask()
			self.fractal = man.Mandelbrot()
			self.settings.set('colorPalette', 'Grey', sync=True)
			# self.palette = 'Grey'
			self.fractal.settings.createMask(self.gui.controlFrame, startrow=self.fractalRow, padx=2, pady=3)

	# Fractal type changed
	def onFractalTypeChanged(self, oldValue, newValue):
		self.fractal.settings.deleteMask()
		if newValue == 'Mandelbrot':
			self.fractal = man.Mandelbrot()
		else:
			self.fractal = jul.Julia()
		self.fractal.settings.createMask(self.gui.controlFrame, startrow=self.fractalRow, padx=2, pady=3)

	# Color palette selected
	def onPaletteChanged(self, oldValue, newValue):
		self.colorSettings.setConfig(col.colorTables[newValue], simple=True)
		self.settings.syncWidget('colorTable')

	# Color palette modified with color editor
	def onColorTableChanged(self, oldValue, newValue):
		paletteName = newValue['name']
		col.colorTables[paletteName] = newValue.getConfig(simple=True)
		# Update dropdown list of color table names
		self.settings.setPar('Fractal selection', 'colorPalette', 'valrange', list(col.colorTables.keys()))
		self.settings.set('colorPalette', paletteName, sync=True)
		self.settings.set('colorTable', newValue, sync=True)

	# Status updates
	def onStatusUpdate(self, statusInfo: dict):
		if 'drawing' in statusInfo:
			self.gui.statusFrame.setFieldValue('drawing', statusInfo['drawing'])
		if 'progress' in statusInfo:
			self.gui.statusFrame.setFieldValue('progress', statusInfo['progress'])
			# self.gui.statusFrame.setProgress(statusInfo['progress'])
		if 'update' not in statusInfo or statusInfo['update'] == True:
			self.gui.mainWindow.update()
