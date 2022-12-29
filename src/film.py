import os
from spectrum import *
from utility import *

def fresnel_rp(cos0, cos1, n0, n1):
    """
    界面でのp偏光のフレネル反射係数

    Parameters
    ----------
    cos0 : float
        界面への入射角
    cos1 : float
        界面での屈折角
    n0 : float
        入射方向の媒質の屈折率
    n1 : float
        屈折方向の媒質の屈折率
    """
    return (n1*cos0 - n0*cos1) / (n1*cos0 + n0*cos1)


def fresnel_rs(cos0, cos1, n0, n1):
    """
    界面でのs偏光のフレネル反射係数

    Parameters
    ----------
    cos0 : float
        界面への入射角
    cos1 : float
        界面での屈折角
    n0 : float
        入射方向の媒質の屈折率
    n1 : float
        屈折方向の媒質の屈折率
    """
    return (n0*cos0 - n1*cos1) / (n0*cos0 + n1*cos1)


def fresnel_tp(cos0, cos1, n0, n1):
    """
    界面でのp偏光のフレネル透過係数

    Parameters
    ----------
    cos0 : float
        界面への入射角
    cos1 : float
        界面での屈折角
    n0 : float
        入射方向の媒質の屈折率
    n1 : float
        屈折方向の媒質の屈折率
    """
    return (2*n0*cos0) / (n1*cos0 + n1*cos1)


def fresnel_ts(cos0, cos1, n0, n1):
    """
    界面でのs偏光のフレネル透過係数

    Parameters
    ----------
    cos0 : float
        界面への入射角
    cos1 : float
        界面での屈折角
    n0 : float
        入射方向の媒質の屈折率
    n1 : float
        屈折方向の媒質の屈折率
    """
    return (2*n0*cos0) / (n0*cos0 + n1*cos1)


def irid_r(r01, r10, r12, t01, t10, phi):
    """
    干渉を考慮した反射係数

    Parameters
    ----------
    r01 : complex
        入射媒質から薄膜へ進む光の反射係数
    r10 : complex
        薄膜から入射媒質へ進む光の反射係数
    r12 : complex
        出射媒質から薄膜へ進む光の反射係数
    t01 : complex
        入射媒質から薄膜へ進む光の透過係数
    t10 : complex
        薄膜から入射媒質へ進む光の透過係数
    phi : float
        一回の反射で生じる位相差

    Returns
    -------
    r : complex
        薄膜干渉による反射率

    Notes
    -----
    等比数列の和を利用
    Reference: [木下 2010] p.73
    """
    k = 1 - r10 * r12 * np.exp(1.j*phi)
    r = r01 + (t01 * r12 * t10 * np.exp(1.j*phi)) / k
    return r



class ThinFilm:
    """
    薄膜クラス
    
    Attributes
    ----------
    __d : float
        膜厚
    __eta : Spectrum
        薄膜の屈折率
    __kappa : Spectrum
        薄膜の消衰係数
    """

    def __init__(self, d, eta, kappa):
        """
        初期化

        Parameters
        ----------
        d : float
            膜厚
        eta : Spectrum
            屈折率
        kappa : Spectrum
            消衰係数
        """
        self.__d = d
        self.__eta = eta
        self.__kappa = kappa
    

    @property
    def d(self):
        return self.__d
    
    @property
    def eta(self):
        return self.__eta
    
    @property
    def kappa(self):
        return self.__kappa



