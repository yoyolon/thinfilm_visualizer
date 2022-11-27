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


def composit_r(r0, r1, phi):
    """
    界面での干渉を考慮したフレネル反射係数

    Parameters
    ----------
    r0 : complex
        薄膜層上面のフレネル反射係数
    r1 : complex
        薄膜層下面のフレネル反射係数
    phi : float
        一回の内部反射で生じる位相差
    """
    return (r0 + r1 * np.exp(2*1.j*phi)) / (1 + r0 * r1 * np.exp(2*1.j*phi))


def composit_t(r0, r1, t0, t1, phi):
    """
    界面での干渉を考慮したフレネル透過係数

    Parameters
    ----------
    r0 : complex
        薄膜層上面のフレネル反射係数
    r1 : complex
        薄膜層下面のフレネル反射係数
    t0 : complex
        薄膜層上面のフレネル透過係数
    t1 : complex
        薄膜層下面のフレネル透過係数
    phi : float
        一回の内部反射で生じる位相差
    """
    return (t0 * t1 * np.epx(1.j*phi)) / (1 + r0 * r1 * np.exp(2*1.j*phi))


def iridr(r01, r10, r12, t01, t10, phi):
    """
    界面での干渉を考慮したフレネル透過係数

    Parameters
    ----------
    r01 : complex
        入射側の媒質->薄膜層のフレネル反射係数
    r10 : complex
        薄膜層->入射媒質のフレネル反射係数
    r12 : complex
        出射側の媒質->薄膜層のフレネル反射係数
    t01 : complex
        入射側の媒質->薄膜層のフレネル透過係数
    t10 : complex
        薄膜層->入射側の媒質のフレネル透過係数
    phi : float
        一回の内部反射で生じる位相差
    """
    return r01 + (t01 * r12 * t10 * np.exp(1.j*phi)) / (1 - r10 * r12 * np.exp(1.j*phi))



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
        
    
    def Evaluate(self, cosTheta):
        """
        薄膜干渉の分光反射率を評価

        Parameters
        ----------
        cosTheta : float
            入射角(ラジアン)

        Returns
        -------
        spd : Spectrum
            薄膜干渉の分光反射率

        Notes
        -----
        現時点では単層薄膜(入射角媒質・薄膜・ベース媒質の三層モデル)を仮定
        計算はndarrayを行い最後にSpectrumに変換
        """
        nLayers = len(self.films)
        sinTheta = np.sqrt(max(0, 1 - cosTheta**2))
        index = 0
        cosFilm = np.zeros([nLayers, NSAMPLESPECTRUM]) # 各層への入射角の余弦
        etaI = self.films[0].eta
        # 薄膜への入射角計算
        for film in self.films:
            sample = np.zeros([NSAMPLESPECTRUM])
            for i in range(NSAMPLESPECTRUM):
                sinTemp = etaI[i] * sinTheta / complex(film.eta[i], film.kappa[i])
                if (sinTemp.real**2 + sinTemp.imag**2 > 1): # 全反射
                    return Spectrum()
                cosTemp = np.sqrt(max(0, 1. - sinTemp**2))
                sample[i] = cosTemp
            cosFilm[index] = sample
            index = index + 1
        # 波長生成
        step = (END_WAVELENGTH - START_WAVELENGTH) / NSAMPLESPECTRUM
        wl = np.zeros(NSAMPLESPECTRUM)
        for i in range(NSAMPLESPECTRUM):
            wl[i] = START_WAVELENGTH + step/2 + i*step
        # 反射率計算
        rp = np.zeros(NSAMPLESPECTRUM, dtype=complex)
        rs = np.zeros(NSAMPLESPECTRUM, dtype=complex)
        for j in range(NSAMPLESPECTRUM):
            cos0 = cosFilm[0][j]
            cos1 = cosFilm[1][j]
            cos2 = cosFilm[2][j]
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
            rp[j] = iridr(rp01, rp10, rp12, tp01, tp10, phi)
            rs[j] = iridr(rs01, rs10, rs12, ts01, ts10, phi)
            #rp[j] = composit_r(rp01, rp12, phi/2)
            #rs[j] = composit_r(rs01, rs12, phi/2)
        v = (np.abs(rp)**2 + np.abs(rs)**2) / 2
        spd = Spectrum(wl, v)
        return spd
        
        
    def CreateTexture(self, width=270, height=90):
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
            temp = self.Evaluate(np.cos(np.pi/180 * i/invstep))
            temp = temp.ToRGB()
            for j in range (height):
                img[j][i] = temp
        img = np.clip(img, 0.0, 1.0)
        return img


    def CreateCSV(self, path):
        """
        入射角が0-90度の分光反射率をCSV出力

        Parameters
        ----------
        path : string
            出力ファイル名
        """

        outpath = os.path.join('out', path)
        data = np.zeros([90, NSAMPLESPECTRUM])
        for i in range (90):
            spd = self.Evaluate(np.cos(np.pi/180 * i))
            for j in range (NSAMPLESPECTRUM):
                data[i][j] = spd.c[j]
        np.savetxt(path ,data,delimiter=',', fmt='%.4f')