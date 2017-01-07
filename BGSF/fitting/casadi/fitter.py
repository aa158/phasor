"""
"""
from __future__ import division, print_function
import numpy as np

from . import visitors as VISIT

from declarative import (
    dproperty,
    NOARG,
    mproperty,
    Bunch,
)

from declarative.bunch import (
    DeepBunch,
    HookBunch,
)

from ..bases import (
    RootElement,
    invalidate_auto,
)

from .base import (
    FitterBase,
)


class FitterRoot(RootElement, FitterBase):

    @mproperty
    def _system_map(self, val = NOARG):
        if val is NOARG:
            val = None
        return val

    #maps names to systems
    @dproperty
    def systems(self):
        prefill = dict()
        if self.inst_preincarnation is not None:
            for name, sys in self.inst_preincarnation.systems.iteritems():
                newsys = self._system_map[sys]
                prefill[name] = self._system_map[sys]
                self._root_register(name, newsys)
        return HookBunch(
            prefill,
            insert_hook = self._root_register
        )

    #maps systems to names
    @mproperty
    def object_roots_inv(self):
        return dict()

    #maps systems to ooas
    @mproperty
    def meta_ooa(self):
        return dict()

    @mproperty
    def _registry_parameters(self):
        return dict()

    def _root_register(self, name, system):
        self.object_roots_inv[system] = name
        self.meta_ooa[name] = system.ooa_params
        self.invalidate()
        return

    def parameter_add(self, system, fitter_datum):
        pkey = fitter_datum.parameter_key
        if system not in self.object_roots_inv:
            raise RuntimeError("Must register system")
        for okey, odatum in self._registry_parameters.iteritems():
            okeyshort = okey[:len(pkey)]
            pkeyshort = pkey[:len(okey)]
            if okeyshort == pkeyshort and odatum is not fitter_datum:
                raise RuntimeError("Parameter Keys Must be Unique")
        #TODO, minimal checks on the fitter_datum included data
        self.invalidate()
        return

    @mproperty
    @invalidate_auto
    def fit_systems(self):
        ooa_meta = Bunch()
        for sysname in self.systems.iterkeys():
            ooa_meta[sysname] = DeepBunch(vpath=True)

        injectors = self.targets_recurse('ooa_inject')
        for injector in injectors:
            injector(ooa_meta)

        systems = Bunch()
        for system, name in self.object_roots_inv.iteritems():
            new_obj = system.regenerate(
                ooa_params = ooa_meta[name],
            )
            systems[name] = new_obj
        return systems

    @mproperty
    @invalidate_auto
    def constraints(self):
        constraints = []
        for name, obj in self.fit_systems.iteritems():
            try:
                clist = obj.constraints
            except AttributeError:
                continue
            constraints.extend(clist)
        constraint_expr = []
        constraint_lb = []
        constraint_ub = []
        for expr, lb, ub in constraints:
            constraint_expr.append(expr)
            constraint_lb.append(lb)
            constraint_ub.append(ub)

        constraints_remapped = []
        for remapper in self.targets_recurse(VISIT.constraints_remap):
            for constraint in constraint_expr:
                constraint = remapper(constraint_expr)
            constraints_remapped.append(constraint)

        ret = Bunch(
            expr = [],
            lb   = [],
            ub   = [],
        )
        for constraint, lb, ub in zip(
            constraints_remapped,
            constraint_lb,
            constraint_ub
        ):
            ret.expr.append(constraint)
            ones = np.ones(constraint.shape)
            lb = ones * lb
            ub = ones * ub
            ret.lb.append(lb)
            ret.ub.append(ub)
        #TODO expression remapping on the constraints
        return ret

    @mproperty
    @invalidate_auto
    def symbol_map(self):
        smappers   = self.targets_recurse('symbol_map')
        sym_list   = []
        ival_list  = []
        datum_list = []
        lb_list    = []
        ub_list    = []
        transform_list = []
        sbunch_list = []
        for smapper in smappers:
            for sbunch in smapper():
                #TODO check sizes of ival and syms
                ival_list.append(sbunch.initial_value)
                datum_list.append(sbunch.datum)
                sym_list.append(sbunch.symbol)
                ub_list.append(sbunch.get('upper_bound', float('inf')))
                lb_list.append(sbunch.get('lower_bound', -float('inf')))
                transform_list.append(sbunch.setdefault('transforms', []))
                sbunch_list.append(sbunch)
        return Bunch(
            sym_list       = sym_list,
            ival_list      = ival_list,
            datum_list     = datum_list,
            lb_list        = lb_list,
            ub_list        = ub_list,
            sbunch_list    = sbunch_list,
            transform_list = transform_list,
        )


