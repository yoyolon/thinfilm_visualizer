import numpy as np


def cmf_x_simple(wl):
    """
    XYZ等色関数(CIE 1931)のX成分の近似を計算する関数

    Parameters
    ----------
    lambda : float
        波長

    Returns
    -------
    x : 波長に対応する等色関数の値

    Notes
    -----
    [Wyman 2013]を実装
    """
    x = (1.065 * np.exp(-0.5 * ((wl - 595.8) / 33.33) ** 2)
        +0.366 * np.exp(-0.5 * ((wl - 446.8) / 19.44) ** 2))
    return x


def cmf_y_simple(wl):
    """
    XYZ等色関数(CIE 1931)のY成分の近似を計算する関数

    Parameters
    ----------
    lambda : float
        波長

    Returns
    -------
    y : 波長に対応する等色関数の値

    Notes
    -----
    [Wyman 2013]を実装
    """
    y = 1.014 * np.exp(-0.5 * ((np.log(wl) - np.log(556.3)) / 0.075) ** 2)
    return y


def cmf_z_simple(wl):
    """
    XYZ等色関数(CIE 1931)のZ成分の近似を計算する関数

    Parameters
    ----------
    lambda : float
        波長

    Returns
    -------
    z : 波長に対応する等色関数の値

    Notes
    -----
    [Wyman 2013]を実装
    """
    z = 1.839 * np.exp(-0.5 * ((np.log(wl) - np.log(449.8)) / 0.051) ** 2)
    return z