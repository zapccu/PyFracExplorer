
from tkinter import *
from tkinter import colorchooser
from tkinter.scrolledtext import ScrolledText


class ColorEditor:

	def __init__(self, mainWindow):
		self.dlg = Toplevel(mainWindow)
		self.dlg.geometry("750x250")
		self.dlg.title("Color Editor")

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
