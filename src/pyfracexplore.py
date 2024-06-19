
# PyFracExplore main

import sys
from tkinter import *
from graphics import *
from fractal import *

class Application:

	width = 800
	height = 800

	def __init__(self, width = 800, height = 800):
		self.width = width
		self.height = height
		self.mainWindow = Tk()
		self.mainWindow.title("PyFracExplore")
		self.mainWindow.geometry(f"{width}x{height}")

		# Container frame
		self.container = Frame(self.mainWindow, width=self.width/2, height=self.height/2)
		self.container.pack(expand=True, fill=BOTH)

		# Canvas
		self.canvas = Canvas(self.container, width=self.width/2, height=self.height/2, bg='black',
							 scrollregion=(0, 0, self.width, self.height))

		# Scrollbars
		hScroll = Scrollbar(self.container, orient='horizontal')
		vScroll = Scrollbar(self.container, orient='vertical')
		hScroll.pack(fill=X, side=BOTTOM)
		vScroll.pack(fill=Y, side=RIGHT)
		hScroll.config(command=self.canvas.xview)
		vScroll.config(command=self.canvas.yview)

		self.canvas.config(xscrollcommand=hScroll.set, yscrollcommand=vScroll.set)
		self.canvas.pack(side=LEFT, expand=True, fill=BOTH)

		self.graphics = Graphics(self.canvas, self.width, self.height, flipY = True)

	def run(self):
		palette = ColorTable()
		palette.createLinearTable(100, Color(0, 0, 0), Color(255, 255, 255))

		self.graphics.setColorTable(palette)

		# self.graphics.drawPalette()

		print("Start")
		frc = Mandelbrot(800, 800, complex(-1.5, -1.5), complex(3.0, 3.0))
		self.graphics.drawLineByLine(frc)
		print("End")

		self.mainWindow.mainloop()

def main():
	app = Application(800, 800)
	app.run()

if __name__ == "__main__":
	sys.exit(main())