"""
"""
from __future__ import (division, print_function)

import numpy.testing as np_test
import declarative as decl
from declarative.bunch import (
    DeepBunch,
)

#import numpy as np

from BGSF import system
from BGSF import readouts
from BGSF import optics
from BGSF.optics.nonlinear_crystal import NonlinearCrystal
from BGSF.utilities.print import pprint

#from BGSF.utilities.np import logspaced


def test_split():
    sys = system.BGSystem()
    sys.my.PSL = optics.Laser(
        F = sys.system.F_carrier_1064,
        power_W = 2.,
    )

    sys.my.PSLG = optics.Laser(
        F = sys.system.F_carrier_1064,
        multiple = 2,
        power_W = 1.,
    )

    sys.my.mDC1 = optics.HarmonicMirror(
        mirror_H1 = optics.Mirror(
            T_hr = 1,
        ),
        mirror_H2 = optics.Mirror(
            T_hr = 0,
        ),
        AOI_deg = 45,
    )
    sys.my.mDC2 = optics.HarmonicMirror(
        mirror_H1 = optics.Mirror(
            T_hr = 1,
        ),
        mirror_H2 = optics.Mirror(
            T_hr = 0,
        ),
        AOI_deg = 45,
    )
    sys.my.PD_R = optics.PD()
    sys.my.PD_G = optics.PD()

    sys.system.bond_sequence(
        sys.PSL.Fr,
        sys.mDC1.FrA,
        sys.mDC2.FrA,
        sys.PD_R.Fr,
    )
    sys.system.bond_sequence(
        sys.PSLG.Fr,
        sys.mDC1.BkB,
    )
    sys.system.bond_sequence(
        sys.mDC2.FrB,
        sys.PD_G.Fr,
    )
    sys.my.DC_R = readouts.DCReadout(
        port = sys.PD_R.Wpd.o,
    )
    sys.my.DC_G = readouts.DCReadout(
        port = sys.PD_G.Wpd.o,
    )
    print("A")
    pprint(sys.ooa_params.test.PSL)
    np_test.assert_almost_equal(sys.DC_R.DC_readout, 2)
    np_test.assert_almost_equal(sys.DC_G.DC_readout, 1)


def test_shg():
    sys = system.BGSystem()
    sys.my.PSL = optics.Laser(
        F = sys.system.F_carrier_1064,
        power_W = 2.,
    )

    sys.my.ktp = NonlinearCrystal(
        nlg = .1,
        length_mm = 10,
    )

    sys.my.mDC2 = optics.HarmonicMirror(
        mirror_H1 = optics.Mirror(
            T_hr = 1,
        ),
        mirror_H2 = optics.Mirror(
            T_hr = 0,
        ),
        AOI_deg = 45,
    )
    sys.my.PD_R = optics.PD()
    sys.my.PD_G = optics.PD()

    sys.system.bond_sequence(
        sys.PSL.Fr,
        sys.ktp.Fr,
        sys.mDC2.FrA,
        sys.PD_R.Fr,
    )
    sys.system.bond_sequence(
        sys.mDC2.FrB,
        sys.PD_G.Fr,
    )
    sys.my.DC_R = readouts.DCReadout(
        port = sys.PD_R.Wpd.o,
    )
    sys.my.DC_G = readouts.DCReadout(
        port = sys.PD_G.Wpd.o,
    )
    #print("A")
    #pprint(sys.ooa_params.test.PSL)
    print("sys.DC_R.DC_readout", sys.DC_R.DC_readout, 2)
    print("sys.DC_G.DC_readout", sys.DC_G.DC_readout, 1)
    np_test.assert_almost_equal(sys.DC_R.DC_readout, 2)
    np_test.assert_almost_equal(sys.DC_G.DC_readout, 1)

if __name__ == '__main__':
    main()
