# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 08:37:57 2026

@author: druillol
"""
############################################################
# Import packages
############################################################
import numpy as np  # handles most of the numerical work
from matplotlib import pyplot as plt

############################################################
#  Librairies personnelles
############################################################
import Generateur_de_Bruits as GdB


############################################################
# Generation d'un Bruit
# somme de deux Bruits 1/f et blanc                   
############################################################
   
def main():
    # Exemple : Bruit en 1/f et blanc
    fkn = GdB.fknee_alphaNoise(1.5,10000,100,1000,200,42,0,0.1)
    noise = fkn.get_samples()

    wn = GdB.whiteNoise(10000,0.05,42)
    wn.init_time= 0
    wn.final_time=0.001
    wn.fs_nb=int(100/0.01)
    rv, noisew = wn.get_samples()
    sig = np.cumsum(noise) + noisew
    time = fkn.tps
    
    resultat = {"time": time, "noise_genered": sig}
    
    # Affichage des 10 premiers points
    print("Temps :", resultat["time"])
    print("Signal :", resultat["noise_genered"])
    
    plt.plot(resultat["time"], resultat["noise_genered"])
    plt.xlabel("Temps (s)")
    plt.ylabel("Amplitude")
    plt.title("Bruit Brownien + Bruit blanc")
    plt.grid()
    plt.show()
    
    
if __name__ == "__main__":
    main()