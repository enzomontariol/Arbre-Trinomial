#%% Imports

from __future__ import annotations

import numpy as np

from Classes.module_arbre import Arbre

#%% Constantes

somme_proba = 1
prix_min_sj = 0 #on part du principe que le prix du sous-jacent ne peut être négatif (ce qui dans le cas d'un actif purement financier sera à priori toujours vrai)
epsilon = 0.00000001 #notre seuil de pruning


#%% Classes

class Noeud :
    def __init__(self, prix_sj : float, arbre : Arbre, position_arbre : int) -> None:
        """Initialisation de la classe

        Args:
            prix_sj (float): le prix du sous-jacent de ce noeud
            arbre (Arbre): l'arbre auquel est rattaché notre noeud
            position_arbre (int): decrit la position du noeud dans l'arbre sur l'axe horizontal
        """
        self.prix_sj = prix_sj
        self.arbre = arbre
        self.position_arbre = position_arbre 
        
        self.bas = None
        self.haut = None
        self.precedent_centre = None
        self.futur_bas = None
        self.futur_centre = None
        self.futur_haut = None 
        self.p_bas = None
        self.p_mid = None
        self.p_haut = None
        self.p_cumule = 1 if self.position_arbre == 0 else 0
        
        self.valeur_intrinseque = None
        
    def _calcul_forward(self) -> float : 
        """Permet de calculer la valeur du prix forward sur dt suivant
        
        Returns:
            float : prix forward
        """
        
        if self.position_arbre < self.arbre.position_div and self.position_arbre + 1 > self.arbre.position_div : 
            div = self.arbre.donnee_marche.dividende_montant
        else : 
            div = 0
            
        return self.prix_sj * self.arbre.facteur_capitalisation - div
    
    def __calcul_variance(self) -> float : 
        """Nous permet de calculer la variance

        Returns:
            float: variance
        """
        
        return (self.prix_sj ** 2) * np.exp(2 * self.arbre.donnee_marche.taux_interet * self.arbre.delta_t) * (np.exp((self.arbre.donnee_marche.volatilite ** 2) * self.arbre.delta_t) - 1)
    
    def __calcul_proba(self) -> None :
        """Nous permet de calculer les probabilités haut, centre, bas.
        """
        
        fw = self._calcul_forward()
       
        p_bas = ((self.futur_centre.prix_sj ** (-2)) * (self.__calcul_variance() + fw ** 2)
                      - 1 - (self.arbre.alpha + 1) * ((self.futur_centre.prix_sj ** (-1)) * fw - 1)) / ((1 - self.arbre.alpha) * (self.arbre.alpha ** (-2) - 1))
                     
        p_haut = (((1 / self.futur_centre.prix_sj * fw - 1) - (1 / self.arbre.alpha - 1) * p_bas) /
                       (self.arbre.alpha - 1))
        
        p_mid = 1 - p_haut - p_bas
        
        if not (p_bas > 0 and p_haut > 0 and p_mid > 0) :
            raise ValueError("Probabilité négative")
        
        if not np.isclose(p_bas + p_haut + p_mid, somme_proba, atol=1e-2) : 
            print(f"p_bas : {p_bas}, p_haut : {p_haut}, p_mid : {p_mid}")
            raise ValueError(f"La somme des probabilités doit être égale à {somme_proba}")
        else :             
            self.p_bas = p_bas
            self.p_haut = p_haut
            self.p_mid = p_mid      
            
    def __test_noeud_proche(self, forward : float) -> bool : 
        """Cette fonction nous permet de tester si le noeud est compris entre un prix d'un noeud haut ou d'un noeud bas.

        Args:
            forward (float): le prix forward de notre noeud que l'on aura calculé préalablement.

        Returns:
            bool: passage du test ou non 
        """
        condition_1 = (self.prix_sj * (1 + 1/self.arbre.alpha) / 2 <= forward)
        condition_2 = (forward <= self.prix_sj * (1 + self.arbre.alpha) / 2)

        # print(condition_1 and condition_2, self.position_arbre, self.prix_sj, forward)
        if condition_1 and condition_2:
            return True
        else : 
            #x = input('aaaadsioqjfosiejo')
            return False
        
    def bas_suivant(self) -> Noeud : 
        """Nous permet de créer le noeud bas suivant si il n'existe pas déjà.

        Returns:
            Noeud: le noeud bas
        """
        if self.bas == None : 
            self.bas = Noeud(self.prix_sj / self.arbre.alpha, self.arbre, self.position_arbre)
            self.bas.haut = self
        return self.bas
            
    def haut_suivant(self) -> Noeud : 
        """Nous permet de créer le noeud haut suivant si il n'existe pas déjà.

        Returns:
            Noeud: le noeud haut
        """
        if self.haut == None : 
            self.haut = Noeud(self.prix_sj * self.arbre.alpha, self.arbre, self.position_arbre)
            self.haut.bas = self   
        return self.haut  
                
    def trouve_centre(self, prochain_noeud : Noeud) -> Noeud : 
        """Fonction nous permettant de retrouver le prochain noeud centre.

        Args:
            prochain_noeud (Noeud): noeud candidat

        Returns:
            Noeud: le centre de notre noeud de référence.
        """
        
        fw = self._calcul_forward()

        #if self.position_arbre > 390:
            #print(self.position_arbre,self.prix_sj)
            #print(self.position_arbre,prochain_noeud.prix_sj)
            #a = input('noooo')

        if prochain_noeud.__test_noeud_proche(fw) : 
            prochain_noeud = prochain_noeud
            
        elif (not prochain_noeud.__test_noeud_proche(fw)) and fw > prochain_noeud.prix_sj : 
            while not prochain_noeud.__test_noeud_proche(fw) :
                #print('lie haut')
                prochain_noeud = prochain_noeud.haut_suivant()
        else:
        #elif (not prochain_noeud.__test_noeud_proche(fw)) and fw < prochain_noeud.prix_sj : 
            while not prochain_noeud.__test_noeud_proche(fw) : 
                #print('lie bas')
                prochain_noeud = prochain_noeud.bas_suivant()
            
        return prochain_noeud

    def creer_prochain_block(self, prochain_noeud : Noeud) -> None :
        """Nous permet de créer un bloc de noeud complet.

        Args:
            prochain_noeud (Noeud): _description_
        """

        self.futur_centre = self.trouve_centre(prochain_noeud=prochain_noeud)
        self.__calcul_proba()
        
        self.futur_centre.p_cumule += self.p_cumule * self.p_mid
        self.futur_centre.precedent_centre = self
        
        if self.arbre.pruning : 
            if  self.haut == None :
                if self.p_cumule * self.p_haut >= epsilon :  
                    self.futur_haut = self.futur_centre.haut_suivant()
                    self.futur_haut.p_cumule +=  self.p_cumule *  self.p_haut           
                else : 
                    # self.p_mid += self.p_haut
                    self.p_haut = 0
            elif not self.haut == None : 
                self.futur_haut = self.futur_centre.haut_suivant()
                self.futur_haut.p_cumule += self.p_cumule * self.p_haut
                
            if self.bas == None : 
                if self.p_cumule * self.p_bas >= epsilon : 
                    self.futur_bas = self.futur_centre.bas_suivant()
                    self.futur_bas.p_cumule += self.p_cumule * self.p_bas
                else : 
                    # self.p_mid += self.p_bas
                    self.p_bas = 0
            elif not self.bas == None : 
                self.futur_bas = self.futur_centre.bas_suivant()
                self.futur_bas.p_cumule += self.p_cumule * self.p_bas
              
        if not self.arbre.pruning :
            self.futur_haut = self.futur_centre.haut_suivant()
            self.futur_haut.p_cumule += self.p_cumule * self.p_haut
            self.futur_bas = self.futur_centre.bas_suivant()
            self.futur_bas.p_cumule += self.p_cumule * self.p_bas

    def calcul_payoff(self) -> float : 
        if self.arbre.option.call : 
            payoff = self.prix_sj - self.arbre.option.prix_exercice
        else : 
            payoff = self.arbre.option.prix_exercice - self.prix_sj
        payoff = max(payoff, 0)
        return payoff
    
    def calcul_valeur_intrinseque(self) -> None : 
        
        if self.futur_centre is None : 
            #print(self.position_arbre,self.prix_sj,self.futur_centre)
            self.valeur_intrinseque = self.calcul_payoff()
            #print("in")
        
        elif self.valeur_intrinseque == None : 
            
            for futur_noeud in ["futur_haut", "futur_centre", "futur_bas"] :
                if getattr(self, futur_noeud) is None :
                    setattr(self, futur_noeud, Noeud(0, self.arbre, self.position_arbre+1))
                    noeud = getattr(self, futur_noeud)
                    noeud.valeur_intrinseque = 0
                else : 
                    noeud = getattr(self, futur_noeud)
                    if getattr(noeud, "valeur_intrinseque") is None  :
                        noeud.calcul_valeur_intrinseque()
                    
            vecteur_proba = np.array([self.p_haut, self.p_mid, self.p_bas]) #vecteur composé des probabilités des noeuds futurs du noeud actuel
            vecteur_prix = np.array([self.futur_haut.valeur_intrinseque, self.futur_centre.valeur_intrinseque, self.futur_bas.valeur_intrinseque]) #
            valeur_intrinseque = self.arbre.facteur_actualisation * vecteur_prix.dot(vecteur_proba) #ici, produit scalaire des prix par leurs probabilités
            
            if self.arbre.option.americaine : 
                valeur_intrinseque = max(self.calcul_payoff(), valeur_intrinseque)
                
            self.valeur_intrinseque = valeur_intrinseque
            #x = input("ecris")
            #print("vecteur_proba", vecteur_proba)
            #print("vecteur_prix", vecteur_prix)
        #print('valeur_intrinseque',self.valeur_intrinseque )

    def calcul_valeur_intrinsequed(self) -> None : 
        print('aaaaaa')


        if (self.futur_centre is None) and (self.futur_haut is None) and (self.futur_bas is None) : 
            
            self.valeur_intrinseque = self.calcul_payoff()
            print('in',self.position_arbre,self.precedent_centre.prix_sj,self.prix_sj,self.valeur_intrinseque)
       



        elif self.valeur_intrinseque == None : 
            #for futur_noeud in ["futur_haut", "futur_centre", "futur_bas"] :
            SommeProba = 0
            if not getattr(self, "futur_haut") is None :
                # print(self.p_haut)
                # print(self.futur_haut.prix_sj)
                # attributs_non_none = [attr for attr in dir(self.futur_haut) 
                #       if not callable(getattr(self.futur_haut, attr)) 
                #       and not attr.startswith("__") 
                #       and getattr(self.futur_haut, attr) is not None]

                # print('=========',attributs_non_none)
                # print(self.futur_haut)
                print('bbbb')
                ExpectationUp = self.p_haut * self.futur_haut.calcul_valeur_intrinseque()
                SommeProba = SommeProba + self.p_haut
                #x = input("ecris")
            else:
                ExpectationUp = 0
            
            if not getattr(self, "futur_centre") is None :
                print('cc')
                ExpectationMid = self.p_mid * self.futur_centre.calcul_valeur_intrinseque()
                SommeProba = SommeProba + self.p_mid
            else:
                ExpectationMid = 0
            
            if not getattr(self, "futur_bas") is None :
                ExpectationDown = self.p_bas * self.futur_bas.calcul_valeur_intrinseque()
                SommeProba = SommeProba + self.p_bas
            else:
                ExpectationDown = 0

                
            self.valeur_intrinseque = (ExpectationUp + ExpectationMid + ExpectationDown) / self.arbre.facteur_actualisation / SommeProba
            #x = input("ecris")
            print(self.valeur_intrinseque)

                # if getattr(self, futur_noeud) is None :
                #     setattr(self, futur_noeud, Noeud(0, self.arbre, self.position_arbre+1))
                #     noeud = getattr(self, futur_noeud)
                #     noeud.valeur_intrinseque = 0
                # else : 
                #     noeud = getattr(self, futur_noeud)
                #     if getattr(noeud, "valeur_intrinseque") is None  :
                #         noeud.calcul_valeur_intrinseque()
                    
            # vecteur_proba = np.array([self.p_haut, self.p_mid, self.p_bas]) #vecteur composé des probabilités des noeuds futurs du noeud actuel
            # vecteur_prix = np.array([self.futur_haut.valeur_intrinseque, self.futur_centre.valeur_intrinseque, self.futur_bas.valeur_intrinseque]) #
            # valeur_intrinseque = self.arbre.facteur_actualisation * vecteur_prix.dot(vecteur_proba) #ici, produit scalaire des prix par leurs probabilités
            
            # if self.arbre.option.americaine : 
            #     valeur_intrinseque = max(self.calcul_payoff(), valeur_intrinseque)
                
            # self.valeur_intrinseque = valeur_intrinseque
        return(self.valeur_intrinseque)
    

    

            
# %%
