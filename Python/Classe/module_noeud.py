#%% Imports

from module_arbre import Arbre

import numpy as np

#%% Constantes

somme_proba = 1
prix_min_sj = 0 #on part du principe que le prix du sous-jacent ne peut être négatif (ce qui dans le cas d'un actif purement financier sera à priori toujours vrai)



# def calcul_forward(pas : int, donnee_marche : DonneeMarche, option : Option, arbre : Arbre, position_arbre : int = 1) -> float :
#     """Permet de calculer le prix forward pour n'importe quelle position dans l'arbre

#     Args:
#         pas (int): le nombre de pas dans notre modèle
#         donnee_marche (DonneeMarche): Les données de marché à utiliser
#         option (Option): L'option de référence

#     Returns:
#         float: Nous renvoie le prix forward du sous-jacent
#     """
#     return donnee_marche.prix_spot * np.exp(donnee_marche.taux_interet * calcul_delta_t(pas, option) * position_arbre)

#%% Classes

class Noeud :
    def __init__(self, prix_sj : float, arbre : Arbre, position_arbre : int) -> None:
        """Initialisation de la classe

        Args:
            prix_sj (float): le prix du sous-jacent de ce noeud
            donnee_marche (DonneeMarche): Classe utilisée pour représenter les données de marché.
            option (Option): Classe utilisée pour représenter une option et ses paramètres.
            nb_pas (int): le nombre de pas dans notre modèle
            position_arbre (int): _descripla position de notre noeud au sein de l'arbre (uniquement sur un axe horizontal)tion_
        """
        self.prix_sj = prix_sj
        self.arbre = arbre
        self.position_arbre = position_arbre
        
    def __calcul_forward(self) -> float : 
        #permet de calculer le prix forward du prochain noeud
        facteur_temps = self.arbre.donnee_marche.taux_interet * self.arbre.get_temps() * self.arbre.delta_t
        return self.prix_sj * np.exp(facteur_temps)
    
    def __proba_neg(proba : float) -> None : 
        if proba < 0 : 
            raise ValueError ("La probabilité est négative")
    
    def __calcul_proba(self) -> None : 
       
        p_bas = ((self.futur_centre.prix_sj ** (-2)) * (self.arbre.donnee_marche.volatilite + self.__calcul_forward() ** 2)
                      - 1 - (self.arbre.alpha + 1) * (self.futur_centre.prix_sj ** (-1)) * self.__calcul_forward() /
                      ((1 - self.arbre.alpha) * (self.arbre.alpha ** (-2) - 1)))
                     
        p_haut = ((1 / self.futur_centre.prix_sj * self.__calcul_forward() - 1) - (1 / self.arbre.alpha - 1) * self.p_bas /
                       (self.arbre.alpha - 1))
        
        p_mid = 1 - (p_haut - p_haut)
        
        if not p_bas > 0 and p_haut > 0 and p_mid > 0 :
            raise ValueError("Probabilité négative")
        
        if p_bas + p_haut + p_mid != somme_proba : 
            raise ValueError(f"La somme des probabilités doit être égale à {somme_proba}")
        else :             
            self.p_bas = p_bas
            self.p_haut = p_haut
            self.p_mid = p_mid        
                
    def liaison_centre(self) -> None : 
        
        self.futur_centre = Noeud(self.__calcul_forward(), self.arbre, self.position_arbre + 1)
        self.futur_centre.parent = self
        
        self.futur_haut = Noeud(self.futur_centre.prix_sj * self.arbre.alpha, self.arbre, self.position_arbre + 1)
        self.futur_haut.parent = self
        self.futur_haut.bas = self.futur_centre
        self.futur_centre.haut = self.futur_haut
        
        self.futur_bas = Noeud(self.futur_centre.prix_sj * self.arbre.alpha**(-1), self.arbre, self.position_arbre + 1)
        self.futur_bas.parent = self
        self.futur_bas.haut = self.futur_centre
        self.futur_centre.bas = self.futur_bas
        
    def liaison_haut(self) -> None :         
        noeud_ref = self
          
        #on descend sur le tronc              
        while not hasattr(noeud_ref.bas, "futur_haut"): 
            noeud_ref = noeud_ref.bas
                 
        if noeud_ref == self :
            #dans le cas où nous nous situons directement sur le futur haut de la racine
            self.futur_centre = self.bas.futur_haut
            self.futur_bas = self.bas.futur_centre
            
        else : 
            while not noeud_ref == self : 
                noeud_ref.futur_centre = noeud_ref.bas.futur_haut
                noeud_ref.futur_bas = noeud_ref.bas.futur_centre
                noeud_ref.futur_haut = Noeud(noeud_ref.futur_centre.prix_sj * noeud_ref.arbre.alpha, noeud_ref.arbre, noeud_ref.position_arbre + 1)
                noeud_ref.futur_haut.bas = noeud_ref.futur_centre
                noeud_ref.futur_centre.haut = noeud_ref.futur_haut
                noeud_ref.haut.futur_centre = noeud_ref.futur_haut
                noeud_ref.haut.futur_bas = noeud_ref.futur_centre
                noeud_ref = noeud_ref.haut
            
        #on retombe sur notre noeud le plus en haut
        self.futur_haut = Noeud(self.futur_centre.prix_sj * self.arbre.alpha, self.arbre, self.position_arbre + 1)
        self.futur_haut.bas = self.futur_centre
        self.futur_centre.haut = self.futur_haut

    def liaison_bas(self) -> None :         
        noeud_ref = self
          
        #on descend sur le tronc              
        while not hasattr(noeud_ref.haut, "futur_bas"): 
            noeud_ref = noeud_ref.haut
                 
        if noeud_ref == self :
            #dans le cas où nous nous situons directement sur le futur haut de la racine
            self.futur_centre = self.haut.futur_bas
            self.futur_haut = self.haut.futur_centre
            
        else : 
            while not noeud_ref == self : 
                noeud_ref.futur_centre = noeud_ref.haut.futur_bas
                noeud_ref.futur_haut = noeud_ref.haut.futur_centre
                noeud_ref.futur_bas = Noeud(noeud_ref.futur_centre.prix_sj * noeud_ref.arbre.alpha**(-1), noeud_ref.arbre, noeud_ref.position_arbre + 1)
                noeud_ref.futur_bas.haut = noeud_ref.futur_centre
                noeud_ref.futur_centre.bas = noeud_ref.futur_bas
                noeud_ref.bas.futur_centre = noeud_ref.futur_bas
                noeud_ref.bas.futur_haut = noeud_ref.futur_centre
                noeud_ref = noeud_ref.bas
            
        #on retombe sur notre noeud le plus en haut
        self.futur_bas = Noeud(self.futur_centre.prix_sj * self.arbre.alpha**(-1), self.arbre, self.position_arbre + 1)
        self.futur_haut.parent = self
        self.futur_bas.haut = self.futur_centre
        self.futur_centre.bas = self.futur_bas
        
            
        
        
            
        
    
    
    # def __liaison_tronc(self) -> None : 
    #     self.futur_centre = Noeud(self.__calcul_forward(), self.arbre, self.position_arbre + 1)
    #     self.futur_centre.tronc = True
    #     self.futur_centre.parent = self
        
    #     if not hasattr(self, "futur_haut") :
    #         self.futur_haut = Noeud(self.futur_centre.prix_sj * self.arbre.alpha, self.arbre, self.position_arbre + 1)
    #         self.futur_haut.haut_tronc = True
    #         self.futur_haut.bas = self.futur_centre
    #         self.futur_centre.haut = self.futur_haut
    #         self.futur_haut.parent = self
    #     else : 
    #         self.futur_haut = self.futur_centre.haut
    #         self.futur_haut.haut_tronc = True
        
    #     if not hasattr(self, "futur_bas") : 
    #         self.futur_bas = Noeud(self.futur_centre.prix_sj * self.arbre.alpha**(-1), self.arbre, self.position_arbre + 1)
    #         self.futur_bas.bas_tronc = True
    #         self.futur_bas.haut = self.futur_centre
    #         self.futur_centre.bas = self.futur_bas
    #         self.futur_bas.parent = self
    #     else : 
    #         self.futur_bas = self.futur_centre.bas
    #         self.futur_bas.bas_tronc = True
    
    # def __liaison_haut(self) -> None : 
    #     self.futur_centre = Noeud(self.__calcul_forward(), self.arbre, self.position_arbre + 1)
    #     self.futur_centre.parent = self
        
    #     if not hasattr(self.futur_centre, "haut") : 
    #         self.futur_haut = Noeud(self.futur_centre.prix_sj * self.arbre.alpha, self.arbre, self.position_arbre + 1)
    #         self.futur_haut.bas = self.futur_centre
    #         self.futur_centre.haut = self.futur_haut
    #         self.futur_haut.parent = self
    #     else : 
    #         self.futur_haut = self.futur_centre.haut
        
    #     self.futur_bas = self.futur_centre.bas
        
    # def __liaison_bas(self) -> None : 
    #     self.futur_centre = Noeud(self.__calcul_forward(), self.arbre, self.position_arbre + 1)
    #     self.futur_centre.parent = self
    #     #TODO à remplacer par une procédure "bestmid" pour prendre en compte un versement de dividende
        
    #     if not hasattr(self.futur_centre, "bas") : 
    #         self.futur_bas = Noeud(self.futur_centre.prix_sj * self.arbre.alpha**(-1), self.arbre, self.position_arbre + 1)
    #         self.futur_bas.haut = self.futur_centre
    #         self.futur_centre.bas = self.futur_bas
    #         self.futur_bas.parent = self
    #     else : 
    #         self.futur_bas = self.futur_centre.bas
        
    #     self.futur_bas = self.futur_centre.bas
    
    # def liaisons(self) -> None : 
        
    #     if self.tronc == True : 
    #         return self.__liaison_tronc()
        
    #     elif self.bas_tronc == True : 
    #         return self.__liaison_bas()
        
    #     elif self.haut_tronc == True :
    #         return self.__liaison_haut()
        
        
# %%
