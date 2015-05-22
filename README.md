# image-puzzle

A little program to show an image puzzle

## Usage

### General

1. Put the images you want to be part of the puzzle into one directory

2. Start the program and select the proper options:

  * Select the number of tiles, if you choose it proportional to the aspect ratio
    of the display the tiles will be squares (default is 16:9)

  * Select the time between the removal of two tiles (default is 0.2 seconds)

  * select the directory with your images

  * Select the color of the tiles, you can give a comma seperated list of
    colors, either string or hexcodes.

  * If you are using X11 (Linux) and have a dual monitor setup check the box
    so that the program can get the correct screen resolution via xrandr.

3. Start the presentation with `Ok.`

## Key bindings:

* `<Right>`: Main Control.
  * Play if all tiles are still visible
  * Remove all tiles if presentation has started
  * Next image if all tiles are gone

* Left Mouse Button: Play/Pause and next image if all tiles are removed

* `<F5>` and `<F11>`: toggle fullscreen mode

* `<Escape>`: Leave fullscreen mode


* `<Left>`  Last image
