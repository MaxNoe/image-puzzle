#!/usr/bin/env python
"""
A small python script for an image puzzle, the images are
hidden under some rectangles which are then removed one after another

Usage:
    puzzle [options]

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
    import tkMessageBox as mbox
else:
    import tkinter as tk
    from tkinter import messagebox as mbox
    from tkinter import filedialog as fdiag

from PIL import ImageTk, Image

from time import sleep
from docopt import docopt

class ImagePuzzle:
    def __init__(self,
                 n_tiles_x=16,
                 n_tiles_y=9,
                 time=0.3,
                 dualmonitor=False,
                 colorcycle=['black'],
                 ):


        self.tk = tk.Tk()
        self.tk.title('Image Puzzle')
        self.tk.attributes('-zoomed', True)

        self.image_path = fdiag.askdirectory(
            mustexist=True,
            title='Choose your Image Directory'
        )
        if not self.image_path:
            message='"{}" is not a proper directory'.format(self.image_path)
            mbox.showerror(title='Input Error', message=message)
            raise IOError(message)


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

        self.colorcycle = colorcycle
        self.time = time
        self.blackscreen = Image.new(mode='RGB', size=(1920, 1080), color='black')
        self.fullscreen = False
        self.paused = True
        self.image_index = 0
        self.rectangle_index = 0

        # Load images
        self.images = self.get_images()

        # instantiate image
        image = Image.open(self.images[0])
        image = self.resize_keep_aspect(image)
        self.image = ImageTk.PhotoImage(image=self.blackscreen)
        self.canvas.create_image([self.width//2, self.height//2], image=self.image)
        self.image.paste(image)

        # setup the tiles
        self.rectangles = []
        i = 0
        for x1, x2 in zip(self.xedges[:-1], self.xedges[1:]):
            for y1, y2 in zip(self.yedges[:-1], self.yedges[1:]):
                color = colorcycle[i % len(colorcycle)]
                i += 1
                self.rectangles.append(
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2,
                        state=tk.NORMAL,
                        fill=color,
                        outline='',
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
        if not self.paused:
            if self.rectangle_index < len(self.rectangles):
                self.canvas.itemconfig(
                    self.rectangles[self.rectangle_index],
                    state=tk.HIDDEN,
                )
                sleep(self.time)
                self.tk.update()
                self.rectangle_index += 1
                self.tk.after(int(self.time*1000), self.remove_tile)
            else:
                self.tk.bind("<Button-1>", self.next_image)

    def toggle_fullscreen(self, event=None):
        if self.fullscreen:
            self.end_fullscreen()
        else:
            self.start_fullscreen()

    def start_fullscreen(self, event=None):
        self.tk.config(cursor="none")
        self.tk.attributes("-fullscreen", True)
        self.fullscreen = True

    def end_fullscreen(self, event=None):
        self.tk.config(cursor="arrow")
        self.tk.attributes("-fullscreen", False)
        self.fullscreen = False

    def next_image(self, event=None):
        self.rectangle_index = 0
        shuffle(self.rectangles)
        self.paused = True
        for rectangle in self.rectangles:
            self.canvas.itemconfig(rectangle, state=tk.NORMAL)
        self.tk.update()
        self.image_index = (self.image_index + 1) % len(self.images)
        image = Image.open(self.images[self.image_index])
        image = self.resize_keep_aspect(image)
        self.image.paste(image)
        self.tk.bind("<Button-1>", self.toggle_paused)

    def resize_keep_aspect(self, image):
        width, height = image.size
        ratio = min(self.width / width, self.height / height)
        image = image.resize((int(width * ratio), int(height * ratio)),
                             Image.BICUBIC)
        width, height = image.size
        box=[int(round((self.width - width)/2, 0)),
             int(round((self.height - height)/2, 0)),
             ]
        box.append(box[0]+width)
        box.append(box[1]+height)
        centered_image = self.blackscreen.copy()
        centered_image.paste(
            image,
            box=box,
            )
        return centered_image

    def get_images(self):
        images = []
        for root, dirs, files in os.walk(self.image_path):
            for f in files:
                if f.split('.')[-1].lower() in ('jpg', 'png', 'jpeg'):
                    images.append(path.abspath(path.join(root, f)))
        if not images:
            message = 'No images found in "{}"'.format(self.image_path)
            mbox.showerror('No images found', message)
            raise IOError(message)

        return sorted(images)

if __name__ == '__main__':
    args = docopt(__doc__)

    time = float(args['--time'])
    n_tiles_x = int(args['--n_tiles_x'])
    n_tiles_y = int(args['--n_tiles_y'])

    w = ImagePuzzle(
        time=time,
        n_tiles_x=n_tiles_x,
        n_tiles_y=n_tiles_y,
        dualmonitor=args['--dualmonitor'],
        colorcycle=['black', '#FF6600',],
    )
    w.tk.mainloop()
