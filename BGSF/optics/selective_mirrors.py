# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
#from BGSF.utilities.print import print

from . import ports
from . import selectors


class MirrorSelectionStack(
    ports.OpticalDegenerate4PortMixin,
    selectors.OpticalSelectionStack,
):
    def __init__(
        self,
        sub_element_map,
        select_map,
        AOI_deg = 0,
        **kwargs
    ):
        if AOI_deg == 0:
            port_set = set(['Fr', 'Fr'])
        else:
            port_set = set(['FrA', 'FrB', 'BkA', 'BkB'])

        #TODO make these use the ooa mechanism rather than kwargs propagation

        #TODO make better error messages
        for mname, mconstr in list(sub_element_map.items()):
            mconstr.adjust_safe(
                AOI_deg         = AOI_deg,
            )
            mconstr.adjust_defer(**kwargs)

        super(MirrorSelectionStack, self).__init__(
            sub_element_map = sub_element_map,
            select_map      = select_map,
            port_set        = port_set,
            AOI_deg         = AOI_deg,
            **kwargs
        )

        #TODO, HACK!
        if AOI_deg == 0:
            self.Fr.pchain = self.Bk
            self.Bk.pchain = self.Fr
        else:
            self.FrA.pchain = self.BkA
            self.BkA.pchain = self.FrA
            self.FrB.pchain = self.BkB
            self.BkB.pchain = self.FrB

        #TODO, combine mechanicals


class PolarizingMirror(MirrorSelectionStack):
    def __init__(
        self,
        mirror_P,
        mirror_S,
        **kwargs
    ):
        super(PolarizingMirror, self).__init__(
            sub_element_map = dict(
                pol_P = mirror_P,
                pol_S = mirror_S,
            ),
            select_map = dict(
                pol_S = ports.PolS,
                pol_P = ports.PolP,
            ),
            **kwargs
        )


class HarmonicMirror(MirrorSelectionStack):
    def __init__(
        self,
        mirror_H1,
        mirror_H2,
        **kwargs
    ):
        kH1 = self.system.F_carrier_1064
        kH2 = 2 * kH1
        super(HarmonicMirror, self).__init__(
            sub_element_map = dict(
                H1 = mirror_H1,
                H2 = mirror_H2,
            ),
            select_map = dict(
                H1 = kH1,
                H2 = kH2,
            ),
            **kwargs
        )




