
# PyFracExplore main

import sys
from tkinter import *

class Application:

    def __init__(self):
        self.mainWindow = Tk()
        self.mainWindow.title("PyFracExplore")

        # Scrollbars
        hScroll = Scrollbar(self.mainWindow, orient='horizontal')
        hScroll.pack(side = BOTTOM, fill = X)
        vScroll = Scrollbar(self.mainWindow)
        vScroll.pack(side = RIGHT, fill = Y)

        # Main frame
        self.drawFrame = Frame(self.mainWindow, width=400, height=400)
        self.drawFrame.pack(side = TOP)

        # hScroll.config(command = self.drawFrame.xview)
        # vScroll.config(command = self.drawFrame.yview)

    def run(self):
        self.mainWindow.mainloop()

def main():
    app = Application()
    app.run()

if __name__ == "__main__":
    sys.exit(main())