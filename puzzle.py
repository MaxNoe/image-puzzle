"""
A small python script for an image puzzle, the images are
hidden under some rectangles which are then removed one after another

Usage:
    puzzle <imagepath> [options]

Options:
    -t <seconds>, --time=<seconds>  time between removal of tiles [default: 0.3]
    -x <N>, --n_tiles_x=<N>         number of tiles in x direction [default: 16]
    -y <N>, --n_tiles_y=<N>         number of tiles in y direction [default: 9]
    --dualmonitor                   Use xrandr tou get correct monitor resolution
                                    in a dualmonitor setup
"""
import sys
import os
from os import path
import subprocess as sp

from random import shuffle

if sys.version_info[0] == 2:
    import Tkinter as tk
else:
    import tkinter as tk

from PIL import ImageTk, Image

from time import sleep
from docopt import docopt

class ImagePuzzle:
    def __init__(self,
                 image_path,
                 n_tiles_x=16,
                 n_tiles_y=9,
                 time=0.3,
                 dualmonitor=False,
                 ):

        self.tk = tk.Tk()
        self.tk.title('Image Puzzle')
        self.tk.attributes('-zoomed', True)

        # if dualmonitor on linux:
        if dualmonitor:
            xrandr_output = sp.check_output("xrandr | grep \* | cut -d' ' -f4",
                                            shell=True)
            xrandr_output = xrandr_output.splitlines()[0].decode('UTF-8')

            self.width = int(xrandr_output.split("x")[0])
            self.height = int(xrandr_output.split("x")[1])
        else:
            self.width = self.tk.winfo_screenwidth()
            self.height = self.tk.winfo_screenheight()

        self.canvas = tk.Canvas(self.tk, width=self.width, height=self.height)
        # borderless
        self.canvas.config(highlightthickness=0)

        self.xedges = [int(i * self.width / n_tiles_x) for i in range(n_tiles_x+1)]
        self.yedges = [int(i * self.height / n_tiles_y) for i in range(n_tiles_y+1)]

        self.time = time
        self.image_path = image_path
        self.fullscreen = False
        self.paused = True
        self.image_index = 0
        self.rectangle_index = 0

        # Load images
        self.images = self.get_images()

        # instantiate image
        self.image = ImageTk.PhotoImage(image=Image.open(self.images[0]))
        self.canvas.create_image([0, 0], anchor=tk.NW, image=self.image)

        self.rectangles = []

        for x1, x2 in zip(self.xedges[:-1], self.xedges[1:]):
            for y1, y2 in zip(self.yedges[:-1], self.yedges[1:]):
                self.rectangles.append(
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        fill='black',
                        state=tk.NORMAL,
                    )
                )
        shuffle(self.rectangles)
        self.canvas.pack(fill=tk.BOTH, expand=1)

        # Key Bindings
        self.tk.bind("<F11>", self.toggle_fullscreen)
        self.tk.bind("<F5>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)
        self.tk.bind("<Button-1>", self.toggle_paused)
        self.tk.bind("<Right>", self.next_image)

    def toggle_paused(self, event=None):
        self.paused = not self.paused
        if not self.paused:
            self.remove_tile()

    def remove_tile(self, event=None):
        if not self.paused and self.rectangle_index < len(self.rectangles):
            self.canvas.itemconfig(self.rectangles[self.rectangle_index],
                                   state=tk.HIDDEN)
            sleep(self.time)
            self.tk.update()
            self.rectangle_index += 1
        if self.rectangle_index < len(self.rectangles):
            self.tk.after(int(self.time*1000), self.remove_tile)

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.tk.attributes("-fullscreen", self.fullscreen)

    def end_fullscreen(self, event=None):
        self.fullscreen = False
        self.tk.attributes("-fullscreen", False)

    def next_image(self, event=None):
        shuffle(self.rectangles)
        self.rectangle_index = 0
        self.paused = True
        for rectangle in self.rectangles:
            self.canvas.itemconfig(rectangle, state=tk.NORMAL)
        self.tk.update()
        self.image_index = (self.image_index + 1) % len(self.images)
        self.image.paste(Image.open(self.images[self.image_index]))

    def get_images(self):
        images = []
        for root, dirs, files in os.walk(self.image_path):
            for f in files:
                if f.split('.')[-1].lower() in ('jpg', 'png', 'jpeg'):
                    images.append(path.join(root, f))
        return sorted(images)

if __name__ == '__main__':
    args = docopt(__doc__)

    time = float(args['--time'])
    n_tiles_x = int(args['--n_tiles_x'])
    n_tiles_y = int(args['--n_tiles_y'])

    w = ImagePuzzle(
        args['<imagepath>'],
        time=time,
        n_tiles_x=n_tiles_x,
        n_tiles_y=n_tiles_y,
        dualmonitor=args['--dualmonitor']
    )
    w.tk.mainloop()
