#%% Imports

import numpy as np

from Classes.module_marche import DonneeMarche
from Classes.module_option import Option
from Classes.module_enums import ConventionBaseCalendaire

#%% Classes

class Arbre : 
    def __init__(self, nb_pas : int, donnee_marche : DonneeMarche, option : Option,
                 convention_base_calendaire : ConventionBaseCalendaire = ConventionBaseCalendaire._365.value, 
                 pruning : bool = True) -> None:
        """Initialisation de la classe

        Args:
            nb_pas (float): le nombre de pas dans notre modèle
            donnee_marche (DonneeMarche): Classe utilisée pour représenter les données de marché.
            option (Option): Classe utilisée pour représenter une option et ses paramètres.
            convention_base_calendaire (ConventionBaseCalendaire, optional): la base calendaire que nous utiliserons pour nos calculs. Défaut ConventionBaseCalendaire._365.value.
            pruning (bool, optional): si l'on va ou non faire du "pruning". Défaut True.
        """
        self.nb_pas = nb_pas
        self.donnee_marche = donnee_marche
        self.option = option
        self.convention_base_calendaire = convention_base_calendaire
        self.pruning = pruning
        self.delta_t = self.__calcul_delta_t()
        self.facteur_capitalisation = self.__calcul_facteur_capitalisation()
        self.facteur_actualisation = self.__calcul_facteur_actualisation()
        self.position_div = self.__calcul_position_div()
        self.alpha = self.__calcul_alpha()
        self.racine = None
        self.prix_option = None
           
    def get_temps (self) -> float : 
        """Renvoie le temps à maturité exprimé en nombre d'année .

        Returns:
            float: temps à maturité en nombre d'année
        """
        
        return (self.option.maturite - self.option.date_pricing).days/self.convention_base_calendaire
    
    def __calcul_delta_t (self) -> float : 
        """Permet de calculer l'intervalle de temps de référence qui sera utilisée dans notre modèle.

        Returns:
            float: l'intervalle de temps delta_t
        """
        
        return self.get_temps() / self.nb_pas
    
    def __calcul_facteur_capitalisation(self) -> float : 
        """Permet de calculer le facteur de capitalisation que nous utiliserons par la suite

        Returns:
            float: un facteur de capitalisation à appliquer à chaque dt.
        """
        
        return np.exp(self.donnee_marche.taux_interet * self.delta_t)
    
    def __calcul_facteur_actualisation(self) -> float :
        """Permet de calculer le facteur d'actualisation que nous utiliserons par la suite


        Returns:
            float: un facteur d'actualisation à appliquer à chaque dt.
        """
        
        return np.exp(-self.donnee_marche.taux_actualisation * self.delta_t)
 
    def __calcul_alpha (self) -> float : 
        """Fonction nous permettant de calculer alpha, que nous utiliserons dans l'arbre.

        Returns:
            float: Nous renvoie le coefficient alpha
        """
        
        alpha = np.exp(self.donnee_marche.volatilite * np.sqrt(3) * np.sqrt(self.delta_t))
        
        return alpha 
    
    def __calcul_position_div (self) -> float : 
        """Nous permet de calculer la position du dividende dans l'arbre

        Returns:
            float: nous renvoie la position d'ex-date du div, exprimé en nombre de pas dans l'arbre.
        """
        
        nb_jour_detachement = (self.donnee_marche.dividende_ex_date - self.option.date_pricing).days
        position_div = nb_jour_detachement / self.convention_base_calendaire / self.delta_t
        
        return position_div
    
    def __planter_arbre(self) -> None : 
        """Procédure nous permettant de construire notre arbre
        """
        
        ##Import du module noeud dans la fonction, afin d'éviter un appel récursif lors de l'instanciation de la classe (Noeud appelant déjà Arbre)
        from Classes.module_noeud import Noeud
        
        def creer_prochain_block_haut(actuel_centre : Noeud, prochain_noeud : Noeud) -> None : 
            """Procédure nous permettant de construire un bloc complet vers le haut à partir d'un noeud de référence et d'un noeud futur

            Args:
                actuel_centre (Noeud): notre noeud de référence
                prochain_noeud (Noeud): le noeud autour duquel nous allons créer le bloc
            """
            temp_centre = actuel_centre
            temp_futur_centre = prochain_noeud
            
            #Nous iterrons en partant du tronc et en nous dirigeant vers l'extrêmité haute d'une colonne afin de créer des noeuds sur la colonne suivante
            while not temp_centre.haut is None : 
                temp_centre = temp_centre.haut
                temp_centre.creer_prochain_block(temp_futur_centre)
                temp_futur_centre = temp_futur_centre.haut
                
        def creer_prochain_block_bas(actuel_centre : Noeud, prochain_noeud : Noeud) -> None : 
            """Procédure nous permettant de construire un bloc complet vers le bas à partir d'un noeud de référence et d'un noeud futur

            Args:
                actuel_centre (Noeud): notre noeud de référence
                prochain_noeud (Noeud): le noeud autour duquel nous allons créer le bloc
            """            
            temp_centre = actuel_centre
            temp_futur_centre = prochain_noeud
            
            #Nous iterrons en partant du tronc et en nous dirigeant vers l'extrêmité basse d'une colonne afin de créer des noeuds sur la colonne suivante
            while not temp_centre.bas is None : 
                temp_centre = temp_centre.bas
                temp_centre.creer_prochain_block(temp_futur_centre)
                temp_futur_centre = temp_futur_centre.bas
                
        def creer_nouvelle_col(self, actuel_centre : Noeud) -> Noeud :
            """Procédure nous permettant de créer entièrement une colonne de notre arbre.

            Args:
                actuel_centre (Noeud): le noeud sur le tronc actuel, que nous prenons en référence et à partir duquel nous créerons la colonne suivante.

            Returns:
                Noeud: nous renvoyons le futur noeud sur le centre afin de faire itérer cette fonction dessus
            """
            
            prochain_noeud = Noeud(actuel_centre._calcul_forward(), self, actuel_centre.position_arbre + 1)
            
            actuel_centre.creer_prochain_block(prochain_noeud)
            creer_prochain_block_haut(actuel_centre, prochain_noeud)
            creer_prochain_block_bas(actuel_centre, prochain_noeud)
            
            return prochain_noeud
        
        #Nous créons la racine de notre arbre ici, ne pouvant le faire au niveau de __init__ afin d'éviter un import récursif
        self.racine = Noeud(prix_sj = self.donnee_marche.prix_spot, arbre = self, position_arbre=0)
        
        #Notre première référence est la racine
        actuel_centre = self.racine
        
        #Nous créons ici le premier bloc. Nous itérerons ensuite sur autant de pas que nécéssaire afin de créer les colonnes suivantes.
        for pas in range(self.nb_pas) :
            actuel_centre = creer_nouvelle_col(self, actuel_centre)
            
    def pricer_arbre(self) -> None : 
        """Fonction qui nous permettra de construire l'arbre puis de le valoriser pour enfin donner la valeur à l'attribut "prix_option".
        """
        self.__planter_arbre()
        
        self.racine.calcul_valeur_intrinseque()
        self.prix_option = self.racine.valeur_intrinseque