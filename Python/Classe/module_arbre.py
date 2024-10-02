#%% Imports

from module_marche import DonneeMarche
from module_option import Option
from module_enums import ConventionBaseCalendaire

import numpy as np
import datetime as dt
import concurrent.futures
import asyncio

#%% Fonctions 



#%% Classes

class Arbre : 
    def __init__(self, nb_pas : int, donnee_marche : DonneeMarche, option : Option) -> None:
        """Initialisation de la classe

        Args:
            nb_pas (float): le nombre de pas dans notre modèle
            donnee_marche (DonneeMarche): Classe utilisée pour représenter les données de marché.
            option (Option): Classe utilisée pour représenter une option et ses paramètres.
        """
        self.nb_pas = nb_pas
        self.donnee_marche = donnee_marche
        self.option = option
        self.delta_t = self.__calcul_delta_t()
        self.alpha = self.__calcul_alpha()
        self.racine = None
        
        # Noeud(self.donnee_marche.prix_spot, self.donnee_marche, self.option, self.nb_pas, position_arbre = 1)

    def get_temps (self, convention_base_calendaire : ConventionBaseCalendaire = ConventionBaseCalendaire._365.value) -> float : 
        """Renvoie le temps à maturité exprimé en nombre d'année .
        
        Attributs: 
            convention_base (ConventionBaseCalendaire): la base annuelle en nombre de jours. Valeur par défaut : 360. Les valeurs possibles sont 365 ou 360 (voir les attributs de la classe enum correspondante).

        Retourne:
            float: temps à maturité en nombre d'année
        """
        return (self.option.maturite - self.option.date_pricing).days/convention_base_calendaire
    
    def __calcul_delta_t (self) -> float : 
        """Permet de calculet l'intervalle de temps de référence qui sera utilisée dans notre modèle.

        Args:
            nb_pas (int): le nombre de pas dans notre modèle


        Returns:
            float: l'intervalle de temps delta_t
        """
        return self.get_temps() / self.nb_pas
 
    def __calcul_alpha (self) -> float : 
        """Fonction nous permettant de calculer alpha, que nous utiliserons dans l'arbre

        Arguments:
            pas (int) : le nombre de pas dans notre modèlé
            donnee_marche (DonneeMarche): Les données de marché à utiliser
            option (Option): Les caractéristiques de l'option

        Retour:
            float: Nous renvoie le coefficient alpha
        """
        alpha = np.exp(self.donnee_marche.volatilite * np.sqrt(3) * np.sqrt(self.delta_t))
        return alpha 
        
    def planter_tronc(self) :
        """Méthode nous permettant d'instancier l'arbre, de créer le noeud racine puis de construire l'ensemble du tronc à partir de la méthode liaison_centre() du module noeud.
        C'est de ce dernier que nous partirons ensuite pour coonstruire le reste de l'arbre.
        """
        from module_noeud import Noeud
        
        self.racine = Noeud(prix_sj = self.donnee_marche.prix_spot, arbre = self, position_arbre=0)
        
        noeud_ref = self.racine
        
        for pas in range(self.nb_pas) : 
            noeud_ref.liaison_centre()
            noeud_ref = noeud_ref.futur_centre                     
            
    def branchage_haut(self) :
        """Méthode nous permettant de créer la partie supérieure de l'arbre à partir de la méthode liaison_haut() du module noeud.
        """

        noeud_ref = self.racine.futur_haut
        
        for pas in range(self.nb_pas - 1)  : 
            noeud_ref.liaison_haut()
            noeud_ref = noeud_ref.futur_haut
            
    def branchage_bas(self) :
        """Méthode nous permettant de créer la partie inférieure de l'arbre à partir de la méthode liaison_haut() du module noeud.
        """
         
        noeud_ref = self.racine.futur_bas
        
        for pas in range(self.nb_pas - 1)  : 
            noeud_ref.liaison_bas()
            noeud_ref = noeud_ref.futur_bas
            
    def planter_arbre_vanille(self):
        """Cette méthode regroupe les trois méthodes planter_tronc(), branchage_bas et branchage_haut afin de construire l'arbre dans son ensemble.
        L'arbre se construit de manière linéraire : tronc, bas, haut."""  
              
        self.planter_tronc()
        self.branchage_bas()
        self.branchage_haut()
            
    async def planter_arbre_speed(self):
        """Cette méthode regroupe les trois méthodes planter_tronc(), branchage_bas et branchage_haut afin de construire l'arbre dans son ensemble.
        L'arbre se construit de manière asynchrone pour les branches inférieures et supérieurs : tronc, bas et haut."""  
        
        self.planter_tronc()
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_haut = loop.run_in_executor(executor, self.branchage_haut)
            future_bas = loop.run_in_executor(executor, self.branchage_bas)

            await asyncio.gather(future_haut, future_bas)
