# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 11:49:40 2024

@author: druillol
"""

import numpy as np  # handles most of the numerical work
import scipy.stats  # implements statistical tools (PDFs, etc)
import scipy.signal as sig
from matplotlib import pyplot as plt
import matplotlib
import matplotlib_inline.backend_inline

class thermalNoise:
    """"Generateur de Bruit uniform"""

    def __init__(self, Resistor=1, Temperature=300):
        self._R = Resistor
        self._Temp = Temperature
        self._initT = 0
        self._finalT = 1
        self._fs = 100
        self._x = []
        self.noise = []

    @property
    def R(self) -> float:
        return self._R

    @property
    def T(self) -> float:
        return self._Temp

    @property
    def init_time(self) -> float:
        return self._initT

    @init_time.setter
    def init_time(self, value):
        self._initT = value

    @property
    def final_time(self) -> float:
        return self._finalT

    @final_time.setter
    def final_time(self, value):
        self._finalT = value

    @property
    def fs_nb(self) -> int:
        return self._fs

    @property
    def tps(self) -> np.array:
        return self._x

    @fs_nb.setter
    def fs_nb(self, value):
        self._fs = value

    def get_samples(self, sigma=0.1):
        self._x = np.linspace(self._initT, self._finalT, num = self._fs)
        coef = 4*scipy.constants.Boltzmann*self._Temp*self._R
        print(coef)
        rv = scipy.stats.uniform(loc=0, scale=sigma)
        mean, var, skew, kurt = scipy.stats.uniform.stats(moments='mvsk')
        self.noise = coef*rv.rvs(size=self._fs)
        return rv, self.noise #np.sqrt(coef*rv.rvs(size=self._fs))

    def hist(self,div):
        counts, bins = np.histogram(self.noise, bins=int(len(self.noise)/div))
        return counts, bins


class whiteNoise:
    """"Generateur de Bruit gaussien"""

    def __init__(self, fs=1, psd: float = 1, seed = None):

        self._initT = 0
        self._finalT = 1
        self._rms = np.sqrt(fs * psd)
        self._fs = fs
        self._range = np.random.default_rng(seed)
        self.noise = []

    @property
    def init_time(self) -> float:
        return self._initT

    @init_time.setter
    def init_time(self, value):
        self._initT = value

    @property
    def final_time(self) -> float:
        return self._finalT

    @final_time.setter
    def final_time(self, value):
        self._finalT = value

    @property
    def fs_nb(self) -> int:
        return self._fs

    @property
    def tps(self) -> np.array:
        return self._x

    @fs_nb.setter
    def fs_nb(self, value):
        self._fs = value

    @property
    def fmin(self) -> float:
        return self._fmin

    def get_samples(self):
        self._x = np.linspace(self._initT, self._finalT, num = self._fs)
        rv = scipy.stats.norm(loc=0, scale=self._rms)
        self.noise = rv.rvs(size=self._fs)
        return rv, self.noise #np.sqrt(coef*rv.rvs(size=self._fs))

    def get_pdf(self, x):
        return scipy.stats.norm.pdf(x, loc=0, scale=self._rms)

    def hist(self,div):
        counts, bins = np.histogram(self.noise, bins=int(len(self.noise)/div))
        return counts, bins

class f_2Noise:
    """Generateur de Bruit en 1/f**2"""

    def __init__(self, fs=1,fmin = 100, psd: float = 1, seed = None, tinit=0, tend=1):
    
        self._range = np.random.default_rng(seed)
        self._fmin = fmin
        self._initT = tinit
        self._finalT = tend
        self._fs = fs

        self._bruitblanc = whiteNoise(self._fs,0.1,42)
        self._bruitblanc.init_time= tinit
        self._bruitblanc.final_time=tend

        self._scaling = 1. / (self._fs * self._fmin)
        self._a = np.array([2. * np.pi * self._fmin])
        self._b = np.array([1., -1. * np.exp(-2. * np.pi * self._fmin / self._fs)])
        r,n = self._bruitblanc.get_samples()
        self._zi = sig.lfilter_zi(self._a,self._b) * n[1]
        self.noise = []

    @property
    def init_time(self) -> float:
        return self._initT

    @init_time.setter
    def init_time(self, value):
        self._initT = value

    @property
    def final_time(self) -> float:
        return self._finalT

    @final_time.setter
    def final_time(self, value):
        self._finalT = value

    @property
    def fs_nb(self) -> int:
        return self._fs

    @property
    def tps(self) -> np.array:
        return self._x

    def get_samples(self):
        self._x = np.linspace(self._initT, self._finalT, num = self._fs)
        r,n = self._bruitblanc.get_samples()
        self.noise, self._zi = sig.lfilter(self._a,
                                       self._b,
                                       n,
                                       zi=self._zi)
        return self.noise * self._scaling

    def hist(self,div):
        counts, bins = np.histogram(self.noise, bins=int(len(self.noise)/div))
        return counts, bins

