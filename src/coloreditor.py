
from tkinter import *
from tkinter import colorchooser
from tkinter.scrolledtext import ScrolledText

import tkconfigure as tkc
import colors as col

defaultPaletteDef = {
	"Grey": {
		"type": "Linear",
		"size": 4096,
		"par": {
			"colorPoints": [(80/255, 80/255, 80/255), (1., 1., 1.)]
		}
	},
	"Sinus": {
		"type": "Sinus",
		"size": 4096,
		"par": {
			"thetas": [.85, .0, .15]
		}
	}
}

class ColorEditor:

	def __init__(self, mainWindow, width: int, height: int, palettename: str = 'Grey', palettedef: dict = defaultPaletteDef['Grey']):
		self.paletteDef = palettedef
		self.orgPaletteDef = palettedef
		self.orgPaletteName = palettename

		self.masterSettings = tkc.TKConfigure({
			"Palette": {
				'paletteName': {
					'inputtype': 'str',
					'initvalue': palettename,
					'widget':    'TKCEntry',
					'label':     'Palette name',
					'width':     15
				},
				'paletteType': {
					'inputtype': 'str',
					'valrange':  ['Linear', 'Sinus'],
					'initvalue': palettedef['type'],
					'widget':    'TKCListbox',
					'label':     'Palette type',
					'width':     20,
					'notify':    self.onPaletteTypeChanged
				},
				'paletteSize': {
					'inputtype': 'int',
					'valrange':  (1, 4096),
					'initvalue': palettedef['size'],
					'label':     'Entries',
					'widget':    'TKCSpinbox',
					'width':     8
				},
				'defaultColor': {
					'inputtype': 'str',
					'valrange':  ('^#([0-9a-fA-F]{2}){3}$',),
					'initvalue': '#000000',
					'label':     'Default color',
					'widget':    'TKCColor',
					'width':     80
				},
				'colorTable': {
					'inputtype': 'list',
					'initvalue': col.createPaletteFromDef(palettedef).tolist(),
					'widget':    'TKCColortable',
					'width':     width-20
				}
			}
		})

		self.typeSettings = self.paletteTypeSettings(palettedef)

		self.width      = width
		self.height     = height
		self.mainWindow = mainWindow
		self.apply      = False

	# Show color editor
	def show(self, palettename: str | None = None, palettedef: dict | None = None) -> bool:
		# Create the window
		self.dlg = Toplevel(self.mainWindow)
		self.dlg.geometry(f"{self.width}x{self.height}")
		self.dlg.title("Color Editor")

		if palettename is not None and palettedef is not None:
			self.paletteDef = palettedef
			self.orgPaletteDef = palettedef
			self.orgPaletteName = palettename
			colorTable = col.createPaletteFromDef(palettedef).tolist()
			self.masterSettings.setValues(
				spaletteName=palettename,
				paletteType=palettedef['type'],
				paletteSize=palettedef['size'],
				colorTable=colorTable
			)
			self.typeSettings = self.paletteTypeSettings(palettedef)

		# Create widgets
		self.tsrow = self.masterSettings.createMask(self.dlg, padx=3, pady=5)
		self.btnrow = self.typeSettings.createMask(self.dlg, startrow=self.tsrow, padx=3, pady=5)

		# Buttons
		self.btnOk     = Button(self.dlg, text="Ok", command=lambda: self.setApply(True))
		self.btnCancel = Button(self.dlg, text="Cancel", command=lambda: self.setApply(False))
		self.btnReset  = Button(self.dlg, text="Reset", command=lambda: self.onReset())
		self.btnOk.grid(column=0, row=self.btnrow)
		self.btnCancel.grid(column=1, row=self.btnrow)
		self.btnReset.grid(column=3, row=self.btnrow)

		self.dlg.wait_window()

		return self.apply

		"""
		self.colorPoints = Frame(self.dlg, width=500, height=50)
		self.colorPoints.place(x=10, y=20)

		# Scrollbars
		self.hScroll = Scrollbar(self.colorPoints, orient='horizontal')
		self.hScroll.pack(fill=X, side=BOTTOM)

		# Create drawing canvas and link with scrollbars
		self.canvas = Canvas(self.colorPoints, width=600, height=50, bg='black', bd=0, highlightthickness=0, scrollregion=(0, 0, 600, 50))
		self.hScroll.config(command=self.canvas.xview)
		self.canvas.config(xscrollcommand=self.hScroll.set)
		self.canvas.pack(side=LEFT, expand=False, fill=NONE, anchor='nw')
		"""

	# Create palette type specific settings
	def paletteTypeSettings(self, palettedef: dict):
		if palettedef['type'] == 'Linear':
			colorSettings = { 'Color points': {} }
			for n, cp in enumerate(palettedef['par']['colorPoints'], start=0):
				colorSettings['Color points']['point' + str(n)] = {
					'inputtype': 'str',
					'initvalue': '#{:02X}{:02X}{:02X}'.format(int(cp[0]*255), int(cp[1]*255), int(cp[2]*255)),
					'label':     'point ' + str(n),
					'widget':    'TKCColor',
					'width':     80,
					'notify':    self.onPointChanged
				}
			return tkc.TKConfigure(colorSettings)
		
		elif palettedef['type'] == 'Sinus':
			colorSettings = { 'Thetas': {} }
			for n, t in enumerate(palettedef['par']['thetas'], start=1):
				colorSettings['Thetas']['theta' + str(n)] = {
					'inputtype': 'float',
					'valrange':  (0, 1, 0.01),
					'initvalue': t,
					'label':     'theta ' + str(n),
					'widget':    'TKCSlider',
					'width':     120,
					'notify':    self.onThetaChanged
				}
			return tkc.TKConfigure(colorSettings)
	
	def onPaletteTypeChanged(self, oldValue, newValue):
		print(f"palette type change from {oldValue} to {newValue}")
		paletteDef = defaultPaletteDef[newValue]
		colortable = col.createPaletteFromDef(paletteDef).tolist()
		self.typeSettings.deleteMask()
		self.typeSettings = self.paletteTypeSettings(paletteDef)
		self.masterSettings.setValues(colorTable=colortable, sync=True)
		self.btnrow = self.typeSettings.createMask(self.dlg, startrow=self.tsrow, padx=3, pady=5)

	def onPointChanged(self, oldValue, newValue):
		nPoints = len(self.paletteDef['par']['colorPoints'])
		pList = [ 'point' + str(i) for i in range(nPoints) ]
		colorPoints = self.typeSettings.getValues(pList)
		rgbPoints = [ tuple(int(cp[i:i+2], 16) / 255 for i in (1, 3, 5)) for cp in colorPoints ]
		colorTable = col.createPaletteFromDef({
			"type": self.paletteDef['type'],
			"size": self.masterSettings['paletteSize'],
			"par": {
				"colorPoints": rgbPoints
			}
		}).tolist()
		self.masterSettings.set('colorTable', colorTable, sync=True)

	def onThetaChanged(self, oldValue, newValue):
		thetas = [ self.typeSettings['theta1'], self.typeSettings['theta2'], self.typeSettings['theta3'] ]
		colorTable = col.createPaletteFromDef({
			"type": "Sinus",
			"size": self.masterSettings['paletteSize'],
			"par": {
				"thetas": thetas
			}
		}).tolist()
		self.masterSettings.set('colorTable', colorTable, sync=True)

	def setApply(self, apply: bool):
		self.apply = apply
		self.dlg.destroy()

	def onReset(self):
		paletteDef = self.orgPaletteDef
		colortable = col.createPaletteFromDef(paletteDef).tolist()
		self.typeSettings.deleteMask()
		self.typeSettings = self.paletteTypeSettings(paletteDef)
		self.masterSettings.setValues(paletteName=self.orgPaletteName, paletteSize=paletteDef['size'], colorTable=colortable, sync=True)
		self.btnrow = self.typeSettings.createMask(self.dlg, startrow=self.tsrow, padx=3, pady=5)
