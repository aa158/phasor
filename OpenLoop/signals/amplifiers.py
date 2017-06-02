# -*- coding: utf-8 -*-
"""
"""
from __future__ import (division, print_function)
from collections import defaultdict
import declarative

from . import bases
from . import ports


class DistributionAmplifier(bases.CouplerBase, bases.SystemElementBase):
    def __init__(
            self,
            port_gains,
            **kwargs
    ):
        super(DistributionAmplifier, self).__init__(**kwargs)
        bases.OOA_ASSIGN(self).port_gains = port_gains

        self.my.In  = ports.SignalInPort()

        for pname in self.port_gains:
            self.insert(ports.SignalOutPort(), pname)
        return

    def system_setup_ports(self, ports_algorithm):
        for kfrom in ports_algorithm.port_update_get(self.In.i):
            for pname in self.port_gains:
                port = getattr(self, pname)
                ports_algorithm.port_coupling_needed(port.o, kfrom)
        for pname in self.port_gains:
            port = getattr(self, pname)
            for kto in ports_algorithm.port_update_get(port.o):
                ports_algorithm.port_coupling_needed(self.In.i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for kfrom in matrix_algorithm.port_set_get(self.In.i):
            for pname, pgain in list(self.port_gains.items()):
                port = getattr(self, pname)
                matrix_algorithm.port_coupling_insert(self.In.i,  kfrom, port.o, kfrom, pgain)
        return


class SummingAmplifier(bases.CouplerBase, bases.SystemElementBase):
    def __init__(
            self,
            port_gains,
            **kwargs
    ):
        super(SummingAmplifier, self).__init__(**kwargs)
        bases.OOA_ASSIGN(self).port_gains = port_gains

        self.my.O  = ports.SignalOutPort(sname = 'LO')

        for pname in self.port_gains:
            self.insert(ports.SignalInPort(sname = pname), pname)
        return

    def system_setup_ports(self, ports_algorithm):
        for kto in ports_algorithm.port_update_get(self.O.o):
            for pname in self.port_gains:
                port = getattr(self, pname)
                ports_algorithm.port_coupling_needed(port.i, kto)
        for pname in self.port_gains:
            port = getattr(self, pname)
            for kfrom in ports_algorithm.port_update_get(port.i):
                ports_algorithm.port_coupling_needed(self.O.o, kfrom)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for pname, pgain in list(self.port_gains.items()):
            port = getattr(self, pname)
            for kfrom in matrix_algorithm.port_set_get(port.i):
                matrix_algorithm.port_coupling_insert(port.i,  kfrom, self.O.o, kfrom, pgain)
        return


class MatrixAmplifier(bases.CouplerBase, bases.SystemElementBase):
    def __init__(
            self,
            port_pair_gains,
            **kwargs
    ):
        super(MatrixAmplifier, self).__init__(**kwargs)
        bases.OOA_ASSIGN(self).port_pair_gains = port_pair_gains

        self.In  = declarative.Bunch()
        self.O  = declarative.Bunch()

        dd = defaultdict(dict)
        for (iname, oname), xfer in list(self.port_pair_gains.items()):
            dd[iname][oname] = xfer
        self._dd = dd

        for (iname, oname), xfer in list(self.port_pair_gains.items()):
            if iname not in self.In:
                self.In[iname] = ports.SignalInPort(sname = iname)
            if oname not in self.O:
                self.O[iname] = ports.SignalOutPort(sname = oname)
        return

    def system_setup_ports(self, ports_algorithm):
        for (iname, oname), xfer in list(self.port_pair_gains.items()):
            for kfrom in ports_algorithm.port_update_get(self.In[iname].i):
                ports_algorithm.port_coupling_needed(self.O[oname].o, kfrom)
            for kto in ports_algorithm.port_update_get(self.O[oname].o):
                ports_algorithm.port_coupling_needed(self.In[iname].i, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        for iname, oxD in list(self._dd.items()):
            for kfrom in matrix_algorithm.port_set_get(self.In[iname].i):
                for oname, xfer in list(oxD.items()):
                    matrix_algorithm.port_coupling_insert(
                        self.In[iname].i,
                        kfrom,
                        self.O[oname].o,
                        kfrom,
                        xfer,
                    )
        return
