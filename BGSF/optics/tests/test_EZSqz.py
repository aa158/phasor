"""
"""
from __future__ import (division, print_function)

from BGSF.optics import (
    Mirror,
    PD,
    MagicPD,
    Space,
    Laser,
    EZSqz,
)

from BGSF.system.optical import (
    OpticalSystem
)

import pytest
pytestmark = pytest.mark.skip('EZSqz still WIP')
pytest.skip("Want to skip!")

#from BGSF.utilities.np import logspaced


def gensys(
        F_AC_Hz,
        loss_EM = 0,
        loss_BS = 0,
):
    sys = OpticalSystem()
    sled = sys.sled
    sled.sqz = EZSqz(
        rel_variance_1 = .1,
        rel_variance_2 = 12,
    )
    sled.sqz = EZSqz(
        nonlinear_power_gain = 10,
        loss = .1,
    )

    sled.laser = Laser(
        F = sys.F_carrier_1064,
        power_W = 1.,
        name = "PSL",
    )

    sled.mX = Mirror(
        T_hr = 0,
        L_hr = loss_EM,
        name = 'mX',
        facing_cardinal = 'W',
    )
    sled.mY = Mirror(
        T_hr = 0,
        L_hr = loss_EM,
        name = 'mY',
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
        L_detune_m = 1064e-9 / 8,
        name = 'sX',
    )
    sled.sY = Space(
        1,
        L_detune_m = 0,
        name = 'sY',
    )

    sled.symPD = MagicPD(
        name = 'symPD',
        facing_cardinal = 'E',
    )
    sled.asymPD = PD(
        name = 'asymPD',
    )

    #sys.link(laser.Fr, symPD.Bk)
    #sys.link(symPD.Fr, mBS.FrA)
    #sys.link(mBS.FrB, sY.Fr)
    #sys.link(sY.Bk, mY.Fr)
    #sys.link(mBS.BkA, sX.Fr)
    #sys.link(sX.Bk, mX.Fr)
    #sys.link(mBS.BkB, asymPD.Fr)
    sys.optical_link_sequence_WtoE(
        sled.laser, sled.symPD, sled.mBS, sled.sX, sled.mX,
    )
    sys.optical_link_sequence_StoN(
        sled.asymPD, sled.mBS, sled.sY, sled.mY,
    )

    #vterm = VacuumTerminator(name = 'vterm')
    #sys.optical_link_sequence_StoN(
    #    vterm, mBS,
    #)

    sys.AC_freq(F_AC_Hz)
    sys.DC_readout_add('sym_DC', sled.symPD.Wpd.o)
    sys.DC_readout_add('asym_DC', sled.asymPD.Wpd.o)
    sys.AC_sensitivity_add('asym_Drive', sled.mX.posZ.i, sled.asymPD.Wpd.o)
    return Bunch(locals())

def test_mich():
    b = gensys(
        #F_AC_Hz = logspaced(.001, 1e6, 10),
        F_AC_Hz = np.array([0]),
    )
    sys = b.sys
    sys.solve_to_order(1, no_AC = True)
    print()
    sys.solve_to_order(2)
    #sys.coupling_matrix_print()
    #sys.source_vector_print()
    #sys.solution_vector_print()
    print("sym_DC",  sys.DC_readout('sym_DC'))
    print("asym_DC", sys.DC_readout('asym_DC'))

    ptot = sys.DC_readout('sym_DC') + sys.DC_readout('asym_DC')
    pfrac = sys.DC_readout('asym_DC') / ptot
    sense = (pfrac * (1-pfrac))**.5 * 4 * np.pi * sys.F_carrier_1064.iwavelen_m

    AC = sys.AC_sensitivity('asym_Drive')
    print("ACmag:", abs(AC) / sense)
    print("ACdeg:", np.angle(AC, deg = True))

    E1064_J = 1.2398 / 1.064 / 6.24e18
    N_expect = (sys.DC_readout('asym_DC') * E1064_J)**.5
    AC_noise = sys.AC_noise('asym_Drive')
    print("ACnoise", AC_noise)
    print("ACnoise_rel", (N_expect / AC_noise)**2)

    #sys.port_set_print(b.mBS.BkB.i)
    #sys.port_set_print(b.vterm.Fr.o)
    #sys.coupling_matrix_inv_print(select_to = b.asymPD.Wpd.o)

    #from BGSF.utilities.mpl.autoniceplot import (mplfigB)
    #F = mplfigB(Nrows = 2)
    #F.ax0.loglog(sys.F_AC_Hz, abs(AC))
    #F.ax1.semilogx(sys.F_AC_Hz, np.angle(AC, deg = True))
    #F.save('trans_xfer_mich')

def test_mich_lossy():
    b = gensys(
        #F_AC_Hz = logspaced(.001, 1e6, 10),
        F_AC_Hz = np.array([0]),
        #loss_EM = .2,
        loss_BS = .2,
    )
    sys = b.sys
    sys.solve_to_order(1, no_AC = True)
    print()
    sys.solve_to_order(2)
    #sys.coupling_matrix_print()
    #sys.source_vector_print()
    #sys.solution_vector_print()
    print("sym_DC",  sys.DC_readout('sym_DC'))
    print("asym_DC", sys.DC_readout('asym_DC'))

    ptot = sys.DC_readout('sym_DC') + sys.DC_readout('asym_DC')
    pfrac = sys.DC_readout('asym_DC') / ptot
    sense = (pfrac * (1-pfrac))**.5 * 4 * np.pi * sys.F_carrier_1064.iwavelen_m

    AC = sys.AC_sensitivity('asym_Drive')
    print("ACmag:", abs(AC) / sense)
    print("ACdeg:", np.angle(AC, deg = True))

    E1064_J = 1.2398 / 1.064 / 6.24e18
    N_expect = (sys.DC_readout('asym_DC') * E1064_J)**.5
    AC_noise = sys.AC_noise('asym_Drive')
    print("ACnoise", AC_noise)
    print("ACnoise_rel", (N_expect / AC_noise)**2)

    sys.port_set_print(b.mX._LFr.i)
    #print("X")
    #sys.coupling_matrix_inv_print(select_from = b.mBS._LBkB.i)

    #print("X")
    #sys.coupling_matrix_print(select_to = b.mBS._LFrB.i)

    #from BGSF.utilities.mpl.autoniceplot import (mplfigB)
    #F = mplfigB(Nrows = 2)
    #F.ax0.loglog(sys.F_AC_Hz, abs(AC))
    #F.ax1.semilogx(sys.F_AC_Hz, np.angle(AC, deg = True))
    #F.save('trans_xfer_mich')

if __name__ == '__main__':
    test_mich()
