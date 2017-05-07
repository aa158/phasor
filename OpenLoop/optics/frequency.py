
# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function
#from OpenLoop.utilities.print import print

import declarative as decl

from ..base import (
    FrequencyBase,
    OOA_ASSIGN,
)


class OpticalFrequency(FrequencyBase):

    @decl.dproperty
    def wavelen_m(self, val):
        return val

    @decl.mproperty
    def iwavelen_m(self):
        return 1/self.wavelen_m

    def __init__(
            self,
            order       = None,
            **kwargs
    ):
        super(OpticalFrequency, self).__init__(**kwargs)
        OOA_ASSIGN(self).order = order
        return
