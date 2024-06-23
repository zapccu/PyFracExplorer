
# PyFracExplore main

import sys
from tkinter import *
from gui import *
from graphics import *
from fractal import *

class Application:

	width = 800
	height = 800

	def __init__(self, width: int, height: int, title: str):
		self.width = width
		self.height = height

		# Main window
		self.mainWindow = Tk()
		self.mainWindow.title(title)
		self.mainWindow.geometry(f"{width}x{height}")

		# GUI sections
		self.statusFrame = StatusFrame(self.mainWindow, 1000, 50)
		self.drawFrame = DrawFrame(self.mainWindow, 800, 750, 800, 800, bg='white')
		self.controlFrame = ControlFrame(self.mainWindow, 200, 750)
		self.statusFrame.addField(10, value="Status")
		self.statusFrame.addField(10, value="TEXT")

		# Initialize graphics
		self.graphics = Graphics(self.drawFrame, flipY=True)

	def run(self):
		palette = ColorTable()
		palette.createLinearTable(100, Color(0, 0, 0), Color(255, 255, 255))
		self.graphics.setColorTable(palette)

		# self.graphics.drawPalette()
		self.mainWindow.update()

		frc = Mandelbrot(800, 800, complex(-2.0, -1.5), complex(3.0, 3.0))
		self.graphics.drawLineByLine(frc)

		self.mainWindow.mainloop()

def main():
	app = Application(1000, 800, "PyFracExplore")
	app.run()

if __name__ == "__main__":
	sys.exit(main())