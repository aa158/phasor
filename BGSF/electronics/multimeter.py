"""
"""
from __future__ import division

import declarative as decl

from .. import readouts
from . import elements
from . import ports

class VoltageReadout(readouts.DCReadout, elements.ElectricalElementBase):

    @decl.dproperty
    def terminal(self, port):
        return port

    @decl.dproperty
    def terminal_N(self, port = None):
        return port

    @decl.dproperty
    def V(self):
        return ports.SignalPortHolderOut(self, x = 'V')

    @decl.dproperty
    def port(self):
        return self.V.o

    def system_setup_ports(self, ports_algorithm):
        #TODO hackish, need better system support for binding
        #this linear port into the readout ports
        ports = [self.terminal.i, self.terminal.o]
        if self.terminal_N is not None:
            ports.extend([self.terminal_N.i, self.terminal_N.o])
        for port1 in ports:
            #for kfrom in ports_algorithm.port_update_get(port1):
            #    ports_algorithm.port_coupling_needed(self.V.o, kfrom)
            for kto in ports_algorithm.port_update_get(self.V.o):
                ports_algorithm.port_coupling_needed(port1, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        #TODO, not sure about the 1/2 everywhere
        _2 = self.math.number(2)
        pcplgs = {
            self.system.ports_pre_get(self.terminal.i) : 1,
            self.system.ports_post_get(self.terminal.o) : 1,
        }
        if self.terminal_N is not None:
            pcplgs[self.terminal_N.i] = -1
            pcplgs[self.terminal_N.o] = -1
        for port, pcplg in pcplgs.items():
            for kfrom in matrix_algorithm.port_set_get(port):
                matrix_algorithm.port_coupling_insert(
                    port,
                    kfrom,
                    self.V.o,
                    kfrom,
                    pcplg,
                )


class CurrentReadout(readouts.DCReadout, elements.ElectricalElementBase):

    @decl.dproperty
    def direction(self, val):
        assert(val in ['in', 'out'])
        return val

    @decl.dproperty
    def terminal(self, port):
        return port

    @decl.dproperty
    def I(self):
        return ports.SignalPortHolderOut(self, x = 'I')

    @decl.dproperty
    def port(self):
        return self.I.o

    def system_setup_ports(self, ports_algorithm):
        #TODO hackish, need better system support for binding
        #this linear port into the readout ports
        ports = [self.terminal.i, self.terminal.o]
        for port1 in ports:
            #for kfrom in ports_algorithm.port_update_get(port1):
            #    ports_algorithm.port_coupling_needed(self.I.o, kfrom)
            for kto in ports_algorithm.port_update_get(self.I.o):
                ports_algorithm.port_coupling_needed(port1, kto)
        return

    def system_setup_coupling(self, matrix_algorithm):
        #TODO, not sure about the 1/2 everywhere
        _2 = self.math.number(2)
        pcplgs = {
            self.terminal.i :  1 / self.Z_termination,
            self.terminal.o : -1 / self.Z_termination,
        }
        direction_cplg = {'in' : 1, 'out' : -1}[self.direction]
        for port, pcplg in pcplgs.items():
            for kfrom in matrix_algorithm.port_set_get(port):
                matrix_algorithm.port_coupling_insert(
                    port,
                    kfrom,
                    self.I.o,
                    kfrom,
                    direction_cplg * pcplg,
                )


