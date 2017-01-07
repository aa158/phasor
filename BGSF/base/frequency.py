# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from YALL.utilities.print import print
import numpy as np

from .bases import (
    FrequencyBase,
)

from .elements import (
    SystemElementBase,
    OOA_ASSIGN,
)


class Frequency(FrequencyBase, SystemElementBase):
    def __init__(
            self,
            F_Hz,
            F_center_Hz = None,
            F_width_Hz  = 0,
            order       = None,
            groups      = {},
            **kwargs
    ):
        super(Frequency, self).__init__(**kwargs)

        OOA_ASSIGN(self).F_Hz = F_Hz

        if F_center_Hz is None:
            F_center_Hz = (np.max(self.F_Hz) + np.min(self.F_Hz)) / 2

        OOA_ASSIGN(self).F_center_Hz = F_center_Hz

        if F_width_Hz is None:
            F_center_Hz = (np.max(self.F_Hz) - np.min(self.F_Hz)) / 2

        OOA_ASSIGN(self).F_width_Hz  = F_width_Hz

        OOA_ASSIGN(self).order = order

        for group, b_incl in groups.items():
            self.ooa_params.groups[group] = b_incl

        groups = set()
        for group, b_incl in self.ooa_params.groups.items():
            if b_incl:
                groups.add(group)
        self.groups = groups
        return
