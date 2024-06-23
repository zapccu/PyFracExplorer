
from tkinter import *


class StatusFrame(Frame):

	fields = []

	def __init__(self, parentWindow: object, width: int, height: int = 50):
		super.__init__(parentWindow, width, height, padx=0, pady=0)

		self.pack_propagate = False
		self.pack(side=BOTTOM, expand=False, fill=NONE, anchor='nw')
	
	# Add field to status bar
	def addField(self, width: int, value: str = "", fg='black', bg='grey'):
		field = Label(self, width=width, text=value, bg=bg)
		field.pack(side=LEFT, expand=False, fill=NONE)
		self.fields.append(field)
	
	def setFieldValue(self, fieldIdx: int, value: str, fg='black', bg='grey'):
		if fieldIdx >= 0 and fieldIdx < len(self.fields):
			self.fields[fieldIdx].config(text=value, fg=fg, bg=bg)
			return True
		else:
			return False
		
class DrawFrame(Frame):

	def __init__(self, parentWindow: object, width: int, height: int, bg='black'):
		super.__init__(parentWindow, width, height, padx=0, pady=0, cursor='CROSS')

		self.pack_propagate(False)
		self.pack(side=LEFT, expand=False, fill=BOTH, anchor='nw')

		# Scrollbars
		self.hScroll = Scrollbar(self.drawFrame, orient='horizontal')
		self.vScroll = Scrollbar(self.drawFrame, orient='vertical')
		self.hScroll.pack(fill=X, side=BOTTOM)
		self.vScroll.pack(fill=Y, side=RIGHT)

		self.canvas = Canvas(self, width=width, height=height, bg=bg, scrollregion=(0, 0, width, height))

		self.hScroll.config(command=self.canvas.xview)
		self.vScroll.config(command=self.canvas.yview)

		self.canvas.config(xscrollcommand=self.hScroll.set, yscrollcommand=self.vScroll.set)
		self.canvas.pack(side=LEFT, expand=False, fill=NONE, anchor='nw')
	
	def setCanvasRes(self, width: int, height: int):
		self.canvas.configure(width=width, height=height, scrollregion=(0, 0, width, height))

class ControlFrame(Frame):

	def __init__(self, parentWindow: object, width: int, height: int, bg='grey'):
		super.__init__(parentWindow, width, height, padx=0, pady=0, cursor='CROSS')

		self.pack_propagate(False)
		self.pack(side=LEFT, expand=False, fill=Y, anchor='nw')
		label1 = Label(self, text="TEST").pack()