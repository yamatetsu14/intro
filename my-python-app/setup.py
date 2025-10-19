from setuptools import setup

APP = ['othello_gui.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'Resources/icon.icns',
    'packages': ['tkinter'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)