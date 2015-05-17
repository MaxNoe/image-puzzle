import sys
from cx_Freeze import setup, Executable

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == 'win32':
    base = 'Win32GUI'


puzzle = Executable(
	'puzzle.py',
	base=base,
	compress=True,
	icon='icon.ico',
	shortcutName="Image Puzzle",
	shortcutDir="DesktopFolder",
)


setup(
	name = 'image-puzzle',
	version = '0.1',
	author = 'Maximilian Nöthe',
	description = 'Image Puzzles: See your images uncoverd bit by bit',
	executables = [puzzle, ],
	options = {'build_exe': {'include_files':'icon.ico'}}
)
