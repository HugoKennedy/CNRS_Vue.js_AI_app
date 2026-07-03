# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 09:26:13 2026

@author: druillol
"""

import numpy as np
from scipy.signal import bessel, lfilter, filtfilt

class Filtre_Bessel:
    """
    Applique un filtre passe-bande de Bessel à un signal.

    Attributs:
        f_cut_low (float): Fréquence de coupure basse (Hz).
        f_cut_high (float): Fréquence de coupure haute (Hz).
        order (int): Ordre du filtre (par défaut 4).
        sampling_freq (float): Fréquence d'échantillonnage (Hz). Doit être > 2 * f_cut_high.
    """

    def __init__(
        self,
        f_cut_low: float,
        f_cut_high: float,
        order: int = 4,
        sampling_freq: float = 1000,
    ):
        """
        Initialise le filtre passe-bande de Bessel.

        Args:
            f_cut_low: Fréquence de coupure basse (Hz).
            f_cut_high: Fréquence de coupure haute (Hz).
            order: Ordre du filtre (par défaut 4).
            sampling_freq: Fréquence d'échantillonnage (Hz). Doit être > 2 * f_cut_high.
        """
        if f_cut_low >= f_cut_high:
            raise ValueError("f_cut_low doit être strictement inférieur à f_cut_high.")
        if sampling_freq <= 2 * f_cut_high:
            raise ValueError("La fréquence d'échantillonnage doit être > 2 * f_cut_high (théorème de Nyquist).")

        self.f_cut_low = f_cut_low
        self.f_cut_high = f_cut_high
        self.order = order
        self.sampling_freq = sampling_freq

        # Normalisation des fréquences de coupure (0 < f_normalized < 1)
        self.f_low_norm = f_cut_low / (0.5 * sampling_freq)
        self.f_high_norm = f_cut_high / (0.5 * sampling_freq)

        # Conception du filtre passe-bande de Bessel
        self.b, self.a = self._design_bandpass_bessel()

    def _design_bandpass_bessel(self):
        """
        Conçoit un filtre passe-bande de Bessel en combinant un filtre passe-haut et un filtre passe-bas.

        Returns:
            tuple: (b, a) coefficients du filtre.
        """
        # Filtre passe-bas de Bessel
        b_low, a_low = bessel(self.order, self.f_high_norm, btype='low', analog=False)

        # Filtre passe-haut de Bessel
        b_high, a_high = bessel(self.order, self.f_low_norm, btype='high', analog=False)

        # Combinaison des deux filtres pour obtenir un passe-bande
        # On utilise la convolution des coefficients pour un filtre en cascade
        from scipy.signal import convolve
        b_band = convolve(b_low, b_high)
        a_band = convolve(a_low, a_high)

        return b_band, a_band

    def apply(self, signal_dict: dict) -> dict:
        """
        Applique le filtre passe-bande au signal d'entrée.

        Args:
            signal_dict: Dictionnaire avec les clés "time" et "signal".

        Returns:
            dict: Dictionnaire avec les clés "time" et "filtered_signal".
        """
        time = signal_dict["time"]
        out_signal = signal_dict["signal"]

        # Applique le filtre avec filtfilt pour éviter les déphasages
        filtered_signal = filtfilt(self.b, self.a, out_signal)

        return {"time": time, "filtered_signal": filtered_signal}
    
############################################################
# Filtrage du signal
# somme de deux Bruits 1/f et blanc                   
############################################################
   
def main():
    # 1. Génération du signal avec 3 sinus
    import TNS_SID4Sim_3Sinus as G3sin
    generateur = G3sin.Generateur_3sinus(
    w=[2 * np.pi * 5, 2 * np.pi * 50, 2 * np.pi * 200],  # Fréquences en rad/s (5 Hz, 20 Hz, 50 Hz)
    phi=[0, np.pi/2, np.pi],
    amplitude=[1, 2, 3],
    t_start=0,
    t_end=1,
    num_points=1000,
    )
    signal_dict = generateur.generate()
    
    # 2. Application du filtre passe-bande (ex: 10 Hz - 30 Hz)
    filtre = Filtre_Bessel(
        f_cut_low=150,  # Fréquence de coupure basse (Hz)
        f_cut_high=300,  # Fréquence de coupure haute (Hz)
        order=4,
        sampling_freq=700,  # Fréquence d'échantillonnage (Hz)
    )
    filtered_signal_dict = filtre.apply(signal_dict)
    
    # 3. Visualisation
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(10, 6))
    plt.plot(signal_dict["time"], signal_dict["signal"], label="Signal original", alpha=0.7)
    plt.plot(filtered_signal_dict["time"], filtered_signal_dict["filtered_signal"], label="Signal filtré", color="red")
    plt.xlabel("Temps (s)")
    plt.ylabel("Amplitude")
    plt.title("Signal original vs. Signal filtré (Passe-bande Bessel 10-30 Hz)")
    plt.legend()
    plt.grid()
    plt.show()
    
    
if __name__ == "__main__":
    main()