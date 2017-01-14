"""
TODO: isolate the RMS
"""
from __future__ import (division, print_function)

from unittest import TestCase, main

#import numpy as np

from declarative.bunch import (
    Bunch,
)

from BGSF.optics import (
    Mirror,
    PD,
    Space,
    Laser,
)

from BGSF.base import (
    Frequency,
)

from BGSF.signals import (
    SignalGenerator,
    Mixer,
    #RMSMixer,
)

from BGSF.system.optical import (
    OpticalSystem
)

from BGSF.readouts import (
    DCReadout,
    #ACReadout,
    NoiseReadout,
)


#from BGSF.utilities.np import logspaced


#http://journals.aps.org/pra/pdf/10.1103/PhysRevA.43.5022
#note that the sideband order must be at least 2 to show the effect
def gensys(
        loss_BS = 0,
        freq_order_max_default = 10,
):
    sys = OpticalSystem(
        freq_order_max_default = freq_order_max_default,
    )
    sled = sys.sled

    sled.my.F_shift = Frequency(
        F_Hz = 1000,
        F_center_Hz = 1000,
    )
    sled.my.laser_upper = Laser(
        F = sys.F_carrier_1064,
        power_W = 1.,
        classical_fdict = {
            sled.F_shift : 1,
        },
    )
    sled.my.laser_lower = Laser(
        F = sys.F_carrier_1064,
        power_W = 1.,
        classical_fdict = {
            sled.F_shift : -1,
        },
    )

    sled.my.mBS = Mirror(
        T_hr = .5,
        L_hr = loss_BS,
        AOI_deg = 45,
    )

    sled.my.PD1 = PD()
    sled.my.PD2 = PD()

    sled.my.mix_LO = SignalGenerator(
        F = sled.F_shift,
        multiple = 1,
        amplitude = 2,
    )
    sled.my.mixer = Mixer(
    )
    #sled.my.mixerIRMS = RMSMixer(
    #)
    #sled.my.mixerQRMS = RMSMixer(
    #)
    sled.my.sDelay = Space(
        L_m = 1,
        #L_detune_m = 1064e-9 / 4,
    )
    sys.bond(sled.mix_LO.Out, sled.mixer.LO)
    sys.bond(sled.PD2.Wpd,   sled.mixer.I)
    #sys.link(sled.mixer.R_I, sled.mixerIRMS.I)
    #sys.link(sled.mixer.R_Q, sled.mixerQRMS.I)

    sys.bond_sequence(
        sled.laser_upper.Fr,
        sled.mBS.FrA,
        sled.PD1.Fr,
    )
    sys.bond_sequence(
        sled.laser_lower.Fr,
        sled.mBS.BkB,
        sled.PD2.Fr,
    )

    sled.my.PD1_DC       = DCReadout(port = sled.PD1.Wpd.o)
    sled.my.PD2_DC       = DCReadout(port = sled.PD2.Wpd.o)
    sled.my.PD1_MIX_I    = DCReadout(port = sled.mixer.R_I.o)
    sled.my.PD1_MIX_Q    = DCReadout(port = sled.mixer.R_Q.o)
    #sled.my.PD1_MIX_IRMS = DCReadout(port = sled.mixerIRMS.RMS.o)
    #sled.my.PD1_MIX_QRMS = DCReadout(port = sled.mixerQRMS.RMS.o)
    sled.my.PD1_AC       = NoiseReadout(portN = sled.PD1.Wpd.o)
    sled.my.PD1_MIX_I_N  = NoiseReadout(portN = sled.mixer.R_I.o)
    sled.my.PD1_MIX_Q_N  = NoiseReadout(portN = sled.mixer.R_Q.o)
    return Bunch(locals())

