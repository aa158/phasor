"""
"""

from __future__ import (division, print_function)
import pytest

import numpy as np
from declarative import Bunch

import BGSF.optics as optics
import BGSF.readouts as readouts

from BGSF.system.optical import (
    OpticalSystem
)

import unittest
assertions = unittest.TestCase('__init__')


#from BGSF.utilities.np import logspaced

def gensys():
    sys = OpticalSystem(
    )
    sled = sys.sled
    sled.my.laser = optics.Laser(
        F = sys.F_carrier_1064,
        power_W = 1.,
    )

    sled.my.etmPD = optics.MagicPD()

    sys.bond_sequence(
        sled.laser.Fr,
        sled.etmPD.Fr,
    )

    sled.my.etm_DC = readouts.DCReadout(port = sled.etmPD.Wpd.o)
    #sys.AC_freq(np.array([1]))
    return Bunch(locals())


def gensys_full():
    sys = OpticalSystem(
    )
    sled = sys.sled
    sled.my.laser = optics.Laser(
        F = sys.F_carrier_1064,
        power_W = 1.,
        name = "laser",
    )

    sled.my.etm = optics.Mirror(
        T_hr = 0.25,
    )
    sled.my.etmPD = optics.MagicPD()
    sled.my.s1 = optics.Space(
        L_m = 100,
        L_detune_m = 0,
    )

    sys.bond_sequence(
        sled.laser.Fr,
        sled.etmPD.Bk,
        sled.s1.Fr,
        sled.etm.Fr,
    )

    sled.my.etm_DC = readouts.DCReadout(port = sled.etmPD.Wpd.o)
    sled.my.etm_drive = readouts.ACReadout(
        portN = sled.etmPD.Wpd.o,
        portD = sled.etm.posZ.i,
    )
    #sys.AC_freq(np.array([1]))
    return Bunch(locals())

@pytest.mark.optics_trivial
@pytest.mark.optics_fast
def test_trivial():
    b = gensys()
    sys = b.sys
    #sys.coupling_matrix_print()
    #sys.source_vector_print()
    #sys.solution.solution_vector_print()
    print("etm_DC", sys.sled.etm_DC.DC_readout)
    assertions.assertAlmostEqual(sys.sled.etm_DC.DC_readout, 1)


@pytest.mark.optics_fast
def test_mirror():
    b = gensys_full()
    sys = b.sys
    #sys.coupling_matrix_print()
    #sys.source_vector_print()
    #sys.solution.solution_vector_print()
    print("etm_DC", sys.sled.etm_DC.DC_readout)
    print("etm_drive", sys.sled.etm_drive.AC_sensitivity)
    #print("etm_Force[N]", sys.DC_readout('etm_ForceZ'))

    #print("A")
    #sys.coupling_matrix_print(select_from = b.sled.etm.posZ.i, select_to = b.sled.etm.Fr.o)
    #print("B")
    #sys.solution.coupling_matrix_print(
    #    select_to= b.sled.etm.Fr.i,
    #)
    assertions.assertAlmostEqual(sys.sled.etm_DC.DC_readout, .75)
    print("inv")
    #sys.solution.coupling_matrix_inv_print()
    print('A')
    sys.solution.coupling_matrix_inv_print(
        select_from = b.sled.etm.posZ.i,
        select_to = b.sled.etmPD.Fr.i,
    )
    print('B')

    sys.solution.coupling_matrix_print(
        select_from = b.sled.etmPD.Fr.i,
        select_to = b.sled.etmPD.Wpd.o,
        drive_set = 'AC',
        readout_set = 'AC',
    )
    print('B inv')
    sys.solution.coupling_matrix_inv_print(
        select_from = b.sled.etmPD.Fr.i,
        select_to = b.sled.etmPD.Wpd.o,
        drive_set = 'AC',
        readout_set = 'AC',
    )
    sys.solution.coupling_matrix_inv_print(
        select_from = b.sled.etm.posZ.i,
        select_to = b.sled.etmPD.Wpd.o,
        drive_set = 'AC',
        readout_set = 'AC',
    )

    #from BGSF.key_matrix import (
    #    DictKey,
    #    FrequencyKey,
    #)

    #rt_inv = sys.invert_system()
    #usb_keyL = DictKey({optics.OpticalFreqKey: FrequencyKey(b.sled.laser.optical_fdict), optics.ClassicalFreqKey: FrequencyKey({sys.F_AC : 1})}) | b.sled.laser.polarization | optics.LOWER
    #usb_keyR = DictKey({optics.OpticalFreqKey: FrequencyKey(b.sled.laser.optical_fdict), optics.ClassicalFreqKey: FrequencyKey({sys.F_AC : 1})}) | b.sled.laser.polarization | optics.RAISE
    #lsb_keyL = DictKey({optics.OpticalFreqKey: FrequencyKey(b.sled.laser.optical_fdict), optics.ClassicalFreqKey: FrequencyKey({sys.F_AC : -1})}) | b.sled.laser.polarization | optics.LOWER
    #lsb_keyR = DictKey({optics.OpticalFreqKey: FrequencyKey(b.sled.laser.optical_fdict), optics.ClassicalFreqKey: FrequencyKey({sys.F_AC : -1})}) | b.sled.laser.polarization | optics.RAISE
    #ucl_key = DictKey({optics.ClassicalFreqKey: FrequencyKey({sys.F_AC : 1})})
    #lcl_key = DictKey({optics.ClassicalFreqKey: FrequencyKey({sys.F_AC : -1})})
    #print("USBLU: ", rt_inv.get((b.sled.etm.Fr.o, usb_keyL), (b.sled.etm.posZ.i, ucl_key), 0))
    #print("USBRU: ", rt_inv.get((b.sled.etm.Fr.o, usb_keyR), (b.sled.etm.posZ.i, ucl_key), 0))
    #print("USBLL: ", rt_inv.get((b.sled.etm.Fr.o, usb_keyL), (b.sled.etm.posZ.i, lcl_key), 0))
    #print("USBRL: ", rt_inv.get((b.sled.etm.Fr.o, usb_keyR), (b.sled.etm.posZ.i, lcl_key), 0))
    #print("LSBLU: ", rt_inv.get((b.sled.etm.Fr.o, lsb_keyL), (b.sled.etm.posZ.i, ucl_key), 0))
    #print("LSBRU: ", rt_inv.get((b.sled.etm.Fr.o, lsb_keyR), (b.sled.etm.posZ.i, ucl_key), 0))
    #print("LSBLL: ", rt_inv.get((b.sled.etm.Fr.o, lsb_keyL), (b.sled.etm.posZ.i, lcl_key), 0))
    #print("LSBRL: ", rt_inv.get((b.sled.etm.Fr.o, lsb_keyR), (b.sled.etm.posZ.i, lcl_key), 0))
    #print("AC:", sys.AC_sensitivity('ETM_Drive'))

    #from BGSF.utilities.mpl.autoniceplot import (mplfigB)
    #F = mplfigB(Nrows = 2)
    #F.ax0.loglog(sys.F_AC_Hz, abs(sys.AC_sensitivity('ETM_Drive')))
    #F.ax1.semilogx(sys.F_AC_Hz, np.angle(sys.AC_sensitivity('ETM_Drive')))
    #F.save('trans_xfer')
    #print("etm_Force[N]", sys.DC_readout('etm_ForceZ'))

if __name__ == '__main__':
    test_mirror()
