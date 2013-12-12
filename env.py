import os.path
import sys

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path += [BASE_PATH, os.path.join(BASE_PATH, 'vendors')]

from IPython.core import ultratb
import subprocess


def exceptionhook(type, value, traceback):
    subprocess.Popen(
        ['notify-send', "-i",
         "/usr/share/icons/gnome/scalable/emotes/face-devilish.svg",
         "python exception"]
    )
    ultratb.FormattedTB(mode='Verbose', color_scheme='Linux', call_pdb=1)(
        type, value, traceback)

sys.excepthook = exceptionhook
