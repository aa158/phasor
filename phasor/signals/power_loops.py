"""
"""
import scipy.signal
import numpy as np

#from phasor.utilities.np import logspaced


def cheby_boost_7(
    F_center = 1.,
    shift = 5.,
):
    F_center = float(F_center)
    N = 7
    z = []
    p = []
    k = 1

    zpk_cheby = scipy.signal.cheby1(N, .2, 1, analog = True, output = 'zpk')
    z.extend(zpk_cheby[1])
    p.extend(zpk_cheby[0])
    k = k / zpk_cheby[2]

    z.append(-1 + 1j)
    p.append(-.1 + 1j)

    p.extend([-.01] * N)

    z = F_center/shift * np.asarray(z)
    p = F_center/shift * np.asarray(p)
    k = F_center/shift * np.asarray(k)

    Fx, hd = scipy.signal.freqresp(
        (z, p, k,),
        F_center
    )
    k = k / abs(hd)
    return z, p, k


def ledge_controller(
    F_center = 1.,
    shift = 5.,
    N = 3,
):
    F_center = float(F_center)
    z = []
    p = []
    k = 1

    zpk_cheby = scipy.signal.cheby1(N, .3, 1, analog = True, output='zpk')
    z.extend(zpk_cheby[1])
    p.extend(zpk_cheby[0])
    k = k / zpk_cheby[2]

    zpk_cheby = scipy.signal.cheby1(N+2, .3, 1.00, analog = True, output='zpk')
    z.extend(zpk_cheby[0])
    p.extend(zpk_cheby[1])
    k = k * zpk_cheby[2]

    zpk_cheby = scipy.signal.butter(2, 2, analog = True, output='zpk')
    z.extend(zpk_cheby[1])
    p.extend(zpk_cheby[0])
    k = k / zpk_cheby[2]

    zpk_cheby = scipy.signal.cheby1(1, 1, 3, analog = True, output='zpk')
    z.extend(zpk_cheby[0])
    p.extend(zpk_cheby[1])
    k = k * zpk_cheby[2]

    z = F_center/shift * np.asarray(z)
    p = F_center/shift * np.asarray(p)
    k = F_center/shift * np.asarray(k)

    Fx, hd = scipy.signal.freqresp(
        (z, p, k,),
        F_center
    )
    k = k / abs(hd)
    return z, p, k


def ledge_boost(
    F_center = 1.,
    shift = 5.,
    N = 3,
):
    F_center = float(F_center)
    z = []
    p = []
    k = 1

    zpk_cheby = scipy.signal.cheby1(N, .3, 1, analog = True, output='zpk')
    z.extend(zpk_cheby[1])
    p.extend(zpk_cheby[0])
    k = k / zpk_cheby[2]

    zpk_cheby = scipy.signal.cheby1(N+2, .3, 1.00, analog = True, output='zpk')
    z.extend(zpk_cheby[0])
    p.extend(zpk_cheby[1])
    k = k * zpk_cheby[2]

    zpk_cheby = scipy.signal.butter(3, 2, analog = True, output='zpk')
    z.extend(zpk_cheby[1])
    p.extend(zpk_cheby[0])
    k = k / zpk_cheby[2]

    zpk_cheby = scipy.signal.cheby1(1, 1, 3, analog = True, output='zpk')
    z.extend(zpk_cheby[0])
    p.extend(zpk_cheby[1])
    k = k * zpk_cheby[2]

    p.append(-1.2+1.5j)
    z.append(-2+1.5j)
    p.append(-1.5+1.5j)
    z.append(-3+1.5j)

    z = F_center/shift * np.asarray(z)
    p = F_center/shift * np.asarray(p)
    k = F_center/shift * np.asarray(k)

    Fx, hd = scipy.signal.freqresp(
        (z, p, k,),
        F_center
    )
    k = k / abs(hd)
    return z, p, k


def cheby_boost(
    F_center = 1.,
    shift = 5.,
):
    F_center = float(F_center)
    N_tot = 0
    z = []
    p = []
    k = 1

    N_tot += 3
    zpk_cheby = scipy.signal.cheby1(3, .2, .8, analog = True, output = 'zpk')
    z.extend(zpk_cheby[1])
    p.extend(zpk_cheby[0])
    k = k / zpk_cheby[2]

    N_tot += 3
    zpk_cheby = scipy.signal.cheby1(3, .2, 1, analog = True, output = 'zpk')
    z.extend(zpk_cheby[1])
    p.extend(zpk_cheby[0])
    k = k / zpk_cheby[2]

    z.append(-.7 + 1j)
    p.append(-.2 + 1j)
    #z.append(-.5 + .8j)
    #p.append(-.2 + .8j)

    p.extend([-.01] * N_tot)

    z = F_center/shift * np.asarray(z)
    p = F_center/shift * np.asarray(p)
    k = F_center/shift * np.asarray(k)

    Fx, hd = scipy.signal.freqresp(
        (z, p, k,),
        F_center
    )
    k = k / abs(hd)
    return z, p, k


def zpk_mult(*zpks):
    zs = []
    ps = []
    ks = 1
    for (z, p, k) in zpks:
        zs.append(z)
        ps.append(p)
        ks = ks * k
    zs = np.concatenate(zs)
    ps = np.concatenate(ps)
    return zs, ps, ks


def zpk_div(zpkN, zpkD):
    zs = []
    ps = []
    ks = 1
    zs.append(zpkN[0])
    ps.append(zpkN[1])
    ks = ks * zpkN[2]

    zs.append(zpkD[1])
    ps.append(zpkD[0])
    ks = ks / zpkD[2]

    zs = np.concatenate(zs)
    ps = np.concatenate(ps)
    return zs, ps, ks


def controller_10x1e3_20x1e8(UGF):
    """
    Controller with prodigious gain
    """
    return zpk_mult(
        ledge_controller(F_center = UGF, shift = 15., N =3),
        ledge_boost(F_center = UGF, shift = 15., N =3),
        ledge_boost(F_center = UGF, shift = 20., N =3),
        ledge_boost(F_center = UGF, shift = 15., N =3),
        ledge_boost(F_center = UGF, shift = 20., N =3),
        ((-UGF,), (0,), .7)
    )

def controller_20x1e9(UGF):
    """
    Controller with prodigious gain
    """
    return zpk_mult(
        ledge_controller(F_center = UGF, shift = 20., N =3),
        ledge_boost(F_center = UGF, shift = 20., N =3),
        ledge_boost(F_center = UGF, shift = 20., N =3),
        ledge_boost(F_center = UGF, shift = 20., N =3),
        ledge_boost(F_center = UGF, shift = 25., N =3),
        ledge_boost(F_center = UGF, shift = 25., N =3),
        ledge_boost(F_center = UGF, shift = 25., N =3),
        ((-UGF,), (-.01,), .7),
    )


def sort_roots(rootlist):
    real_roots = []
    cplx_pos_roots = []
    cplx_neg_roots = []
    for root in rootlist:
        Q_ratio = root.imag / root.real
        #then the imaginary part is not resolved, so drop it
        if abs(Q_ratio) < 1e-8:
            real_roots.append(root.real)
        elif root.imag > 0:
            cplx_pos_roots.append(root)
        else:
            cplx_neg_roots.append(root)
    return real_roots, cplx_pos_roots, cplx_neg_roots


def zpk2rcpz_dict(zpk):
    z, p, k = zpk
    zr, zp, zn = sort_roots(z)
    pr, pp, pn = sort_roots(p)
    return dict(
        poles_r = pr,
        poles_c = pp,
        zeros_r = zr,
        zeros_c = zp,
        gain    = k,
    )



