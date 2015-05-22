#!/usr/bin/env python
"""
A small python script for an image puzzle, the images are
hidden under tiles which are then removed one after another
"""

import sys
import os
from os import path
import subprocess as sp

from random import shuffle

if sys.version_info[0] == 2:
    import Tkinter as tk
    import tkMessageBox as mbox
    import tkFont as font
else:
    import tkinter as tk
    from tkinter import messagebox as mbox
    from tkinter import filedialog as fdiag
    from tkinter import font
    from tkinter import ttk

from PIL import ImageTk, Image

from time import sleep

def makeentry(parent, caption, width=None, default=None, **options):
    ttk.Label(parent, text=caption).pack(side=tk.LEFT, padx=1)
    var = tk.StringVar(value=default)
    entry = ttk.Entry(parent, textvariable=var, **options)
    if width:
        entry.config(width=width)
    entry.pack(side=tk.LEFT, padx=1)
    return entry, var

class OptionsWindow:
    def __init__(self):
        self.tk = tk.Tk()
        self.tk.title('Options')

        frame1 = ttk.Frame(self.tk)
        frame1.pack(side=tk.TOP, padx=2, pady=2)

        button_frame = ttk.Frame(self.tk)
        button_frame.pack(side=tk.BOTTOM, padx=2, pady=2)

        self.xtiles_box, self.xtiles = makeentry(
            frame1, caption='Number of Tiles  X:', width=3, default=16,
            justify=tk.RIGHT,
        )
        self.ytiles_box, self.ytiles = makeentry(
            frame1, caption=' Y:', width=3, default=9, justify=tk.RIGHT,
        )

        frame2 = ttk.Frame(self.tk)
        frame2.pack(side=tk.TOP, padx=2, pady=2)
        self.time_box, self.time = makeentry(
            frame2, caption='removal interval / seconds', default=0.2, width=4,
            justify=tk.RIGHT,
        )

        frame3 = ttk.Frame(self.tk)
        frame3.pack(side=tk.TOP, padx=2, pady=2)
        self.image_path_box, self.image_path = makeentry(
            frame3, caption='Image Directory', default=os.getcwd(),
        )
        self.browse_button = ttk.Button(
            frame3, text='Browse ...', command=self.set_image_path,
        )
        self.browse_button.pack(side=tk.BOTTOM)

        frame4 = ttk.Frame(self.tk)
        frame4.pack(side=tk.TOP, padx=2, pady=2)
        self.color_cycle_box, self.color_cycle = makeentry(
            frame4, caption='color cycle, names or hexcodes', default='black,red'
        )

        frame5 = ttk.Frame(self.tk)
        frame5.pack(side=tk.TOP, padx=2, pady=2)
        self.dualmonitor = tk.BooleanVar(value=False)
        self.dualmonitor_box = ttk.Checkbutton(
            frame5, text='dualmonitor (linux only)', variable=self.dualmonitor,
        )
        self.dualmonitor_box.pack(side=tk.LEFT)


        self.ok_button = ttk.Button(button_frame, text='Ok',
                                    command=self.save_close)
        self.ok_button.pack(side=tk.LEFT)
        self.cancel_button = ttk.Button(
            button_frame, text='Cancel', command=self.close,
        )
        self.cancel_button.pack(side=tk.LEFT)
        self.tk.mainloop()

    def set_image_path(self):
        image_path = fdiag.askdirectory(
            mustexist=True,
            title='Choose your Image Directory'
        )
        if image_path:
            self.image_path.set(image_path)

    def save_close(self):
        settings = {}
        settings['n_tiles_x'] = int(self.xtiles.get())
        settings['n_tiles_y'] = int(self.ytiles.get())
        settings['time'] = float(self.time.get())
        settings['image_path'] = self.image_path.get()
        settings['dualmonitor'] = self.dualmonitor.get()
        settings['colorcycle'] =self.color_cycle.get().split(',')

        self.settings = settings
        self.tk.destroy()

    def close(self):
        self.tk.destroy()
        sys.exit()


class ImagePuzzle:
    def __init__(self,
                 n_tiles_x=16,
                 n_tiles_y=9,
                 time=0.2,
                 colorcycle=['black', 'red'],
                 image_path='.',
                 dualmonitor=False,
                 ):
        tiles_x = n_tiles_x
        tiles_y = n_tiles_y
        self.time = time
        colorcycle = colorcycle
        self.image_path = image_path
        dualmonitor = dualmonitor

        self.tk = tk.Tk()
        self.tk.title('Image Puzzle')

        if not path.exists(self.image_path):
            message='"{}" is not a proper directory'.format(self.image_path)
            mbox.showerror(title='Input Error', message=message)
            raise IOError(message)

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

        xedges = [int(i * self.width / tiles_x) for i in range(tiles_x + 1)]
        yedges = [int(i * self.height / tiles_y) for i in range(tiles_y + 1)]

        self.blackscreen = Image.new(mode='RGB', size=(self.width, self.height), color='black')
        self.fullscreen = False
        self.paused = True
        self.image_index = 0
        self.rectangle_index = 0

        # Load images
        self.images = self.get_images()

        # instantiate image
        image = Image.open(self.images[0])
        image = self.resize_keep_aspect(image)
        self.image = ImageTk.PhotoImage(master=self.canvas,
                                        image=self.blackscreen)
        self.canvas.create_image([self.width//2, self.height//2],
                                 image=self.image,
                                 )
        self.image.paste(image)

        # setup the tiles
        self.rectangles = []
        i = 0
        for x1, x2 in zip(xedges[:-1], xedges[1:]):
            for y1, y2 in zip(yedges[:-1], yedges[1:]):
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
        self.tk.bind("<Right>", self.toggle_paused)
        self.tk.bind("<Left>", self.last_image)

    def toggle_paused(self, event=None):
        self.paused = not self.paused
        if not self.paused:
            self.remove_tile()
        self.tk.bind("<Right>", self.remove_all_tiles)

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

    def remove_all_tiles(self, event=None):
        self.paused = True
        for rectangle in self.rectangles:
            self.canvas.itemconfig(rectangle, state=tk.HIDDEN)
        self.tk.update()
        self.tk.bind('<Right>', self.next_image)

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
        self.tk.bind("<Right>", self.toggle_paused)

    def last_image(self, event=None):
        self.rectangle_index = 0
        shuffle(self.rectangles)
        self.paused = True
        for rectangle in self.rectangles:
            self.canvas.itemconfig(rectangle, state=tk.NORMAL)
        self.tk.update()
        self.image_index = (len(self.images) + self.image_index - 1) % len(self.images)
        image = Image.open(self.images[self.image_index])
        image = self.resize_keep_aspect(image)
        self.image.paste(image)
        self.tk.bind("<Button-1>", self.toggle_paused)
        self.tk.bind("<Right>", self.toggle_paused)

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
    o = OptionsWindow()
    settings = o.settings

    w = ImagePuzzle(**settings)
    w.tk.mainloop()
