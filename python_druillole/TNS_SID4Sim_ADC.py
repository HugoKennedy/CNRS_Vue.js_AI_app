# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 09:39:17 2026

@author: druillol
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Union, List

class ADC_Emulator:
    """
    Émule un ADC (Convertisseur Analogique-Numérique) avec :
    - Échantillonnage à une fréquence donnée.
    - Interpolation Zero-Order Hold (ZOH).
    - Visualisation du signal échantillonné.

    Attributs:
        sampling_freq (float): Fréquence d'échantillonnage (Hz).
        coef (int): Coefficient de résolution pour la mise à l'échelle (par défaut 100).
    """

    def __init__(self, sampling_freq: float, coef: int = 100):
        """
        Initialise l'émulateur ADC.

        Args:
            sampling_freq: Fréquence d'échantillonnage (Hz).
            coef: Coefficient pour la résolution de la mise à l'échelle.
        """
        self.sampling_freq = sampling_freq
        self.coef = coef
        self.pas_reel = 1 / (coef * sampling_freq)

    def _compute_local_slope(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Calcule les pentes locales entre les points (x, y)."""
        if len(x) != len(y):
            raise ValueError("x et y doivent avoir la même longueur.")
        return np.gradient(y, x)

    def _rescale_x(self, x: np.ndarray, pas: float) -> np.ndarray:
        """Met à l'échelle l'axe x avec un pas donné."""
        min_x, max_x = np.min(x), np.max(x)
        return np.arange(min_x, max_x, pas)

    def _rescale_y(self, x: np.ndarray, y: np.ndarray, pas: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Met à l'échelle les axes x et y en utilisant une interpolation linéaire locale.

        Returns:
            Tuple[np.ndarray, np.ndarray]: (x_scaled, y_scaled)
        """
        x_scaled = self._rescale_x(x, pas)
        y_scaled = np.interp(x_scaled, x, y)
        return x_scaled, y_scaled

    def _zero_order_hold(self, x: np.ndarray, y: np.ndarray, xp: np.ndarray) -> np.ndarray:
        """
        Applique une interpolation Zero-Order Hold (ZOH) sur le signal.

        Args:
            x: Axe temporel original.
            y: Signal original.
            xp: Points d'échantillonnage.

        Returns:
            np.ndarray: Signal interpolé avec ZOH.
        """
        yp = np.interp(xp, x, y)
        return np.repeat(yp, self.coef)

    def sample_signal(self, time: np.ndarray, signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Échantillonne le signal avec la fréquence d'échantillonnage de l'ADC.

        Args:
            time: Axe temporel du signal.
            signal: Signal à échantillonner.

        Returns:
            Tuple[np.ndarray, np.ndarray]: (x_echantillonné, y_echantillonné)
        """
        # Met à l'échelle le signal
        x_scaled, y_scaled = self._rescale_y(time, signal, self.pas_reel)

        # Génère les points d'échantillonnage
        ratio = int(self.sampling_freq * (time[-1] - time[0]))
        xp = np.linspace(time[0], time[-1], ratio)

        # Applique le ZOH
        y_echantillonne = self._zero_order_hold(x_scaled, y_scaled, xp)

        return x_scaled, y_echantillonne

    def plot_comparison(self, time: np.ndarray, signal: np.ndarray, x_echantillonne: np.ndarray, y_echantillonne: np.ndarray):
        """Affiche le signal original et le signal échantillonné."""
        plt.figure(figsize=(10, 6))
        plt.plot(time, signal, label="Signal original", alpha=0.7)
        plt.scatter(x_echantillonne, y_echantillonne, c='b', marker='_', label="Échantillons ADC")
        plt.plot(x_echantillonne, y_echantillonne, '-r', label="ZOH")
        plt.xlabel("Temps (s)")
        plt.ylabel("Amplitude")
        plt.title("Signal original vs. Signal échantillonné (ADC)")
        plt.legend()
        plt.grid(True)
        plt.show()
        
def main():
    # 1. Génération du signal avec 3 sinus
    import TNS_SID4Sim_3Sinus as G3sin
    generateur = G3sin.Generateur_3sinus(
        w=[2 * np.pi * 5, 2 * np.pi * 20, 2 * np.pi * 50],  # 5 Hz, 20 Hz, 50 Hz
        phi=[0, np.pi/2, np.pi],
        amplitude=[1, 0.5, 2],
        t_start=0,
        t_end=1,
        num_points=1000,
    )
    resultat = generateur.generate()
    
    plt.plot(resultat["time"], resultat["signal"])
    plt.xlabel("Temps (s)")
    plt.ylabel("Amplitude")
    plt.title("Signal = sin(w1*t + phi1) + sin(w2*t + phi2) + sin(w3*t + phi3)")
    plt.grid()
    plt.show()
    print(resultat["time"].shape, resultat["signal"].shape)
    
    
    # 2. Filtrage passe-bande (10 Hz - 30 Hz)
    import TNS_SID4Sim_Bessel as FBessel
    filtre = FBessel.Filtre_Bessel(
        f_cut_low=10,
        f_cut_high=30,
        order=4,
        sampling_freq=1000,
    )
    filtered_signal_dict = filtre.apply(resultat)
    filtered_signal = filtered_signal_dict["filtered_signal"]
    print(filtered_signal.shape)
    
    # 3. Échantillonnage avec l'ADC (fréquence d'échantillonnage = 100 Hz)
    adc = ADC_Emulator(sampling_freq=100, coef=100)
    x_echantillonne, y_echantillonne = adc.sample_signal(resultat["time"], filtered_signal)
    print(x_echantillonne.shape, y_echantillonne.shape)
    # 4. Visualisation
    adc.plot_comparison(resultat["time"], filtered_signal, x_echantillonne, y_echantillonne)
    
    
if __name__ == "__main__":
    main()