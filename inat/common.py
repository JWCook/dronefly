"""Module for common code."""
import logging
import re
from itertools import zip_longest

DEQUOTE = re.compile(r'^"?(.*?)"?$')
LOG = logging.getLogger("red.dronefly.inatcog")


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)
