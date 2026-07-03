# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 08:37:57 2026

@author: druillol
"""
############################################################
# Import packages
############################################################
import numpy as np  # handles most of the numerical work
import scipy.stats  # implements statistical tools (PDFs, etc)
import scipy.signal as signal
from matplotlib import pyplot as plt
import matplotlib
import matplotlib_inline.backend_inline

############################################################
#  Librairies personnelles
############################################################
import Generateur_de_Bruits as GdB


############################################################
# Generation d'un signal utile
# 3 sinusoides à 3 frequences différentes                   
############################################################
class Generateur_3sinus:
    """
    Génère un signal composé de la somme de 3 sinus de la forme sin(w*t + phi).

    Attributs:
        w (list): Liste des 3 fréquences angulaires (rad/s).
        phi (list): Liste des 3 phases initiales (rad).
        amplitude (list): Liste des 3 amplitudes (par défaut [1, 1, 1]).
        t_start (float): Temps de départ (par défaut 0).
        t_end (float): Temps de fin (par défaut 1).
        num_points (int): Nombre de points dans le signal (par défaut 1000).
    """

    def __init__(
        self,
        w: list,
        phi: list,
        amplitude: list = [1, 1, 1],
        t_start: float = 0,
        t_end: float = 1,
        num_points: int = 1000,
    ):
        """
        Initialise le générateur avec les paramètres des sinus.

        Args:
            w: Liste des 3 fréquences angulaires (rad/s).
            phi: Liste des 3 phases initiales (rad).
            amplitude: Liste des 3 amplitudes (par défaut [1, 1, 1]).
            t_start: Temps de départ (par défaut 0).
            t_end: Temps de fin (par défaut 1).
            num_points: Nombre de points dans le signal (par défaut 1000).
        """
        if len(w) != 3 or len(phi) != 3 or len(amplitude) != 3:
            raise ValueError("Les listes w, phi et amplitude doivent contenir exactement 3 éléments.")

        self.w = w
        self.phi = phi
        self.amplitude = amplitude
        self.t_start = t_start
        self.t_end = t_end
        self.num_points = num_points

    def generate(self) -> dict:
        """
        Génère le signal et retourne un dictionnaire avec les clés 'time' et 'signal'.

        Returns:
            dict: {"time": np.ndarray, "signal": np.ndarray}
        """
        # Génère un tableau de temps linéairement espacé
        time = np.linspace(self.t_start, self.t_end, self.num_points)

        # Initialise le signal à zéro
        signal_genered = np.zeros_like(time)

        # Ajoute chaque sinus au signal
        for i in range(3):
            signal_genered += self.amplitude[i] * np.sin(self.w[i] * time + self.phi[i])

        return {"time": time, "signal": signal_genered}
    
def main():
    # Exemple : 3 sinus avec w = [1, 20, 300] rad/s et phi = [0, π/2, π]
    generateur = Generateur_3sinus(
        w=[2*np.pi, 2*np.pi*20, 2*np.pi*300],
        phi=[0, np.pi/2, np.pi],
        amplitude=[1, 0.5, 2],
        t_start=0,
        t_end=10,
        num_points=1000
    )
    
    resultat = generateur.generate()
    
    # Affichage des 10 premiers points
    print("Temps :", resultat["time"][:10])
    print("Signal :", resultat["signal"][:10])
    
    plt.plot(resultat["time"], resultat["signal"])
    plt.xlabel("Temps (s)")
    plt.ylabel("Amplitude")
    plt.title("Signal = sin(w1*t + phi1) + sin(w2*t + phi2) + sin(w3*t + phi3)")
    plt.grid()
    plt.show()
    
if __name__ == "__main__":
    main()