class fknee_alphaNoise:
    """Generateur de Bruit en 1/f**2"""

    def __init__(self, alpha = 1,fs=1,fmin = 100, fmax = 1000, psd: float = 1, seed = None, tinit=0, tend=1):
    
        self._range = np.random.default_rng(seed)
        self._fmin = fmin
        self._fmax = fmax
        self._initT = tinit
        self._finalT = tend
        self._fs = fs
        self._alpha = alpha

        self._bruitblanc = whiteNoise(self._fs,0.1,42)
        self._bruitblanc.init_time= tinit
        self._bruitblanc.final_time=tend

        nb_dec_min = np.log10(2*np.pi*self._fmin)
        nb_dec_max = np.log10(2*np.pi*self._fmax)
        self._nb_decade_alpha = np.ceil(4.5 * (nb_dec_max - nb_dec_min)).astype(int)
        self._deltap = (nb_dec_max - nb_dec_min) / self._nb_decade_alpha
        self._coef_num = [0] * self._nb_decade_alpha
        self._coef_den = [0] * self._nb_decade_alpha
        self._zi = [0] * self._nb_decade_alpha
        print(self._nb_decade_alpha, len(self._zi))
        for i in range(0, self._nb_decade_alpha):
            log_p_i = nb_dec_min + self._deltap * 0.5 * ((2. * i + 1.) - self._alpha / 2.)
            filter_f_min = np.power(10., log_p_i) / (2. * np.pi)
            filter_f_max = np.power(10., log_p_i +
                                    (self._deltap * self._alpha / 2.)) / (2. * np.pi)
            if i == 0:
                self._fmin = filter_f_min
            a0 = (self._fs + self._fmax * np.pi) / (self._fs + self._fmin * np.pi)
            a1 = -1. * (self._fs - self._fmax * np.pi) / (self._fs + self._fmin * np.pi)
            b1 = (self._fs - self._fmin * np.pi) / (self._fs + self._fmin * np.pi)
            self._coef_num[i] = np.array([a0, a1])
            self._coef_den[i] = np.array([1., -1. * b1])
            self._zi[i] = sig.lfilter_zi(self._coef_num[i], self._coef_den[i])
        self._fmax = filter_f_max
        self._scaling = 1. / np.power(self._fmax, self._alpha / 2.)
        self.noise = []

    @property
    def init_time(self) -> float:
        return self._initT

    @init_time.setter
    def init_time(self, value):
        self._initT = value

    @property
    def final_time(self) -> float:
        return self._finalT

    @final_time.setter
    def final_time(self, value):
        self._finalT = value

    @property
    def fs_nb(self) -> int:
        return self._fs

    @property
    def tps(self) -> np.array:
        return self._x

    def get_samples(self):
        self._x = np.linspace(self._initT, self._finalT, num = self._fs)
        r,n = self._bruitblanc.get_samples()
        for i in range(0, self._nb_decade_alpha):
            self.noise, self._zi[i] = sig.lfilter(self._coef_num[i],
                                       self._coef_den[i],
                                       n,
                                       zi=self._zi[i])
        return self.noise * self._scaling

    def hist(self,div):
        counts, bins = np.histogram(self.noise, bins=int(len(self.noise)/div))
        return counts, bins

class spectralAnalyse:

    def __init__(self, signal, fs):
        self._signal = signal
        self._fs = fs

    @property
    def fs_nb(self) -> int:
        return self._fs

    @fs_nb.setter
    def fs_nb(self, value):
        self._fs = value


    def autocorrelation(self):
        corr = sig.correlate(self._signal, self._signal)
        lags = sig.correlation_lags(len(self._signal), len(self._signal))
        corr /= np.max(corr)
        return lags, corr

    def DSP_periodogram(self):
        f, Pxx_den = sig.periodogram(self._signal, self._fs)
        return f, Pxx_den

    def SP_periodogram(self):
        f, Pxx_spec = sig.periodogram(self._signal, self._fs, 'flattop', scaling='spectrum')
        return f, Pxx_spec



