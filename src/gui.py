
from tkinter import *



class StatusFrame(Frame):

	fields = []

	def __init__(self, parentWindow: object, width: int, height: int = 50):
		super().__init__(parentWindow, width=width, height=height, padx=0, pady=0, bg='grey')

		self.parentWindow = parentWindow

		self.pack_propagate = False
		self.pack(side=BOTTOM, expand=False, fill=X, anchor='nw')
	
	# Add field to status bar
	def addField(self, hSize: int, value: str = "", fg='black', bg='grey'):
		field = Label(self, width=hSize, text=value, bg=bg, relief=SUNKEN)
		field.pack_propagate(False)
		field.pack(side=LEFT, expand=False, fill=NONE, anchor="w", padx=2, pady=2)
		self.fields.append(field)
	
	def setFieldValue(self, fieldIdx: int, value: str, fg='black', bg='grey'):
		if fieldIdx >= 0 and fieldIdx < len(self.fields):
			self.fields[fieldIdx].config(text=value, fg=fg, bg=bg)
			return True
		else:
			return False
		
class DrawFrame(Frame):

	def __init__(self, parentWindow: object, width: int, height: int, bg='black'):
		super().__init__(parentWindow, width=width, height=height, padx=0, pady=0, cursor='cross')

		self.parentWindow = parentWindow

		self.pack_propagate(False)
		self.pack(side=LEFT, expand=False, fill=BOTH, anchor='nw')

		# Scrollbars
		self.hScroll = Scrollbar(self, orient='horizontal')
		self.vScroll = Scrollbar(self, orient='vertical')
		self.hScroll.pack(fill=X, side=BOTTOM)
		self.vScroll.pack(fill=Y, side=RIGHT)

		self.canvas = Canvas(self, width=canvasWidth, height=canvasHeight, bg=bg, scrollregion=(0, 0, width, height))
		self.canvasWidth = width
		self.canvasHeight = height

		self.hScroll.config(command=self.canvas.xview)
		self.vScroll.config(command=self.canvas.yview)

		self.canvas.config(xscrollcommand=self.hScroll.set, yscrollcommand=self.vScroll.set)
		self.canvas.pack(side=LEFT, expand=False, fill=NONE, anchor='nw')
	
	def setCanvasRes(self, width: int, height: int):
		self.canvas.configure(width=width, height=height, scrollregion=(0, 0, width, height))
		self.canvasWidth = width
		self.canvasHeight = height

class ControlFrame(Frame):

	def __init__(self, parentWindow: object, width: int, height: int, bg='grey'):
		super().__init__(parentWindow, width=width, height=height, padx=0, pady=0, bg='blue')

		self.parentWindow = parentWindow

		self.pack_propagate(False)
		self.pack(side=LEFT, expand=False, fill=Y, anchor='nw')
		label1 = Label(self, text="TEST").pack()