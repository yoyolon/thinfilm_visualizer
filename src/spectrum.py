import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from PIL import Image, ImageTk
import os
from utility import *
from config import *


class Spectrum:
    """
    スペクトルを表現するクラス

    Attributes
    ----------
    __c : ndarray
        波長に対応する値
    __wl : ndarray
        波長
    __name : string
        プロット時の名前
    """


    def __init__(self, wl=None, v=None, constv=None, name='test'):
        """
        コンストラクタ

        Parameters
        ----------
        wl : ndarray
            波長
        v : ndarray
            波長に対応する値
        constv : float
            スペクトルが一定の場合の値
        name : string
            プロット時の名前
        """
        self.__c = np.zeros(NSAMPLESPECTRUM)
        self.__wl = np.zeros(NSAMPLESPECTRUM)
        self.__wl_mod = np.zeros(NSAMPLESPECTRUM)        
        self.__name = name
        step = (END_WAVELENGTH - START_WAVELENGTH) / NSAMPLESPECTRUM
        for i in range(NSAMPLESPECTRUM):
            self.__wl[i] = START_WAVELENGTH+ step * i
            self.__wl_mod[i] = START_WAVELENGTH+ step * i + step * 0.5
        # 波長と値のペアが与えられた場合
        if (wl is not None and v is not None):
            self.from_sample(wl, v)         
        # 定数がえられた場合
        elif (constv is not None):
            self.__c = np.full(NSAMPLESPECTRUM, constv)
            
            
    @property
    def c(self):
        return self.__c
    
    @property
    def wl(self):
        return self.__wl
    
    @property
    def wl_mod(self):
        return self.__wl_mod
    
    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self, name):
        self.__name = name
    
    
    def __add__(self, other):
        if type(other) == Spectrum:
            return Spectrum(self.wl_mod, self.c + other.c)
        else:
            raise TypeError()
    
    def __sub__(self, other):
        if type(other) == Spectrum:
            return Spectrum(self.wl_mod, self.c - other.c)
        else:
            raise TypeError()
    
    def __mul__(self, other):
        if type(other) == Spectrum:
            return Spectrum(self.wl_mod, self.c * other.c)
        else:
            return Spectrum(self.wl_mod, self.c * other)            
            
    def __rmul__(self, other):
        if type(other) == Spectrum:
            return Spectrum(self.wl_mod, self.c * other.c)
        else:
            return Spectrum(self.wl_mod, self.c * other)              
            
    def __truediv__(self, other):
        if type(other) == Spectrum:
            if (not other.is_zero_div()):
                raise ZeroDivisionError()
            return Spectrum(self.wl_mod, self.c / other.c)
        else:
            return Spectrum(self.wl_mod, self.c / other)
    
    def __getitem__(self, key):
        return self.c[key]
    
    

    def from_sample(self, wl, v):
        """
        波長と値のサンプルからスペクトルを生成

        Parameters
        ----------
        wl : ndarray
            波長
        v : ndarray
            波長に対応する値
        """
        samples = {key: val for key, val in zip(wl, v)}
        samples = sorted(samples.items())
        samples = np.array(samples)
        samples = np.transpose(samples)
        wl, v = samples[0], samples[1]
        # サンプルの補間
        for i in range(NSAMPLESPECTRUM):
            lambda0 = lerp(i/NSAMPLESPECTRUM, START_WAVELENGTH, END_WAVELENGTH)
            lambda1 = lerp((i+1)/NSAMPLESPECTRUM, START_WAVELENGTH, END_WAVELENGTH)
            self.__c[i] = np.interp((lambda0+lambda1)*0.5, wl, v)

            
    def to_xyz(self):
        """
        SPDをXYZ三刺激値に変換

        Returns
        -------
        xyz : 変換後のXYZ三刺激値
        """
        xyz = np.empty(3)
        xyz[0] = np.sum(X.c * self.c)
        xyz[1] = np.sum(Y.c * self.c)
        xyz[2] = np.sum(Z.c * self.c)
        scale = (END_WAVELENGTH -START_WAVELENGTH) / (NSAMPLESPECTRUM * Y_luminance)
        xyz *= scale
        return xyz
    
    
    def to_rgb(self):
        """
        SPDをRGB値に変換

        Returns
        -------
        rgb : 変換後のRGB値
        """
        xyz = self.to_xyz()
        rgb = xyz_to_rgb(xyz)
        return rgb
    

    def is_black(self):
        """ゼロ判定"""
        return np.all(self.c == 0)
    

    def is_zero_div(self):
        """ゼロ除算判定"""
        return np.count_nonzero(self.c)


# XYZ等色関数の生成
path_xyz = os.path.join('data', 'cmf', 'ciexyz31.csv')
wl, xyz = load_cmf(path_xyz)
X = Spectrum(wl, xyz[0], name='X')
Y = Spectrum(wl, xyz[1], name='Y')
Z = Spectrum(wl, xyz[2], name='Z')
# 1nmサンプリングの輝度成分
Y_luminance = np.sum(Y.c) * (END_WAVELENGTH-START_WAVELENGTH) / NSAMPLESPECTRUM