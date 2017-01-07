from __future__ import division
from __future__ import print_function
from YALL.utilities.print import print

import numpy as np


def stackrange(rangetup):
    rangestack = []
    for v in rangetup:
        try:
            iter(v)
        except TypeError:
            rangestack.append(range(v))
        else:
            rangestack.append(v)

    iterstack = [iter(rangestack[0])]
    tupstack = [()]
    while True:
        while len(iterstack) < len(rangestack):
            if not iterstack:
                break
            try:
                nval = iterstack[-1].next()
                tupstack.append(tupstack[-1] + (nval,))
                iterstack.append(iter(rangestack[len(iterstack)]))
            except StopIteration:
                iterstack.pop()
                tupstack.pop()
                continue
        if not iterstack:
            break

        ptup = tupstack.pop()
        for v in iterstack.pop():
            yield ptup + (v,)


def linalg_solve_bcast(M, V):
    #print(M.shape, V.shape)
    #assert(M.shape[2:] == V.shape[1:])
    if M.shape[:-2] == () and V.shape[:-1] == ():
        return np.linalg.solve(M, V)
    else:
        b = np.broadcast(M[..., 0, 0], V[..., 0])
        rtype = np.find_common_type([], [M.dtype, V.dtype])
        rvec = np.empty(b.shape + M.shape[-1:], dtype = rtype)
        idx = 0
        for idx in stackrange(b.shape):
            idxM = tuple((0 if iM == 1 else iB) for iM, iB in zip(M.shape[:-2], idx))
            idxV = tuple((0 if iV == 1 else iB) for iV, iB in zip(V.shape[:-1], idx))
            Mred = M[idxM + (slice(None), slice(None))]
            Vred = V[idxV + (slice(None),)]
            Vsol = np.linalg.solve(Mred, Vred)
            rvec[idx + (slice(None),)] = Vsol
        return rvec
