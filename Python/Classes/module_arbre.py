#%% Imports

import numpy as np
import concurrent.futures
import asyncio

from Classes.module_marche import DonneeMarche
from Classes.module_option import Option
from Classes.module_enums import ConventionBaseCalendaire

#%% Classes

class Arbre : 
    def __init__(self, nb_pas : int, donnee_marche : DonneeMarche, option : Option, convention_base_calendaire : ConventionBaseCalendaire = ConventionBaseCalendaire._365.value) -> None:
        """Initialisation de la classe

        Args:
            nb_pas (float): le nombre de pas dans notre modèle
            donnee_marche (DonneeMarche): Classe utilisée pour représenter les données de marché.
            option (Option): Classe utilisée pour représenter une option et ses paramètres.
        """
        self.nb_pas = nb_pas
        self.donnee_marche = donnee_marche
        self.option = option
        self.convention_base_calendaire = convention_base_calendaire
        self.delta_t = self.__calcul_delta_t()
        self.position_div = self.__calcul_position_div()
        self.alpha = self.__calcul_alpha()
        self.racine = None
           
    def get_temps (self) -> float : 
        """Renvoie le temps à maturité exprimé en nombre d'année .

        Returns:
            float: temps à maturité en nombre d'année
        """
        return (self.option.maturite - self.option.date_pricing).days/self.convention_base_calendaire
    
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

        Args:
            pas (int) : le nombre de pas dans notre modèlé
            donnee_marche (DonneeMarche): Les données de marché à utiliser
            option (Option): Les caractéristiques de l'option

        Returns:
            float: Nous renvoie le coefficient alpha
        """
        alpha = np.exp(self.donnee_marche.volatilite * np.sqrt(3) * np.sqrt(self.delta_t))
        return alpha 
    
    def __calcul_position_div (self) -> float : 
        nb_jour_detachement = (self.donnee_marche.dividende_ex_date - self.option.date_pricing).days
        position_div = nb_jour_detachement / self.convention_base_calendaire / self.delta_t
        return position_div
    
    def planter_tronc(self) -> None :
        """Méthode nous permettant d'instancier l'arbre, de créer le noeud racine puis de construire l'ensemble du tronc à partir de la méthode liaison_centre() du module noeud.
        C'est de ce dernier que nous partirons ensuite pour coonstruire le reste de l'arbre.
        """
        from Classes.module_noeud import Noeud
        
        self.racine = Noeud(prix_sj = self.donnee_marche.prix_spot, arbre = self, position_arbre=0)
        
        noeud_ref = self.racine
        
        for pas in range(self.nb_pas) : 
            noeud_ref.liaison_centre()
            noeud_ref = noeud_ref.futur_centre                     
            
    def branchage_haut(self) -> None :
        """Méthode nous permettant de créer la partie supérieure de l'arbre à partir de la méthode liaison_haut() du module noeud.
        """

        noeud_ref = self.racine.futur_haut
        
        for pas in range(self.nb_pas - 1)  : 
            noeud_ref.liaison_haut()
            noeud_ref = noeud_ref.futur_haut
            
    def branchage_bas(self) -> None :
        """Méthode nous permettant de créer la partie inférieure de l'arbre à partir de la méthode liaison_haut() du module noeud.
        """
         
        noeud_ref = self.racine.futur_bas
        
        for pas in range(self.nb_pas - 1)  : 
            noeud_ref.liaison_bas()
            noeud_ref = noeud_ref.futur_bas
            
    def planter_arbre_vanille(self) -> None :
        """Cette méthode regroupe les trois méthodes planter_tronc(), branchage_bas et branchage_haut afin de construire l'arbre dans son ensemble.
        L'arbre se construit de manière linéraire : tronc, bas, haut."""  
              
        self.planter_tronc()
        self.branchage_bas()
        self.branchage_haut()
            
    async def planter_arbre_speed(self) -> None :
        """Cette méthode regroupe les trois méthodes planter_tronc(), branchage_bas et branchage_haut afin de construire l'arbre dans son ensemble.
        L'arbre se construit de manière asynchrone pour les branches inférieures et supérieurs : tronc, bas et haut."""  
        
        self.planter_tronc()
        
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_haut = loop.run_in_executor(executor, self.branchage_haut)
            future_bas = loop.run_in_executor(executor, self.branchage_bas)

            await asyncio.gather(future_haut, future_bas)
            
    def pricer_arbre(self) -> None : 
        
        noeud_racine = noeud_ref = self.racine
        
        while hasattr(noeud_ref, "futur_haut") : #on se place ici au noeud le plus en haut de la fin de l'arbre
            noeud_ref = noeud_ref.futur_haut
        
        noeud_ref_2 = noeud_ref 
               
        while noeud_ref != noeud_racine : 
            while hasattr(noeud_ref, "bas") : #on calcule la valeur intrinseque des noeuds de la derniere colonne en iterant vers le bas 
                noeud_ref.calcul_valeur_intrinseque()
                noeud_ref = noeud_ref.bas
            noeud_ref.calcul_valeur_intrinseque()
            noeud_ref_2 = noeud_ref = noeud_ref_2.bas.precedent_centre 
            
        noeud_racine.calcul_valeur_intrinseque()
        self.prix_option  = noeud_racine.valeur_intrinseque