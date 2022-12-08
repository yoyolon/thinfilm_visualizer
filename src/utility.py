import numpy as np
import csv

"""定数"""
START_WAVELENGTH = 400
END_WAVELENGTH = 700
NSAMPLESPECTRUM = 15
RANGE_WAVELENGTH = END_WAVELENGTH - START_WAVELENGTH
STEP_WAVELENGTH = RANGE_WAVELENGTH / NSAMPLESPECTRUM


def lerp(t, v1, v2):
    """
    線形補間

    Parameters
    ----------
    t : float
        補間パラメータ
    v1 : int
        補間する値
    v2 : int
        補間する値
    """
    return (1-t) * v1 + t * v2


def load_spd(filename):
    """
    CVSファイルからSPDデータを読み込む

    Parameters
    ----------
    filename : string
        CSVファイルのパス

    Returns
    -------
    wl : ndarray
        波長配列
    v : ndarray
        値配列

    Notes
    -----
    CSVファイルは1列目が波長で2列目が波長に対応する値
    """
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        wl = np.empty(0)
        v = np.empty(0)
        for row in reader:
            wl = np.append(wl, float(row[0]))
            v = np.append(v, float(row[1]))
    return wl, v


def load_cmf(filename):
    """
    CVSファイルから等色関数データを読み込む

    Parameters
    ----------
    filename : string
        CSVファイルのパス

    Returns
    -------
    wl : ndarray
        波長配列
    xyz : ndarray
        等色関数配列

    Notes
    -----
    CSVファイルは1列目が波長で2-4列目が波長に対応するXYZ等色関数
    RGB値はガンマ補正前と仮定
    """
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        wl = np.empty(0)
        xyz = np.empty((0,3))
        for row in reader:
            wl = np.append(wl, float(row[0]))
            temp = np.array([[float(row[1]), float(row[2]), float(row[3])]])
            xyz = np.append(xyz, temp, axis=0)
        xyz = np.transpose(xyz)
    return wl, xyz


def xyz_to_rgb(xyz):
    """
    XYZ三刺激値からRGB値へ変換

    Parameters
    ----------
    xyz : ndarray
        XYZ値

    Returns
    -------
    rgb : ndarray
        RGB値

    Notes
    -----
    XYZはCIE-XYZ表色系をRGBはsRGB色空間を採用
    RGB値はガンマ補正前と仮定
    """
    rgb = np.empty(3)
    rgb[0] =  3.2406*xyz[0] + -1.5372*xyz[1] + -0.4986*xyz[2]
    rgb[1] = -0.9689*xyz[0] +  1.8758*xyz[1] +  0.0415*xyz[2]
    rgb[2] =  0.0557*xyz[0] + -0.2040*xyz[1] +  1.0570*xyz[2]
    return rgb


def rgb_to_xyz(rgb):
    """
    RGB値からXYZ三刺激値へ変換

    Parameters
    ----------
    rgb : ndarray
        RGB値

    Returns
    -------
    xyz : ndarray
        XYZ値

    Notes
    -----
    XYZはCIE-XYZ表色系をRGBはsRGB色空間を採用
    RGB値はガンマ補正前と仮定
    """
    xyz = np.empty(3)
    xyz[0] = 0.4124*rgb[0] + 0.3576*rgb[1] + 0.1805*rgb[2]
    xyz[1] = 0.2126*rgb[0] + 0.7152*rgb[1] + 0.0722*rgb[2]
    xyz[2] = 0.0193*rgb[0] + 0.1192*rgb[1] + 0.9505*rgb[2]
    return rgb


def to_radian(deg):
    """
    度数法から弧度法に変換

    Parameters
    ----------
    deg : float
        度数法の角度
    """
    return deg / 180.0 * np.pi


def to_degree(rad):
    """
    弧度法から度数法に変換

    Parameters
    ----------
    rad : float
        弧度法の角度
    """
    return rad / np.pi * 180