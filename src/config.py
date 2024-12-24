import os
from dataclasses import dataclass
import argparse
from loguru import logger
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', default=False, action='store_true', help="enable debug")
parser.add_argument('-p', '--path', default="/tmp/qubes-forward.db", help="path to database file")
args = parser.parse_args()

logger.remove()

mylogger = logger
mylogger.add(sys.stdout, level="DEBUG")
mylogger.add(sys.stdout, level="WARNING")
mylogger.add(sys.stdout, level="INFO")
if args.debug:
    mylogger.add(sys.stdout, level="ERROR")


@dataclass
class Config:
    dev: bool = True if os.environ.get('QUBES_FORWARD_GUI_DEV', False) != False else False
    debug: bool = args.debug
    db_path: str = args.path
    logger = mylogger

config = Config()