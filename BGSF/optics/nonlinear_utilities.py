# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
from __future__ import print_function
#from YALL.utilities.print import print
#import numpy as np

from ..key_matrix import (
    DictKey,
)

from .ports import (
    QuantumKey,
    RAISE, LOWER,
    ClassicalFreqKey,
)


def ports_fill_2optical_2classical(
        system,
        ports_algorithm,
        ports_in_optical,
        ports_out_optical,
        pmap,
        in_port_classical,
        out_port_classical,
):
    for port in ports_in_optical:
        pfrom = port.i
        for ptoOpt in pmap[pfrom]:
            for kfrom in ports_algorithm.port_update_get(pfrom):
                ports_algorithm.port_coupling_needed(ptoOpt, kfrom)
        if in_port_classical is not None:
            for kfrom, lkfrom in ports_algorithm.symmetric_update(pfrom, in_port_classical.i):
                if kfrom.contains(LOWER):
                    ftoOptP = kfrom[ClassicalFreqKey] + lkfrom[ClassicalFreqKey]
                else:
                    ftoOptP = kfrom[ClassicalFreqKey] - lkfrom[ClassicalFreqKey]
                if system.reject_classical_frequency_order(ftoOptP):
                    continue
                ktoOptP = kfrom.without_keys(ClassicalFreqKey) | DictKey({ClassicalFreqKey: ftoOptP})

                ports_algorithm.prev_solution_needed(pfrom, kfrom)
                ports_algorithm.prev_solution_needed(in_port_classical.i, lkfrom)

                for ptoOpt in pmap[pfrom]:
                    ports_algorithm.port_coupling_needed(ptoOpt, ktoOptP)
                    ports_algorithm.port_coupling_needed(ptoOpt, kfrom)
                ports_algorithm.coherent_sources_perturb_needed(ptoOpt, ktoOptP)

        if out_port_classical is not None:
            for kfrom, lkto in ports_algorithm.symmetric_update(pfrom, out_port_classical.o):
                if kfrom.contains(LOWER):
                    fnew = kfrom[ClassicalFreqKey] - lkto[ClassicalFreqKey]
                    qKey = RAISE
                elif kfrom.contains(RAISE):
                    fnew = kfrom[ClassicalFreqKey] + lkto[ClassicalFreqKey]
                    qKey = LOWER
                if system.reject_classical_frequency_order(fnew):
                    continue
                kfrom2 = kfrom.without_keys(QuantumKey, ClassicalFreqKey) | DictKey({ClassicalFreqKey: fnew}) | qKey
                ports_algorithm.port_coupling_needed(pfrom, kfrom2)
                pass

    for port in ports_in_optical:
        pfrom = port.i
        def subset_second(pool2):
            setdict = dict()
            for kfrom2 in pool2:
                kfrom1_sm = kfrom2.without_keys(ClassicalFreqKey, QuantumKey)
                if kfrom2.contains(RAISE):
                    kfrom1_sm = kfrom1_sm | LOWER
                elif kfrom2.contains(LOWER):
                    kfrom1_sm = kfrom1_sm | RAISE
                group = setdict.setdefault(kfrom1_sm, [])
                group.append(kfrom2)
            def subset_func(kfrom1):
                kfrom1_sm = kfrom1.without_keys(ClassicalFreqKey)
                return setdict.get(kfrom1_sm, [])
            return subset_func
        for kfrom1, kfrom2 in ports_algorithm.symmetric_update(
                pfrom,
                pfrom,
                subset_second = subset_second
        ):
            if kfrom1.contains(LOWER):
                fdiff = kfrom1[ClassicalFreqKey] - kfrom2[ClassicalFreqKey]
            elif kfrom1.contains(RAISE):
                fdiff = kfrom2[ClassicalFreqKey] - kfrom1[ClassicalFreqKey]
            if system.reject_classical_frequency_order(fdiff):
                continue
            ports_algorithm.port_coupling_needed(
                out_port_classical.o,
                DictKey({ClassicalFreqKey: fdiff})
            )

    for port in ports_out_optical:
        pto = port.o
        for kto, lkfrom in ports_algorithm.symmetric_update(pto, out_port_classical.o):
            if kto.contains(LOWER):
                ffromOptP = kto[ClassicalFreqKey] - lkfrom[ClassicalFreqKey]
            else:
                ffromOptP = kto[ClassicalFreqKey] + lkfrom[ClassicalFreqKey]
            if system.reject_classical_frequency_order(ffromOptP):
                continue
            for pfromOpt in pmap[pto]:
                ports_algorithm.port_coupling_needed(
                    pfromOpt,
                    kto.without_keys(ClassicalFreqKey) | DictKey({ClassicalFreqKey: ffromOptP})
                )
                ports_algorithm.port_coupling_needed(
                    pfromOpt,
                    kto.without_keys(ClassicalFreqKey) | DictKey({ClassicalFreqKey: ffromOptP})
                )