class TestPolarizations(TestCase):
    def test_cyclostationary(self):
        b = gensys(
            #F_AC_Hz = logspaced(.001, 1e6, 10),
            #F_AC_Hz = np.array([10]),
            freq_order_max_default = 3,
        )
        sys = b.sys
        print()
        sol = sys.solve()
        #sys.coupling_matrix_print()
        #sys.source_vector_print()
        #sys.solution_vector_print()
        import pprint
        pp = pprint.PrettyPrinter()
        pp.pprint(sys.sled)
        print("DC1",  sys.sled.PD1_DC.DC_readout)
        print("DC2",  sys.sled.PD2_DC.DC_readout)
        print("AC1",  sys.sled.PD1_AC.CSD['R', 'R'])
        E1064_J = 1.2398 / 1.064 / 6.24e18
        N_expect = (2 * sys.sled.PD1_DC.DC_readout * E1064_J)
        print("AC1 rel",  (sys.sled.PD1_AC.CSD['R', 'R'] / N_expect)**.5)

        print("DC1_MIX_I",  sys.sled.PD1_MIX_I.DC_readout)
        print("DC1_MIX_Q",  sys.sled.PD1_MIX_Q.DC_readout)

        print("AC1_MIX_I_N",  sys.sled.PD1_MIX_I_N.CSD['R', 'R'])
        print("AC1_MIX_I_N rel",  (sys.sled.PD1_MIX_I_N.CSD['R', 'R'] / N_expect))
        self.assertAlmostEqual(sys.sled.PD1_MIX_I_N.CSD['R', 'R'] / N_expect, 3, 2)
        #print("DC1_MIX_I_RMS",  sys.sled.PD1_MIX_IRMS.DC_readout)
        print("AC1_MIX_Q_N",  sys.sled.PD1_MIX_Q_N.CSD['R', 'R'])
        print("AC1_MIX_Q_N rel",  (sys.sled.PD1_MIX_Q_N.CSD['R', 'R'] / N_expect))
        self.assertAlmostEqual(sys.sled.PD1_MIX_Q_N.CSD['R', 'R'] / N_expect, 1, 2)
        #print("DC1_MIX_Q_RMS",  sys.sled.PD1_MIX_QRMS.DC_readout)
        #sol.coupling_matrix_print(select_to = b.sled.mixerIRMS.RMS.o)
        sol.solution_vector_print(select_to = b.sled.mixer.R_I.o)
        sol.solution_vector_print(select_to = b.sled.mixer.R_Q.o)

        #TODO isolate this test
        #from BGSF.system_graphs import (
        #    coherent_sparsity_graph
        #)

        #gdata = coherent_sparsity_graph(sol)
        #print("Order: ", gdata.order)
        #print("Inputs: ")
        #def lprint(s):
        #    p = [repr(l) for l in s]
        #    p.sort()
        #    for x in p:
        #        print(x)
        #lprint(gdata.inputs_set)
        #print("Outputs: ")
        #lprint(gdata.outputs_set)
        #print(len(gdata.inputs_set) * len(gdata.outputs_set))
        #print(len(gdata.active) * len(gdata.active))
        ##print("Active: ")
        ##lprint(gdata.active)

        #sys.coupling_matrix_print(select_to = b.sled.mixer.R_Q.o)

        #sys.coupling_matrix_inv_print(
        #    select_to = b.sled.mixer.R_I.o,
        #    select_from = b.sled.laser_upper.Fr.o,
        #)
        #sys.coupling_matrix_inv_print(
        #    select_to = b.sled.mixer.R_I.o,
        #    select_from = b.sled.laser_lower.Fr.o,
        #)

        #print()
        #sys.coupling_matrix_inv_print(
        #    select_to = b.sled.mixer.R_Q.o,
        #    select_from = b.sled.laser_upper.Fr.o,
        #)
        #sys.coupling_matrix_inv_print(
        #    select_to = b.sled.mixer.R_Q.o,
        #    select_from = b.sled.laser_lower.Fr.o,
        #)


if __name__ == '__main__':
    main()
