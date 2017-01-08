"""
"""

from __future__ import division
from __future__ import print_function

from unittest import TestCase, main

import numpy as np

from declarative.bunch import (
    Bunch,
)

from BGSF.optics import (
    Mirror,
    PD,
    MagicPD,
    Space,
    Laser,
)

from BGSF.system.optical import (
    OpticalSystem
)

from BGSF.readouts import (
    DCReadout,
    ACReadout,
)

#from BGSF.utilities.np import logspaced


def gensys(
        F_AC_Hz,
        loss_EM = 0,
        loss_BS = 0,
):
    sys = OpticalSystem()
    sled = sys.sled
    sled.PSL = Laser(
        F = sys.F_carrier_1064,
        power_W = 1.,
    )

    sled.mX = Mirror(
        T_hr = 0,
        L_hr = loss_EM,
        facing_cardinal = 'W',
    )
    sled.mY = Mirror(
        T_hr = 0,
        L_hr = loss_EM,
        facing_cardinal = 'S',
    )
    #T_hr = sys.optical_harmonic_value(.3),
    sled.mBS = Mirror(
        T_hr = .5,
        L_hr = loss_BS,
        AOI_deg = 45,
        facing_cardinal = 'NW',
    )

    sled.sX = Space(
        1,
        L_detune_m = 1064e-9 / 8 * .01,
    )
    sled.sY = Space(
        1,
        L_detune_m = 0,
    )

    sled.symPD = MagicPD(
        facing_cardinal = 'E',
    )
    sled.asymPD = PD()

    sys.optical_link_sequence_WtoE(
        sled.PSL,
        sled.symPD,
        sled.mBS,
        sled.sX,
        sled.mX,
    )
    sys.optical_link_sequence_StoN(
        sled.asymPD,
        sled.mBS,
        sled.sY,
        sled.mY,
    )

    sled.sym_DC = DCReadout(
        port = sled.symPD.Wpd.o,
    )
    sled.asym_DC = DCReadout(
        port = sled.asymPD.Wpd.o,
    )
    sled.asym_drive = ACReadout(
        portD = sled.mX.posZ.i,
        portN = sled.asymPD.Wpd.o,
    )
    return Bunch(locals())


class TestMichelson(TestCase):
    def test_mich(self):
        b = gensys(
            #F_AC_Hz = logspaced(.001, 1e6, 10),
            F_AC_Hz = np.array([0]),
        )
        sys = b.sys
        #sys.solve_to_order(1)
        #print()
        sol = sys.solve()
        #sys.coupling_matrix_print()
        #sys.source_vector_print()
        #sys.solution_vector_print()
        print("sym_DC",  sol.views.sym_DC.DC_readout)
        print("asym_DC", sol.views.asym_DC.DC_readout)

        ptot = sol.views.sym_DC.DC_readout + sol.views.asym_DC.DC_readout
        pfrac = sol.views.asym_DC.DC_readout / ptot
        sense = (pfrac * (1-pfrac))**.5 * 4 * np.pi * sys.F_carrier_1064.iwavelen_m

        AC = sol.views.asym_drive.AC_sensitivity
        print("AC mag rel expect:", abs(AC) / sense)
        self.assertAlmostEqual(abs(AC), sense, 5)
        print("AC phase :", np.angle(AC, deg = True))

        E1064_J = 1.2398 / 1.064 / 6.24e18
        N_expect = (2 * sol.views.asym_DC.DC_readout * E1064_J)**.5
        AC_noise = sol.views.asym_drive.AC_ASD
        print("ACnoise", AC_noise)
        print("ACnoise_rel", (N_expect / AC_noise)**2)
        self.assertAlmostEqual(N_expect, AC_noise, 5)

        print("ACnoise m_rtHz", sol.views.asym_drive.AC_noise_limited_sensitivity)
        #sys.port_set_print(b.mBS.BkB.i)
        #sys.port_set_print(b.vterm.Fr.o)
        #sys.coupling_matrix_inv_print(select_to = b.asymPD.Wpd.o)

        #from BGSF.utilities.mpl.autoniceplot import (mplfigB)
        #F = mplfigB(Nrows = 2)
        #F.ax0.loglog(sys.F_AC_Hz, abs(AC))
        #F.ax1.semilogx(sys.F_AC_Hz, np.angle(AC, deg = True))
        #F.save('trans_xfer_mich')

    def test_mich_lossy(self):
        b = gensys(
            #F_AC_Hz = logspaced(.001, 1e6, 10),
            F_AC_Hz = np.array([0]),
            #loss_EM = .2,
            loss_BS = .2,
        )
        sys = b.sys
        sol = sys.solve()
        #sys.coupling_matrix_print()
        #sys.source_vector_print()
        #sys.solution_vector_print()
        print("sym_DC",  sol.views.sym_DC.DC_readout)
        print("asym_DC", sol.views.asym_DC.DC_readout)

        ptot = sol.views.sym_DC.DC_readout + sol.views.asym_DC.DC_readout
        pfrac = sol.views.asym_DC.DC_readout / ptot
        sense = (pfrac * (1-pfrac))**.5 * 4 * np.pi * sys.F_carrier_1064.iwavelen_m

        AC = sol.views.asym_drive.AC_sensitivity
        print("AC mag rel expect:", abs(AC) / sense)

        #TODO account for the sensitivity loss from the loss here
        #self.assertAlmostEqual(abs(AC), sense, 5)
        print("AC phase :", np.angle(AC, deg = True))

        E1064_J = 1.2398 / 1.064 / 6.24e18
        N_expect = (sol.views.asym_DC.DC_readout * E1064_J)**.5
        AC_noise = sol.views.asym_drive.AC_ASD
        print("ACnoise", AC_noise)
        print("ACnoise_rel", (N_expect / AC_noise)**2)
        self.assertAlmostEqual(N_expect, AC_noise, 5)

        print("ACnoise m_rtHz", sol.views.asym_drive.AC_noise_limited_sensitivity)
        #sys.port_set_print(b.mBS.BkB.i)
        #sys.port_set_print(b.vterm.Fr.o)
        #sys.coupling_matrix_inv_print(select_to = b.asymPD.Wpd.o)

        #from BGSF.utilities.mpl.autoniceplot import (mplfigB)
        #F = mplfigB(Nrows = 2)
        #F.ax0.loglog(sys.F_AC_Hz, abs(AC))
        #F.ax1.semilogx(sys.F_AC_Hz, np.angle(AC, deg = True))
        #F.save('trans_xfer_mich')

if __name__ == '__main__':
    main()