if __name__ == "__main__" :
    matplotlib.rc('xtick', labelsize=6)
    matplotlib.rc('ytick', labelsize=6)
    ######################################
    # Bruit Thermique
    ######################################
    tn = thermalNoise(15000,300)
    tn.init_time= 0
    tn.final_time=0.001
    tn.fs_nb=int(1000/0.01)
    rv, noise = tn.get_samples(0.01)
    counts, bins = tn.hist(30)
    print(len(noise))
    print(len(tn.tps))
    font = {'family' : 'serif',
            'weight' : 'bold',
            'size'   : 3}
    # AFFICHAGE GRAPHIQUE
    matplotlib.rc('font', **font)
    fig, ax = plt.subplots(2, 1, figsize=(10, 6), tight_layout=True)
    fig.set_figwidth(3)
    fig.set_figheight(2)
    ax[0].plot(tn.tps, np.sqrt(noise), 'k-', lw=2, label='frozen pdf')
    print(noise[0:5])
    ax[1].hist(bins[:-1],bins, weights=counts)
    ax[1].legend(loc='best', frameon=False)
    plt.tight_layout()
    plt.show()
    
    ######################################
    # Bruit blanc
    ######################################

    wn = whiteNoise(10000,0.1,42)
    wn.init_time= 0
    wn.final_time=0.001
    wn.fs_nb=int(100/0.01)
    rv, noisew = wn.get_samples()
    counts, bins = wn.hist(30)

    # AFFICHAGE GRAPHIQUE
    fig, ax = plt.subplots(2, 1, figsize=(10, 6), tight_layout=True)
    fig.set_figwidth(3)
    fig.set_figheight(2)
    ax[0].plot(wn.tps, noisew, 'k-', lw=2, label='frozen pdf')
    counts = counts/np.max(counts)
    ax[1].hist(bins[:-1],bins, weights=counts)
    ax[1].plot(bins,25*wn.get_pdf(bins), c='black')
    ax[1].legend(loc='best', frameon=False)
    plt.tight_layout()
    plt.show()

    ######################################
    # Bruit 1/f^2
    ######################################
    f2n = f_2Noise(10000,10,0.1,42,0,0.1)
    noise = f2n.get_samples()
    counts, bins = f2n.hist(30)
    noise = noise + 0.01*noisew

    # AFFICHAGE GRAPHIQUE
    fig, ax = plt.subplots(2, 1, figsize=(10, 6), tight_layout=True)
    ax[0].plot(f2n.tps, noise, 'k-', lw=2, label='1/f pdf')
    counts = counts/np.max(counts)
    ax[1].hist(bins[:-1],bins, weights=counts)
    ax[1].legend(loc='best', frameon=False)
    plt.tight_layout()
    plt.show()

    spa = spectralAnalyse(noise,1000000)
    x,y = spa.autocorrelation()
    f, DSPsig = spa.DSP_periodogram()
    f, SPsig = spa.SP_periodogram()

    fig, ax = plt.subplots(3, 1, figsize=(10, 6), tight_layout=True)
    ax[0].plot(x,y)
    ax[1].loglog(f, DSPsig)
    ax[1].set_ylim([1e-10, 1e-1])
    ax[1].set_xlabel('frequency [Hz]')
    ax[1].set_ylabel('Linear spectrum [V RMS]')
    ax[1].grid(True, which="both", axis='x')
    ax[2].loglog(f, np.sqrt(SPsig))
    ax[2].set_ylim([1e-4, 1e2])
    ax[2].set_xlabel('frequency [Hz]')
    ax[2].set_ylabel('Linear spectrum [V RMS]')
    ax[2].grid(True, which="both", axis='x')
    plt.tight_layout()
    plt.show()

    ######################################
    # Bruit 1/f^alpha
    ######################################
    fkn = fknee_alphaNoise(1.99,100000,100,1000,0.1,42,0,0.1)
    noise = fkn.get_samples()
    counts, bins = fkn.hist(30)

    # AFFICHAGE GRAPHIQUE
    fig, ax = plt.subplots(2, 1, figsize=(10, 6), tight_layout=True)
    ax[0].plot(fkn.tps, noise, 'k-', lw=2, label='1/f pdf')
    counts = counts/np.max(counts)
    ax[1].hist(bins[:-1],bins, weights=counts)
    ax[1].legend(loc='best', frameon=False)
    plt.tight_layout()
    plt.show()

    spa = spectralAnalyse(noise,1000000)
    x,y = spa.autocorrelation()
    f, DSPsig = spa.DSP_periodogram()
    f, SPsig = spa.SP_periodogram()

    fig, ax = plt.subplots(3, 1, figsize=(10, 6), tight_layout=True)
    ax[0].plot(x,y)
    ax[1].loglog(f, DSPsig)
    ax[1].set_ylim([1e-10, 1e-1])
    ax[1].set_xlabel('frequency [Hz]')
    ax[1].set_ylabel('Linear spectrum [V RMS]')
    ax[1].grid(True, which="both", axis='x')
    ax[2].semilogx(f, np.sqrt(SPsig))
    #ax[2].set_ylim([1e-4, 1e2])
    ax[2].set_xlabel('frequency [Hz]')
    ax[2].set_ylabel('Linear spectrum [V RMS]')
    ax[2].grid(True, which="both", axis='x')
    plt.tight_layout()
    plt.show()

    t = np.linspace(0,0.1,100000)
    f_x = np.sin(2*np.pi*10000*t)
    fig, ax = plt.subplots(3, 1, figsize=(10, 6), tight_layout=True)
    ax[0].plot(t,f_x)




