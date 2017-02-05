"""
"""
from __future__ import print_function, division

import declarative
from BGSF import optics
from BGSF import base
from BGSF import signals
from BGSF import system
from BGSF import readouts
from BGSF.models.LIGO import ligo_sled


def test_LIGO_basic():
    sys = system.BGSystem(
        freq_order_max_default = 1,
    )
    sys.my.det = ligo_sled.LIGOBasicOperation()
    sys.solution


if __name__ == '__main__':
    test_LIGO_basic()
