#%% Imports

from Classes.module_arbre import Arbre

import numpy as np

#%% Constantes

somme_proba = 1
prix_min_sj = 0 #on part du principe que le prix du sous-jacent ne peut être négatif (ce qui dans le cas d'un actif purement financier sera à priori toujours vrai)

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
        
        if self.position_arbre < self.arbre.position_div and self.position_arbre + 1 > self.arbre.position_div : 
            div = self.arbre.donnee_marche.dividende_montant
        else : 
            div = 0
            
        return self.prix_sj * self.arbre.facteur_capitalisation - div
    
    def __calcul_variance(self) -> float : 
        return (self.prix_sj ** 2) * np.exp(2 * self.arbre.donnee_marche.taux_interet * self.arbre.delta_t) * (np.exp((self.arbre.donnee_marche.volatilite ** 2) * self.arbre.delta_t) - 1)
    
    def __calcul_proba(self) -> None : 
       
        p_bas = ((self.futur_centre.prix_sj ** (-2)) * (self.__calcul_variance() + (self.__calcul_forward() ** 2))
                      - 1 - (self.arbre.alpha + 1) * ((self.futur_centre.prix_sj ** (-1)) * self.__calcul_forward() - 1)) / ((1 - self.arbre.alpha) * (self.arbre.alpha ** (-2) - 1))
                     
        p_haut = ((1 / self.futur_centre.prix_sj * self.__calcul_forward() - 1) - (1 / self.arbre.alpha - 1) * p_bas /
                       (self.arbre.alpha - 1))
        
        p_mid = 1 - p_haut - p_bas
        
        if not p_bas > 0 and p_haut > 0 and p_mid > 0 :
            raise ValueError("Probabilité négative")
        
        if round(p_bas + p_haut + p_mid, 1) != somme_proba : 
            print(f"p_bas : {p_bas}, p_haut : {p_haut}, p_mid : {p_mid}")
            raise ValueError(f"La somme des probabilités doit être égale à {somme_proba}")
        else :             
            self.p_bas = p_bas
            self.p_haut = p_haut
            self.p_mid = p_mid        
                
    def liaison_centre(self) -> None : 
        
        self.futur_centre = Noeud(self.__calcul_forward(), self.arbre, self.position_arbre + 1)
        self.futur_centre.precedent_centre = self
        self.__calcul_proba()
        
        self.futur_haut = Noeud(self.futur_centre.prix_sj * self.arbre.alpha, self.arbre, self.position_arbre + 1)
        self.futur_haut.bas = self.futur_centre
        self.futur_centre.haut = self.futur_haut
        
        self.futur_bas = Noeud(self.futur_centre.prix_sj * self.arbre.alpha**(-1), self.arbre, self.position_arbre + 1)
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
            self.futur_centre.precedent_centre = self
            self.__calcul_proba()
            self.futur_bas = self.bas.futur_centre
            
            
        else : 
            while not noeud_ref == self : 
                noeud_ref.futur_centre = noeud_ref.bas.futur_haut
                noeud_ref.futur_centre.precedent_centre = noeud_ref
                noeud_ref.__calcul_proba()
                noeud_ref.futur_bas = noeud_ref.bas.futur_centre
                noeud_ref.futur_haut = Noeud(noeud_ref.futur_centre.prix_sj * noeud_ref.arbre.alpha, noeud_ref.arbre, noeud_ref.position_arbre + 1)
                noeud_ref.futur_haut.bas = noeud_ref.futur_centre
                noeud_ref.futur_centre.haut = noeud_ref.futur_haut
                noeud_ref.haut.futur_centre = noeud_ref.futur_haut
                noeud_ref.haut.futur_bas = noeud_ref.futur_centre
                noeud_ref = noeud_ref.haut
            
        #on retombe sur notre noeud le plus en haut
        self.futur_haut = Noeud(self.futur_centre.prix_sj * self.arbre.alpha, self.arbre, self.position_arbre + 1)
        self.__calcul_proba()
        self.futur_haut.bas = self.futur_centre
        self.futur_centre.haut = self.futur_haut
        self.futur_centre.precedent_centre = self

    def liaison_bas(self) -> None :         
        noeud_ref = self
          
        while not hasattr(noeud_ref.haut, "futur_bas"): 
            noeud_ref = noeud_ref.haut
                 
        if noeud_ref == self :
            self.futur_centre = self.haut.futur_bas
            self.futur_centre.precedent_centre = self
            self.__calcul_proba()
            self.futur_haut = self.haut.futur_centre
            
        else : 
            while not noeud_ref == self : 
                noeud_ref.futur_centre = noeud_ref.haut.futur_bas
                noeud_ref.futur_centre.precedent_centre = noeud_ref
                noeud_ref.__calcul_proba()
                noeud_ref.futur_haut = noeud_ref.haut.futur_centre
                noeud_ref.futur_bas = Noeud(noeud_ref.futur_centre.prix_sj * noeud_ref.arbre.alpha**(-1), noeud_ref.arbre, noeud_ref.position_arbre + 1)
                noeud_ref.futur_bas.haut = noeud_ref.futur_centre
                noeud_ref.futur_centre.bas = noeud_ref.futur_bas
                noeud_ref.bas.futur_centre = noeud_ref.futur_bas
                noeud_ref.bas.futur_haut = noeud_ref.futur_centre
                noeud_ref = noeud_ref.bas
            
        self.futur_bas = Noeud(self.futur_centre.prix_sj * self.arbre.alpha**(-1), self.arbre, self.position_arbre + 1)
        self.__calcul_proba()
        self.futur_haut.parent = self
        self.futur_bas.haut = self.futur_centre
        self.futur_centre.bas = self.futur_bas
        self.futur_centre.precedent_centre = self
        
    def calcul_valeur_intrinseque(self) -> None :
        


        if self.position_arbre == self.arbre.nb_pas : #si nous somme à la fin de l'arbre, nous prenons le maximum entre le payoff de l'option et 0
            
            if self.arbre.option.call : 
                payoff = self.prix_sj - self.arbre.option.prix_exercice
            else : 
                payoff = self.arbre.option.prix_exercice  - self.prix_sj
                
            self.valeur_intrinseque = max(payoff, 0)
            
        else : #si nous ne sommes pas à la fin de l'arbre, 
            
            vecteur_proba = np.array([self.p_haut, self.p_mid, self.p_bas]) #vecteur composé des probabilités des noeuds futurs du noeud actuel
            vecteur_prix = np.array([self.futur_haut.valeur_intrinseque, self.futur_centre.valeur_intrinseque, self.futur_bas.valeur_intrinseque]) #
            valeur_intrinseque = self.arbre.facteur_actualisation * vecteur_prix.dot(vecteur_proba) #ici, produit scalaire des prix par leurs probabilités
            
            if self.arbre.option.americaine : #dans le cas d'une option américaine, la valeur d'un noeud est égal au maximum entre le payoff de l'option et la valeur intrinseque définie plus haut 
                
                if self.arbre.option.call : 
                    payoff = self.prix_sj - self.arbre.option.prix_exercice
                else : 
                    payoff = self.arbre.option.prix_exercice  - self.prix_sj
                
                self.valeur_intrinseque = max(payoff, valeur_intrinseque) 
            else : #le prix est égal au produit scalaire du vecteur des prix des noeuds précédents par le vecteur de leurs probabilités pour un call 
                
                self.valeur_intrinseque = valeur_intrinseque 
                    
#TODO : possible de reproduire la même logique sur tout l'arbre (pricing avec des vecteurs avec un mouvement backward, nous permettant alors de venir de mettre en place de la parallelisation)
#TODO : le facteur d'actualisation peut être défini comme constante au niveau de l'arbre 


#TODO : (Idée) plutôt que venir calculer les probabilités et les prix à chaque création de noeud, venir créer un arbre ne contenant que la structure mais sur lequel nous n'aurons fait aucun calcul.
#Ensuite, se débrouiller à faire des opération matricielles pour appliquer des probas et prix sur l'ensemble de l'arbre 