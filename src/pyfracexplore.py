
# PyFracExplore main

import sys
from tkinter import *

class Application:

    def __init__(self):
        self.mainWindow = Tk()
        self.mainWindow.title("PyFracExplore")

        # Container frame
        self.container = Frame(self.mainWindow, width=400, height=400)
        self.container.pack(expand=True, fill=BOTH)

        # Canvas
        self.canvas = Canvas(self.container, width=400, height=400, bg='black',
                             scrollregion=(0, 0, 800, 800))

        # Scrollbars
        hScroll = Scrollbar(self.container, orient='horizontal')
        vScroll = Scrollbar(self.container, orient='vertical')
        hScroll.pack(fill=X, side=BOTTOM)
        vScroll.pack(fill=Y, side=RIGHT)
        hScroll.config(command=self.canvas.xview)
        vScroll.config(command=self.canvas.yview)

        self.canvas.config(xscrollcommand=hScroll.set, yscrollcommand=vScroll.set)
        self.canvas.pack(side=LEFT, expand=True, fill=BOTH)

        # self.canvas.create_line((0, 0), (799, 799), fill='green', width=1)

    def run(self):
        self.mainWindow.mainloop()

def main():
    app = Application()
    app.run()

if __name__ == "__main__":
    sys.exit(main())