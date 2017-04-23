"""
"""
from __future__ import division

import declarative as decl

from . import ports
from . import bases

sided_conversions = {
    "one-sided" :    2,
    "one sided" :    2,
    "one" :          2,
    "single-sided" : 2,
    "single sided" : 2,
    "single" :       2,
    "two-sided" :    1,
    "two sided" :    1,
    "two" :          1,
    "double-sided" : 1,
    "double sided" : 1,
    "double" :       1,
}

class WhiteNoise(bases.SignalElementBase):
    @decl.dproperty
    def port(self, val):
        #self.system.own_port_virtual(self, val.i)
        return val

    @decl.dproperty
    def sided(self, val):
        assert(val in sided_conversions)
        return val

    @decl.mproperty
    def conversion(self):
        return sided_conversions[self.sided]

    def Fsq_Hz_by_freq(self, F):
        return 1

    def system_setup_noise(self, matrix_algorithm):
        for k1 in matrix_algorithm.port_set_get(self.port.i):
            freq = k1[ports.ClassicalFreqKey]
            k2 = k1.without_keys(ports.ClassicalFreqKey) | ports.DictKey({ports.ClassicalFreqKey : -freq})
            matrix_algorithm.noise_pair_insert(
                self.port.i, k1, self.port.i, k2, self
            )
        return

    def noise_2pt_expectation(self, p1, k1, p2, k2):
        Fsq_Hz = 1 / self.conversion
        return Fsq_Hz
