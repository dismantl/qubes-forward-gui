import sys
sys.path.append('lib')
import PyQt6.QtWidgets as widgets
from peewee import *
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor
import re
import os
from dataclasses import dataclass
from argparse import ArgumentParser
from loguru import logger
from sys import stdout
from subprocess import Popen, PIPE
from os import popen

from main import main

if __name__ == '__main__':
    main()