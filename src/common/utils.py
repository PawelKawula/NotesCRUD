import os, sys

from .constants import SRC_PATH

def add_source_path():
    SOURCE_PATH = os.path.join(SRC_PATH)
    sys.path.append(SOURCE_PATH)
