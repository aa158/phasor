# -*- coding: utf-8 -*-
from __future__ import (division, print_function)
from builtins import object

import declarative as declarative

from ..base import visitors as VISIT

from ..base.ports import(
    DictKey,
    FrequencyKey,
    ElementKey,
    PortKey,
    MechKey,
    ClassicalFreqKey,
    PortHolderInBase,
    PortHolderOutBase,
    PortHolderInOutBase,
    MechanicalPortHolderIn,
    MechanicalPortHolderOut,
)  # NOQA

from ..signals.ports import(
    SignalPortHolderIn,
    SignalPortHolderOut,
)

from . import bases

QuantumKey = u'Ψ'
RAISE = DictKey({QuantumKey: u'↑'})
LOWER = DictKey({QuantumKey: u'↓'})

PolKEY = u'⤱'
PolS = DictKey({PolKEY: 'S'})
PolP = DictKey({PolKEY: 'P'})

OpticalFreqKey = u'F⇝'


class OpticalDegenerate4PortMixin(object):

    @declarative.dproperty
    def AOI_deg(self, val = 0):
        val = self.ooa_params.setdefault('AOI_deg', val)
        return val

    @declarative.mproperty
    def is_4_port(self):
        if self.AOI_deg == 0:
            val = False
        else:
            val = True
        return val


class OpticalRawPortHolder(bases.SystemElementBase):
    @declarative.dproperty
    def sname(self, val = declarative.NOARG):
        if val is declarative.NOARG:
            val = self.name_child
        return val

    @declarative.dproperty
    def element(self):
        return self.parent

    @declarative.dproperty
    def i(self):
        pkey = DictKey({
            ElementKey : self.element,
            PortKey    : self.sname + u'⥳',
        })
        self.system.port_add(self.element, pkey)
        return pkey

    @declarative.dproperty
    def o(self):
        pkey = DictKey({
            ElementKey: self.element,
            PortKey   : self.sname + u'⥲',
        })
        self.system.port_add(self.element, pkey)
        return pkey


class OpticalPort(OpticalRawPortHolder, bases.SystemElementBase):
    _bond_partner = None

    @declarative.mproperty
    def bond_key(self):
        return self

    def bond(self, other):
        self.bond_inform(other.bond_key)
        other.bond_inform(self)

    def bond_inform(self, other_key):
        #TODO make this smarter
        if self._bond_partner is not None:
            raise RuntimeError("Multiple Bond Partners not Allowed")
        else:
            self._bond_partner = other_key

    def bond_completion(self):
        #it should have been autoterminated if anything
        assert(self._bond_partner is not None)

        #TODO make a system algorithm object for this
        self.system.bond_completion_raw((self, self._bond_partner), self)
        return

    def targets_list(self, typename):
        if typename == VISIT.bond_completion:
            #TODO make a system algorithm object for this
            self.bond_completion()
            return self
        elif typename == VISIT.auto_terminate:
            if self._bond_partner is None:
                from .vacuum import VacuumTerminator
                self.my.terminator = VacuumTerminator()
                self.system.bond(self, self.terminator.Fr)
                return (self, self.terminator)
        else:
            return super(OpticalPort, self).targets_list(typename)

    pchain = None

    @declarative.mproperty
    def chain_next(self):
        if self.pchain is not None:
            if isinstance(self.pchain, str):
                return getattr(self.element, self.pchain)
            elif callable(self.pchain):
                return self.pchain()
            else:
                return self.pchain
        else:
            return None


class OpticalPortHolderCarrier(bases.SystemElementBase):
    def inner_port(self, port):
        return port

    def bond(self, other):
        self.inner_port.bond(other)

    def bond_inform(self, other_key):
        self.inner_port.bond_inform(other_key)

    def bond_completion(self):
        return self.inner_port.bond_completion()

    pchain = None

    @declarative.mproperty
    def chain_next(self):
        if self.pchain is not None:
            if isinstance(self.pchain, str):
                return getattr(self.element, self.pchain)
            elif callable(self.pchain):
                return self.pchain()
            else:
                return self.pchain
        else:
            return None







