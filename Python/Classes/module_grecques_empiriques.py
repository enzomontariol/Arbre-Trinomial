from typing import Union
import datetime as dt

from Python.Classes.module_arbre import Arbre
from module_enums import DifferenceFinieType          

class GrecquesEmpiriques : 
    def __init__(self, arbre : Arbre, var_s : float = 0.01, var_v : float = 0.01, var_t : int = 1, var_r : float = 0.01, difference_finie_type : DifferenceFinieType = DifferenceFinieType.centree):
        
        self.arbre = arbre
        self.var_s = var_s
        self.var_v = var_v
        self.var_t = var_t
        self.var_r = var_r
        self.difference_finie_type = difference_finie_type
        
        if not hasattr(self.arbre, "prix_option") : 
            self.arbre.pricer_arbre()
            
    def __pricer_arbre_choc(self, attribut_a_modifier : str, d : Union [float, dt.date]) -> Arbre : 
        
        nouvel_arbre = self.arbre
        
        if attribut_a_modifier == "maturite" : 
            attribut_a_modifier = f"option.{attribut_a_modifier}"
            setattr(nouvel_arbre, attribut_a_modifier, d)
        elif attribut_a_modifier == "taux_interet" : #on part du principe que le choc sur les taux d'intérêt s'applique à la fois au facteur de capitalisation et d'actualisaition
            attribut_a_modifier_1 = f"donnee_marche.taux_interet"
            attribut_a_modifier_2 = f"donnee_marche.taux_actualisation"
            setattr(nouvel_arbre, attribut_a_modifier_1, d)
            setattr(nouvel_arbre, attribut_a_modifier_2, d)
        else : 
            attribut_a_modifier = f"donnee_marche.{attribut_a_modifier}"
            setattr(nouvel_arbre, attribut_a_modifier, d)
        
        nouvel_arbre.__init__
        nouvel_arbre.pricer_arbre()
        
        return nouvel_arbre
            
    def approxime_delta(self) -> float : 
        ds = self.var_s * self.arbre.donnee_marche.prix_spot
        neg_ds = -self.var_s * self.arbre.donnee_marche.prix_spot
        nouvel_arbre_1 = self.__pricer_arbre_choc("prix_spot", ds)
        nouvel_arbre_2 = self.__pricer_arbre_choc("prix_spot", neg_ds)
        delta = (nouvel_arbre_1.prix_option - nouvel_arbre_2.prix_option) / 2 * self.var_s
    
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
            
        gamma = (self.prix_nouvel_arbre_ds_1 - 2 * self.arbre.prix_option + self.prix_nouvel_arbre_ds_2) / (self.var_s**2)
    
        return gamma
    
    def approxime_vega(self) -> float : 
        
        dv = self.var_v * self.arbre.donnee_marche.volatilite
        neg_dv = -self.var_v * self.arbre.donnee_marche.volatilite
        nouvel_arbre_1 = self.__pricer_arbre_choc("volatilite", dv)
        nouvel_arbre_2 = self.__pricer_arbre_choc("volatilite", neg_dv)
        vega = (nouvel_arbre_1.prix_option - nouvel_arbre_2.prix_option) / 2 * self.var_v
    
        #on stocke dans la classe la valeur de l'arbre choqué pour ne pas à avoir à recalculer si on calcule une dérivée de second ordre
        if not hasattr(self, "vol_nouvel_arbre_ds_1") :             
            self.vol_nouvel_arbre_ds_1 = nouvel_arbre_1.prix_option
          
        #idem ici
        if not hasattr(self, "vol_nouvel_arbre_ds_2") : 
            self.vol_nouvel_arbre_ds_2 = nouvel_arbre_2.prix_option
    
        return vega
    
    def approxime_theta(self) -> float : 

        dt = self.arbre.option.maturite + dt.timedelta(days=self.var_t)
        
        nouvel_arbre_1 = self.__pricer_arbre_choc("maturite", dt)
        
        theta = (nouvel_arbre_1.prix_option - self.arbre.prix_option) / (self.var_t / self.arbre.convention_base_calendaire)
        
        #on stocke dans la classe la valeur de l'arbre choqué pour ne pas à avoir à recalculer si on calcule une dérivée de second ordre
        if not hasattr(self, "temps_nouvel_arbre_ds_1") :             
            self.temps_nouvel_arbre_ds_1 = nouvel_arbre_1.prix_option
            
        return theta
    
    def approxime_rho(self) -> float : 
        
        dr = self.var_r * self.arbre.donnee_marche.taux_interet
        neg_dr = -self.var_r * self.arbre.donnee_marche.taux_interet
        nouvel_arbre_1 = self.__pricer_arbre_choc("taux_interet", dr)
        nouvel_arbre_2 = self.__pricer_arbre_choc("taux_interet", neg_dr)
        rho = (nouvel_arbre_1.prix_option - nouvel_arbre_2.prix_option) / 2 * self.var_r
    
        #on stocke dans la classe la valeur de l'arbre choqué pour ne pas à avoir à recalculer si on calcule une dérivée de second ordre
        if not hasattr(self, "taux_nouvel_arbre_ds_1") :             
            self.taux_nouvel_arbre_ds_1 = nouvel_arbre_1.prix_option
          
        #idem ici
        if not hasattr(self, "taux_nouvel_arbre_ds_2") : 
            self.taux_nouvel_arbre_ds_2 = nouvel_arbre_2.prix_option
    
        return rho
        