class Irid:
    """
    薄膜干渉計算クラス
    
    Attributes
    ----------
    __films : list of Film
        薄膜層の配列
    """
    
    def __init__(self, films):
        """
        初期化

        Parameters
        ----------
        films : list of FIlm
            薄膜層の配列
        """
        self.__films = films
    

    @property
    def films(self):
        return self.__films

    @films.setter
    def films(self, f):
        self.__films = f
        
    
    def evaluate(self, cos_in):
        """
        薄膜干渉の分光反射率を計算

        Parameters
        ----------
        cos_in : float
            入射角余弦

        Returns
        -------
        spd : Spectrum
            薄膜干渉の分光反射率

        Notes
        -----
        単層薄膜を仮定
        自作クラスのndarrayやcomplexが使えないため直接計算
        """
        sin_in = np.sqrt(max(0, 1 - cos_in**2))
        index = 0
        cos_theta_array = np.zeros([len(self.films), NSAMPLESPECTRUM]) # 各層への入射角の余弦
        etaI = self.films[0].eta
        # 各層への入射角余弦を計算
        for film in self.films:
            cos_theta = np.zeros([NSAMPLESPECTRUM])
            for i in range(NSAMPLESPECTRUM):
                # スネルの法則から屈折角余弦を計算
                sin_theta = etaI[i] * sin_in / complex(film.eta[i], film.kappa[i])
                if (sin_theta.real**2 + sin_theta.imag**2 > 1): # 全反射
                    return Spectrum()
                cos_theta[i] = np.sqrt(max(0, 1. - sin_theta**2)) # i番目の波長帯での入射角余弦
            cos_theta_array[index] = cos_theta
            index = index + 1
        # 波長生成
        step = (END_WAVELENGTH - START_WAVELENGTH) / NSAMPLESPECTRUM
        wl = np.zeros(NSAMPLESPECTRUM)
        for i in range(NSAMPLESPECTRUM):
            wl[i] = START_WAVELENGTH + step/2 + i*step
        # 反射率計算
        rp = np.zeros(NSAMPLESPECTRUM, dtype=complex) # p偏光の反射係数
        rs = np.zeros(NSAMPLESPECTRUM, dtype=complex) # s偏光の反射係数
        for j in range(NSAMPLESPECTRUM):
            cos0 = cos_theta_array[0][j]
            cos1 = cos_theta_array[1][j]
            cos2 = cos_theta_array[2][j]
            n0 = complex(self.films[0].eta[j], self.films[0].kappa[j])
            n1 = complex(self.films[1].eta[j], self.films[1].kappa[j])
            n2 = complex(self.films[2].eta[j], self.films[2].kappa[j])
            # フレネル係数計算
            rp01 = fresnel_rp(cos0, cos1, n0, n1)
            rs01 = fresnel_rs(cos0, cos1, n0, n1)
            rp10 = fresnel_rp(cos1, cos0, n1, n0)
            rs10 = fresnel_rs(cos1, cos0, n1, n0)
            rp12 = fresnel_rp(cos1, cos2, n1, n2)
            rs12 = fresnel_rs(cos1, cos2, n1, n2)
            tp01 = fresnel_tp(cos0, cos1, n0, n1)
            ts01 = fresnel_ts(cos0, cos1, n0, n1)
            tp10 = fresnel_tp(cos1, cos0, n1, n0)
            ts10 = fresnel_ts(cos1, cos0, n1, n0)
            phi = 4 * np.pi * self.films[1].d / wl[j] * n1 * cos1 # 位相差
            rp[j] = irid_r(rp01, rp10, rp12, tp01, tp10, phi)
            rs[j] = irid_r(rs01, rs10, rs12, ts01, ts10, phi)
        v = (np.abs(rp)**2 + np.abs(rs)**2) / 2
        spd = Spectrum(wl, v)
        return spd
        
        
    def create_texture(self, width=270, height=90):
        """
        入射角が0-90度の反射率テクスチャを作成

        Parameters
        ----------
        width : int
            テクスチャ画像の幅
        height : int
            テクスチャ画像の高さ

        Returns
        -------
        img : ndarray
            RGB値の反射率テクスチャ
        
        """
        img = np.zeros([height, width, 3])
        invstep = width / 90
        for i in range (width):
            temp = self.evaluate(np.cos(np.pi/180 * i/invstep))
            temp = temp.to_rgb()
            for j in range (height):
                img[j][i] = temp
        img = np.clip(img, 0.0, 1.0)
        return img


    def create_csv(self, path):
        """
        入射角が0-90度の分光反射率をCSV出力

        Parameters
        ----------
        path : string
            出力ファイル名
        """

        data = np.zeros([90, NSAMPLESPECTRUM])
        for i in range (90):
            spd = self.evaluate(np.cos(np.pi/180 * i))
            for j in range (NSAMPLESPECTRUM):
                data[i][j] = spd.c[j]
        np.savetxt(path ,data,delimiter=',', fmt='%.4f')