def modulations_fill_2optical_2classical(
    system,
    matrix_algorithm,
    pfrom, kfrom,
    ptoOpt,
    in_port_classical,
    out_port_classical,
    Stdcplg,
    StdcplgC,
    CLcplg,
    CLcplgC,
    BAcplg,
    BAcplgC,
):
    if ptoOpt is not None and in_port_classical is not None:
        lkfroms = matrix_algorithm.port_set_get(in_port_classical.i)
    else:
        lkfroms = []
    lkfrom_completed = set()
    for lkfrom in lkfroms:
        #must check and reject already completed ones as the inject generates more lkfroms
        if lkfrom in lkfrom_completed:
            continue
        lk_freq = lkfrom[ClassicalFreqKey]
        assert(not lkfrom - DictKey({ClassicalFreqKey: lk_freq}))
        lk_freqN = -lk_freq
        if lk_freqN == lk_freq:
            #TODO: make the nonlinear system properly handle the DC cases
            continue
        lkfromN = DictKey({ClassicalFreqKey: lk_freqN})
        #print(pfrom.i, ptoOpt.o)
        #print(lkfromN, lkfroms)
        assert(lkfromN in lkfroms)
        lkfrom_completed.add(lkfrom)
        lkfrom_completed.add(lkfromN)

        if kfrom.contains(LOWER):
            kfrom_conj = (kfrom - LOWER) | RAISE
        else:
            kfrom_conj = (kfrom - RAISE) | LOWER

        optCplg  = (pfrom.i, kfrom)
        optCplgC = (pfrom.i, kfrom_conj)

        posCplgP = (in_port_classical.i, lkfrom)
        posCplgN = (in_port_classical.i, lkfromN)

        ftoOptP = kfrom[ClassicalFreqKey] + lkfrom[ClassicalFreqKey]
        ftoOptN = kfrom[ClassicalFreqKey] + lkfromN[ClassicalFreqKey]

        if not system.reject_classical_frequency_order(ftoOptP):
            ktoOptP = kfrom.without_keys(ClassicalFreqKey) | DictKey({ClassicalFreqKey: ftoOptP})
        else:
            ktoOptP = None

        if not system.reject_classical_frequency_order(ftoOptN):
            ktoOptN = kfrom.without_keys(ClassicalFreqKey) | DictKey({ClassicalFreqKey: ftoOptN})
        else:
            ktoOptN = None

        if kfrom.contains(LOWER):
            if ktoOptP is not None:
                matrix_algorithm.nonlinear_triplet_insert(
                    optCplg,
                    posCplgP,
                    (ptoOpt.o, ktoOptP),
                    Stdcplg * CLcplg
                )
            if ktoOptN is not None:
                matrix_algorithm.nonlinear_triplet_insert(
                    optCplg,
                    posCplgN,
                    (ptoOpt.o, ktoOptN),
                    Stdcplg * CLcplg
                )
        else:
            #TODO check
            if ktoOptP is not None:
                matrix_algorithm.nonlinear_triplet_insert(
                    optCplg,
                    posCplgN,
                    (ptoOpt.o, ktoOptP),
                    StdcplgC * CLcplgC
                )
            if ktoOptN is not None:
                matrix_algorithm.nonlinear_triplet_insert(
                    optCplg,
                    posCplgP,
                    (ptoOpt.o, ktoOptN),
                    StdcplgC * CLcplgC
                )
    if ptoOpt is not None:
        if kfrom.contains(LOWER):
            matrix_algorithm.port_coupling_insert(
                pfrom.i, kfrom, ptoOpt.o, kfrom,
                Stdcplg,
            )
        else:
            matrix_algorithm.port_coupling_insert(
                pfrom.i, kfrom, ptoOpt.o, kfrom,
                StdcplgC,
            )

    lktos = matrix_algorithm.port_set_get(out_port_classical.o)
    lkto_completed = set()
    for lkto in lktos:
        #must check and reject already completed ones as the inject generates more lktos
        if lkto in lkto_completed:
            continue
        lk_freq = lkto[ClassicalFreqKey]
        assert(not lkto - DictKey({ClassicalFreqKey: lk_freq}))
        lk_freqN = -lk_freq
        lktoN = DictKey({ClassicalFreqKey: lk_freqN})
        assert(lktoN in lktos)
        lkto_completed.add(lkto)
        lkto_completed.add(lktoN)

        if kfrom.contains(LOWER):
            kfrom_conj = (kfrom - LOWER) | RAISE
        else:
            kfrom_conj = (kfrom - RAISE) | LOWER

        optCplg  = (pfrom.i, kfrom)
        optCplgC = (pfrom.i, kfrom_conj)

        ftoOptP = kfrom[ClassicalFreqKey] + lkto[ClassicalFreqKey]
        ftoOptN = kfrom[ClassicalFreqKey] + lktoN[ClassicalFreqKey]

        if not system.reject_classical_frequency_order(ftoOptP):
            ktoOptP = kfrom.without_keys(ClassicalFreqKey) | DictKey({ClassicalFreqKey: ftoOptP})
        else:
            ktoOptP = None

        if not system.reject_classical_frequency_order(ftoOptN):
            ktoOptN = kfrom.without_keys(ClassicalFreqKey) | DictKey({ClassicalFreqKey: ftoOptN})
        else:
            ktoOptN = None
        #Both raising and lowering use optCplgC because it is always the conjugate to the other, so it always matches LOWER with the classical field of RAISE
        #and vice-versa
        if kfrom.contains(LOWER):
            #TODO Check factor of 2 overcounting here between raising and lowering
            if ktoOptP is not None:
                matrix_algorithm.port_coupling_insert(
                    pfrom.i, ktoOptP, out_port_classical.o, lkto,
                    Stdcplg * BAcplg / 2, optCplgC,
                )
            if lktoN != lkto and ktoOptN is not None:
                matrix_algorithm.port_coupling_insert(
                    pfrom.i, ktoOptN, out_port_classical.o, lktoN,
                    Stdcplg * BAcplg / 2, optCplgC,
                )
        elif kfrom.contains(RAISE):
            #TODO Check factor of 2 overcounting here between raising and lowering
            # because of conjugation issues, the frequencies are reversed in the lktos for the optical RAISE operators
            if ktoOptP is not None:
                matrix_algorithm.port_coupling_insert(
                    pfrom.i, ktoOptP, out_port_classical.o, lktoN,
                    StdcplgC * BAcplgC / 2, optCplgC,
                )
            if lktoN != lkto and ktoOptN is not None:
                matrix_algorithm.port_coupling_insert(
                    pfrom.i, ktoOptN, out_port_classical.o, lkto,
                    StdcplgC * BAcplgC / 2, optCplgC,
                )
        else:
            raise RuntimeError("Boo")
