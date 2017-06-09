"""
"""
from __future__ import (division, print_function)

import numpy.testing as np_test
import numpy as np
import declarative as decl
from declarative.bunch import (
    DeepBunch,
)

#import numpy as np

from openLoop import system
from openLoop import readouts
from openLoop import optics
from openLoop.optics.nonlinear_crystal import NonlinearCrystal
from openLoop.utilities.print import pprint

#from openLoop.utilities.np import logspaced


def test_split():
    sys = system.BGSystem()
    sys.own.PSL = optics.Laser(
        F = sys.system.F_carrier_1064,
        power_W = 2.,
    )

    sys.own.PSLG = optics.Laser(
        F = sys.system.F_carrier_1064,
        multiple = 2,
        power_W = 1.,
    )

    sys.own.mDC1 = optics.HarmonicMirror(
        mirror_H1 = optics.Mirror(
            T_hr = 1,
        ),
        mirror_H2 = optics.Mirror(
            T_hr = 0,
        ),
        AOI_deg = 45,
    )
    sys.own.mDC2 = optics.HarmonicMirror(
        mirror_H1 = optics.Mirror(
            T_hr = 1,
        ),
        mirror_H2 = optics.Mirror(
            T_hr = 0,
        ),
        AOI_deg = 45,
    )
    sys.own.PD_R = optics.PD()
    sys.own.PD_G = optics.PD()

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
    sys.own.DC_R = readouts.DCReadout(
        port = sys.PD_R.Wpd.o,
    )
    sys.own.DC_G = readouts.DCReadout(
        port = sys.PD_G.Wpd.o,
    )
    print("A")
    pprint(sys.ooa_params.test.PSL)
    np_test.assert_almost_equal(sys.DC_R.DC_readout, 2)
    np_test.assert_almost_equal(sys.DC_G.DC_readout, 1)


#def test_shg():
#    sys = system.BGSystem()
#    sys.own.PSL = optics.Laser(
#        F = sys.system.F_carrier_1064,
#        power_W = 1.,
#    )
#
#    sys.own.ktp = NonlinearCrystal(
#        nlg = 1,
#        length_mm = 1,
#        N_ode = 1000,
#        solution_order = 4,
#    )
#
#    sys.own.mDC2 = optics.HarmonicMirror(
#        mirror_H1 = optics.Mirror(
#            T_hr = 1,
#        ),
#        mirror_H2 = optics.Mirror(
#            T_hr = 0,
#        ),
#        AOI_deg = 45,
#    )
#    sys.own.PD_R = optics.PD()
#    sys.own.PD_G = optics.PD()
#
#    sys.system.bond_sequence(
#        sys.PSL.Fr,
#        sys.ktp.Fr,
#        sys.mDC2.FrA,
#        sys.PD_R.Fr,
#    )
#    sys.system.bond_sequence(
#        sys.mDC2.FrB,
#        sys.PD_G.Fr,
#    )
#    sys.own.DC_R = readouts.DCReadout(
#        port = sys.PD_R.Wpd.o,
#    )
#    sys.own.DC_G = readouts.DCReadout(
#        port = sys.PD_G.Wpd.o,
#    )
#    #print("A")
#    #pprint(sys.ooa_params.test.PSL)
#    print("sys.DC_R.DC_readout", sys.DC_R.DC_readout, 2)
#    print("sys.DC_G.DC_readout", sys.DC_G.DC_readout, 1)
#    conv = 0.069527636785009506
#    conv = 1 - np.tanh(2)**2
#    np_test.assert_almost_equal(sys.DC_R.DC_readout / conv, 1, 2)
#    np_test.assert_almost_equal(sys.DC_G.DC_readout / (1 - conv), 1, 2)


def test_aom():
    from openLoop.optics.models.AOMTestStand import AOMTestStand
    db = DeepBunch()
    sys = system.BGSystem(
        ooa_params = db,
    )
    sys.own.test = AOMTestStand()
    db = sys.ooa_shadow()
    sys.test.LO.amplitude
    print(sys.test.DC_R1.DC_readout)

if __name__ == '__main__':
    main()
