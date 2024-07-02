
from tkinter import *

class StatusFrame(Frame):

	def __init__(self, app: object, width: int, height: int = 50):
		super().__init__(app.mainWindow, width=width, height=height, padx=0, pady=0, bg='grey')

		self.app = app
		self.field = {}

		self.pack_propagate = False
		self.pack(side=BOTTOM, expand=False, fill=X, anchor='nw')
	
	# Add field to status bar
	def addField(self, name: str, hSize: int, value: str = "", fg='black', bg='grey'):
		field = Label(self, width=hSize, text=value, bg=bg, relief=SUNKEN)
		field.pack_propagate(False)
		field.pack(side=LEFT, expand=False, fill=NONE, anchor="w", padx=2, pady=2)
		self.field[name] = field
	
	def setFieldValue(self, name: str, value: str, fg='black', bg='grey'):
		if name not in self.field:
			return False
		else:
			self.field[name].config(text=value, fg=fg, bg=bg)
			return True
		
class DrawFrame(Frame):

	def __init__(self, app: object, width: int, height: int, bg='black'):
		super().__init__(app.mainWindow, width=width, height=height, padx=0, pady=0, cursor='cross')

		self.app = app

		self.pack_propagate(False)
		self.pack(side=LEFT, expand=False, fill=BOTH, anchor='nw')

		# Scrollbars
		self.hScroll = Scrollbar(self, orient='horizontal')
		self.vScroll = Scrollbar(self, orient='vertical')
		self.hScroll.pack(fill=X, side=BOTTOM)
		self.vScroll.pack(fill=Y, side=RIGHT)

		self.canvas = Canvas(self, width=width, height=height, bg=bg, bd=0, scrollregion=(0, 0, width, height))
		self.canvasWidth = width
		self.canvasHeight = height

		self.hScroll.config(command=self.canvas.xview)
		self.vScroll.config(command=self.canvas.yview)

		self.canvas.config(xscrollcommand=self.hScroll.set, yscrollcommand=self.vScroll.set)
		self.canvas.pack(side=LEFT, expand=False, fill=NONE, anchor='nw')

		# Event handler
		self.canvas.bind('<Motion>', self.app.onMove)
		self.canvas.bind('<ButtonPress-1>', self.app.onButtonPressed)
		self.canvas.bind('<B1-Motion>', self.app.onDrag)
		self.canvas.bind('<ButtonRelease-1>', self.app.onButtonReleased)

	def setCanvasRes(self, width: int, height: int):
		if width != self.canvasWidth or height != self.canvasHeight:
			self.canvas.configure(width=width, height=height, scrollregion=(0, 0, width, height))
			self.canvasWidth = width
			self.canvasHeight = height

class ControlFrame(Frame):

	def __init__(self, app: object, width: int, height: int, bg='grey'):
		super().__init__(app.mainWindow, width=width, height=height, padx=0, pady=0, bg='blue')

		self.app = app

		self.pack_propagate(False)
		self.pack(side=LEFT, expand=False, fill=Y, anchor='nw')

		self.btnDraw = Button(
            self,
            text="Draw",
            width=8,
            fg="green",
            command=lambda: self.app.onDraw(),
        ).pack()
