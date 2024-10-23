from typing import Union
import datetime as dt
import copy

from Python.Classes.module_arbre_noeud import Arbre

class GrecquesEmpiriques : 
    def __init__(self, arbre : Arbre, var_s : float = 0.01, var_v : float = 0.01, var_t : int = 1, var_r : float = 0.01):
        
        self.arbre = arbre
        self.var_s = var_s
        self.var_v = var_v
        self.var_t = var_t
        self.var_r = var_r
        
        if not hasattr(self.arbre, "prix_option") : 
            self.arbre.pricer_arbre()
            
    def __pricer_arbre_choc(self, attribut_a_modifier : str, d : Union [float, dt.date]) -> Arbre : 
                
        nouvel_arbre = copy.copy(self.arbre)
        donnee_marche = copy.copy(self.arbre.donnee_marche)
        option = copy.copy(self.arbre.option)
        
        if attribut_a_modifier == "date_pricing" : 
            setattr(option, attribut_a_modifier, d)
            setattr(donnee_marche, "date_debut", d)
        elif attribut_a_modifier == "taux_interet" : #on part du principe que le choc sur les taux d'intérêt s'applique à la fois au facteur de capitalisation et d'actualisaition
            attribut_a_modifier_1 = "taux_interet"
            attribut_a_modifier_2 = "taux_actualisation"
            d1 = getattr(donnee_marche, attribut_a_modifier_1) + d
            d2 = getattr(donnee_marche, attribut_a_modifier_2) + d
            setattr(donnee_marche, attribut_a_modifier_1, d1)
            setattr(donnee_marche, attribut_a_modifier_2, d2)
        else : 
            d1 = getattr(donnee_marche, attribut_a_modifier) + d
            setattr(donnee_marche, attribut_a_modifier, d1)
        
        nouvel_arbre.__init__(nb_pas=self.arbre.nb_pas, donnee_marche=donnee_marche, option=option)
        nouvel_arbre.pricer_arbre()
        
        return nouvel_arbre
            
    def approxime_delta(self) -> float : 
        ds = self.var_s * self.arbre.donnee_marche.prix_spot
        neg_ds = -self.var_s * self.arbre.donnee_marche.prix_spot
        nouvel_arbre_1 = self.__pricer_arbre_choc("prix_spot", ds)
        nouvel_arbre_2 = self.__pricer_arbre_choc("prix_spot", neg_ds)
        # delta = (nouvel_arbre_1.prix_option - nouvel_arbre_2.prix_option) / 2 * self.var_s
        delta = (nouvel_arbre_1.prix_option - nouvel_arbre_2.prix_option) / 2 * ds
        
        #on stocke dans la classe la valeur de l'arbre choqué pour ne pas à avoir à recalculer si on calcule une dérivée de second ordre
        if not hasattr(self, "prix_nouvel_arbre_ds_1") :             
            self.prix_nouvel_arbre_ds_1 = nouvel_arbre_1.prix_option
          
        #idem ici
        if not hasattr(self, "prix_nouvel_arbre_ds_2") : 
            self.prix_nouvel_arbre_ds_2 = nouvel_arbre_2.prix_option
    
        return delta
    
    def approxime_gamma(self) -> float : 
        
        ds = self.var_s * self.arbre.donnee_marche.prix_spot
        neg_ds  = -self.var_s * self.arbre.donnee_marche.prix_spot
        
        if not hasattr(self, "prix_nouvel_arbre_ds_1") : 
            nouvel_arbre_1 = self.__pricer_arbre_choc("prix_spot", ds)
            self.prix_nouvel_arbre_ds_1 = nouvel_arbre_1.prix_option
            
        if not hasattr(self, "prix_nouvel_arbre_ds_2") : 
            nouvel_arbre_2 = self.__pricer_arbre_choc("prix_spot", neg_ds)
            self.prix_nouvel_arbre_ds_2 = nouvel_arbre_2.prix_option
            
        gamma = (self.prix_nouvel_arbre_ds_1 - 2 * self.arbre.prix_option + self.prix_nouvel_arbre_ds_2) / (ds**2)
    
        return gamma
    
    def approxime_vega(self) -> float : 
        
        dv = self.var_v 
        neg_dv = -self.var_v 
        nouvel_arbre_1 = self.__pricer_arbre_choc("volatilite", dv)
        nouvel_arbre_2 = self.__pricer_arbre_choc("volatilite", neg_dv)
        vega = (nouvel_arbre_1.prix_option - nouvel_arbre_2.prix_option) / 2 * dv * 100
    
        #on stocke dans la classe la valeur de l'arbre choqué pour ne pas à avoir à recalculer si on calcule une dérivée de second ordre
        if not hasattr(self, "vol_nouvel_arbre_dv_1") :             
            self.vol_nouvel_arbre_ds_1 = nouvel_arbre_1.prix_option
          
        #idem ici
        if not hasattr(self, "vol_nouvel_arbre_dv_2") : 
            self.vol_nouvel_arbre_ds_2 = nouvel_arbre_2.prix_option
    
        return vega
    
    def approxime_theta(self) -> float : 

        d_t = self.arbre.option.date_pricing + dt.timedelta(days=self.var_t)
        
        nouvel_arbre_1 = self.__pricer_arbre_choc("date_pricing", d_t)
        
        theta = nouvel_arbre_1.prix_option - self.arbre.prix_option
        
        #on stocke dans la classe la valeur de l'arbre choqué pour ne pas à avoir à recalculer si on calcule une dérivée de second ordre
        if not hasattr(self, "temps_nouvel_arbre_dt_1") :             
            self.theta_nouvel_arbre_ds_1 = nouvel_arbre_1.prix_option
            
        return theta
    
    def approxime_rho(self) -> float : 
        
        dr = self.var_r
        neg_dr = -self.var_r
        nouvel_arbre_1 = self.__pricer_arbre_choc("taux_interet", dr)
        nouvel_arbre_2 = self.__pricer_arbre_choc("taux_interet", neg_dr)
        rho = (nouvel_arbre_1.prix_option - nouvel_arbre_2.prix_option) / 2 * dr * 100
    
        #on stocke dans la classe la valeur de l'arbre choqué pour ne pas à avoir à recalculer si on calcule une dérivée de second ordre
        if not hasattr(self, "vol_nouvel_arbre_dr_1") :             
            self.rho_nouvel_arbre_ds_1 = nouvel_arbre_1.prix_option
          
        #idem ici
        if not hasattr(self, "vol_nouvel_arbre_dr_2") : 
            self.rho_nouvel_arbre_ds_2 = nouvel_arbre_2.prix_option
    
        return rho