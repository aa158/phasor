"""
"""
from __future__ import division, print_function
from builtins import zip
import numpy as np

import declarative
from declarative import bunch
from ...math.complex import Complex

from . import visitors as VISIT

from declarative.substrate import (
    RootElement,
    invalidate_auto,
)

from .base import (
    FitterBase,
)


class FitterRoot(RootElement, FitterBase):

    @declarative.mproperty
    def _system_map(self, val = declarative.NOARG):
        if val is declarative.NOARG:
            val = None
        return val

    #maps names to systems
    @declarative.dproperty
    def systems(self):
        prefill = dict()
        if self.inst_preincarnation is not None:
            for sysname, sys in list(self.inst_preincarnation.systems.items()):
                newsys = self._system_map[sysname]
                prefill[sysname] = self._system_map[sysname]
                self._root_register(sysname, newsys)
        return bunch.HookBunch(
            prefill,
            insert_hook = self._root_register
        )

    #maps systems to names
    @declarative.mproperty
    def object_roots_inv(self):
        return dict()

    #maps systems to ooas
    @declarative.mproperty
    def meta_ooa(self):
        return dict()

    @declarative.mproperty
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
        for okey, odatum in list(self._registry_parameters.items()):
            okeyshort = okey[:len(pkey)]
            pkeyshort = pkey[:len(okey)]
            if okeyshort == pkeyshort and odatum is not fitter_datum:
                raise RuntimeError("Parameter Keys Must be Unique")
        #TODO, minimal checks on the fitter_datum included data
        self.invalidate()
        return

    @declarative.mproperty
    @invalidate_auto
    def fit_systems(self):
        ooa_meta = declarative.Bunch()
        for sysname in list(self.systems.keys()):
            ooa_meta[sysname] = bunch.DeepBunch(vpath=True)

        injectors = self.targets_recurse(VISIT.ooa_inject)
        for injector in injectors:
            injector(ooa_meta)

        systems = declarative.Bunch()
        for system, name in list(self.object_roots_inv.items()):
            new_obj = system.regenerate(
                ooa_params = ooa_meta[name],
            )
            systems[name] = new_obj
        return systems

    @declarative.mproperty
    @invalidate_auto
    def constraints(self):
        constraints = []
        for name, obj in list(self.fit_systems.items()):
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

        constraints_remapped = constraint_expr[:]
        for remapper in self.targets_recurse(VISIT.constraints_remap):
            constraints_remapped = remapper(constraints_remapped)

        ret = declarative.Bunch(
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
            try:
                shape = constraint.shape
            except AttributeError:
                pass
            else:
                ones = np.ones(shape)
                lb = ones * lb
                ub = ones * ub
            ret.lb.append(lb)
            ret.ub.append(ub)
        #TODO expression remapping on the constraints
        return ret

    @declarative.mproperty
    @invalidate_auto
    def symbol_map(self):
        smappers   = self.targets_recurse(VISIT.symbol_map)
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
                if isinstance(sbunch.symbol, Complex):
                    ival_list.append(sbunch.initial_value.real)
                    datum_list.append(sbunch.datum)
                    sym_list.append(sbunch.symbol.real)
                    ub_list.append(sbunch.get('upper_bound', float('inf')).real)
                    lb_list.append(sbunch.get('lower_bound', -float('inf')).real)
                    #not used in the current expressions and wont currently work with the
                    #complex symbols
                    #transform_list.append(sbunch.setdefault('transforms', []))
                    sbunch_list.append(sbunch)

                    ival_list.append(sbunch.initial_value.imag)
                    datum_list.append(sbunch.datum)
                    sym_list.append(sbunch.symbol.imag)
                    ub_list.append(sbunch.get('upper_boundI', float('inf')).imag)
                    lb_list.append(sbunch.get('lower_boundI', -float('inf')).imag)
                    #not used in the current expressions and wont currently work with the
                    #complex symbols
                    #transform_list.append(sbunch.setdefault('transforms', []))
                    sbunch_list.append(sbunch)
                else:
                    ival_list.append(sbunch.initial_value)
                    datum_list.append(sbunch.datum)
                    sym_list.append(sbunch.symbol)
                    ub_list.append(sbunch.get('upper_bound', float('inf')))
                    lb_list.append(sbunch.get('lower_bound', -float('inf')))
                    #not used in the current expressions and wont currently work with the
                    #complex symbols
                    #transform_list.append(sbunch.setdefault('transforms', []))
                    sbunch_list.append(sbunch)
        return declarative.Bunch(
            sym_list       = sym_list,
            ival_list      = ival_list,
            datum_list     = datum_list,
            lb_list        = lb_list,
            ub_list        = ub_list,
            sbunch_list    = sbunch_list,
            #transform_list = transform_list,
        )


