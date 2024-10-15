#%% Imports

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D

from module_marche import DonneeMarche
from module_option import Option
from module_enums import ConventionBaseCalendaire

#%% Classes

class Arbre : 
    def __init__(self, nb_pas : int, donnee_marche : DonneeMarche, option : Option, convention_base_calendaire : ConventionBaseCalendaire = ConventionBaseCalendaire._365.value, pruning : bool = True) -> None:
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
        self.pruning = pruning
        self.delta_t = self.__calcul_delta_t()
        self.facteur_capitalisation = self.__calcul_facteur_capitalisation()
        self.facteur_actualisation = self.__calcul_facteur_actualisation()
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
    
    def __calcul_facteur_capitalisation(self) -> float : 
        
        return np.exp(self.donnee_marche.taux_interet * self.delta_t)
    
    def __calcul_facteur_actualisation(self) -> float :
        
        return np.exp(-self.donnee_marche.taux_actualisation * self.delta_t)
 
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
    
    def planter_arbre(self) -> None : 
        
        from module_noeud import Noeud
        
        def creer_prochain_block_haut(actuel_centre : Noeud, prochain_noeud : Noeud) -> None : 
            
            temp_centre = actuel_centre
            temp_futur_centre = prochain_noeud
            
            while not temp_centre.haut is None : 
                temp_centre = temp_centre.haut
                temp_centre.creer_prochain_block(temp_futur_centre)
                # temp_centre.futur_bas = temp_futur_centre
                temp_futur_centre = temp_futur_centre.haut
                
        def creer_prochain_block_bas(actuel_centre : Noeud, prochain_noeud : Noeud) -> None : 
            
            temp_centre = actuel_centre
            temp_futur_centre = prochain_noeud
            
            while not temp_centre.bas is None : 
                temp_centre = temp_centre.bas
                temp_centre.creer_prochain_block(temp_futur_centre)
                # temp_centre.futur_haut = temp_futur_centre
                temp_futur_centre = temp_futur_centre.bas
                

        def creer_nouvelle_col(self, actuel_centre : Noeud) -> Noeud : 
            
            prochain_noeud = Noeud(actuel_centre._calcul_forward(), self, actuel_centre.position_arbre + 1)
            
            actuel_centre.creer_prochain_block(prochain_noeud)
            creer_prochain_block_haut(actuel_centre, prochain_noeud)
            creer_prochain_block_bas(actuel_centre, prochain_noeud)
            
            return prochain_noeud
        
        self.racine = Noeud(prix_sj = self.donnee_marche.prix_spot, arbre = self, position_arbre=0)
        
        actuel_centre = self.racine
        
        for pas in range(self.nb_pas) :
            actuel_centre = creer_nouvelle_col(self, actuel_centre)
            
    def pricer_arbre(self) -> None : 
        self.planter_arbre()
        
        self.racine.calcul_valeur_intrinseque()
        self.prix_option = self.racine.valeur_intrinseque

    def visualize_tree(self) -> None:

        G = nx.DiGraph()
        labels = {}
        positions = {}
        queue = [(self.racine, 0, 0)]
        
        while queue:
            node, x, y = queue.pop(0)
            
            # Create a multi-line label for each node:
            # 1. valeur_intrinseque (intrinsic value) on the top
            # 2. prix_sj (price of underlying asset) in the center
            # 3. p_cumule (cumulative probability) on the bottom
            node_label = f"{node.valeur_intrinseque:.2f}\n{node.prix_sj:.2f}\n{node.p_cumule:.6f}"
            labels[node] = node_label
            positions[node] = (x, y)
            G.add_node(node)
            
            # Iterate through each direction and corresponding child node
            for direction, child in zip(["bas", "centre", "haut"], [node.futur_bas, node.futur_centre, node.futur_haut]):
                if child is not None:
                    # Retrieve the corresponding probability based on direction
                    if direction == "bas":
                        prob = node.p_bas
                    elif direction == "centre":
                        prob = node.p_mid
                    elif direction == "haut":
                        prob = node.p_haut
                    else:
                        prob = 0  # Fallback, should not occur
                    
                    # Format the probability to four decimal places
                    prob_label = f"{prob:.4f}"
                    
                    # Add edge with probability as the label
                    G.add_edge(node, child, label=prob_label)
                    
                    # Append the child node to the queue for further processing
                    queue.append((child, x + 1, y - 1 if direction == "bas" else y + 1 if direction == "haut" else y))
        
        plt.figure(figsize=(32, 24))
        
        # Draw the nodes with labels
        nx.draw_networkx_nodes(G, pos=positions, node_size=2500, node_color='lightblue')
        nx.draw_networkx_labels(G, pos=positions, labels=labels, font_size=10)
        
        # Extract edge labels (probabilities)
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edges(G, pos=positions, arrows=True, arrowstyle='-|>', arrowsize=20)
        nx.draw_networkx_edge_labels(G, pos=positions, edge_labels=edge_labels, font_color='red', font_size=8)

        # Add a title to the plot
        plt.title("Arbre d'Option Pricing avec Probabilités, Valeur Intrinsèque et p_cumule", fontsize=16)

        # Add a legend explaining the labels
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label='Noeud:',
                markerfacecolor='lightblue', markersize=15),
            Line2D([0], [0], label="Valeur Intrinsèque (Top): Intrinsic Value", color='w'),
            Line2D([0], [0], label="Prix_sj (Middle): Price of the Underlying Asset", color='w'),
            Line2D([0], [0], label="p_cumule (Bottom): Cumulative Probability", color='w'),
            Line2D([0], [0], color='red', lw=2, label='Probabilité (Edge)')
        ]

        plt.legend(handles=legend_elements, loc='upper left', fontsize=10)
        
        plt.axis('off')  # Hide the axes
        plt.tight_layout()
        plt.show()
   
        
#%% debugging zone

if __name__ == "__main__" : 
    
    import datetime as dt
    import time
    import sys
    
    sys.setrecursionlimit(10000)
    
    start = time.time()
    
    today = dt.date.today()
    today_1y = dt.date(today.year+1, today.month, today.day)

    spot = 100 
    vol = 0.2
    discount_rate = risk_free = 0.04 
    dividende_ex_date = dt.date(today.year+1, today.month-6, today.day) 
    dividende_montant = 4 

    strike = 100
    expiry = today_1y 

    nb_pas = 1000

    donnée = DonneeMarche(today, spot, vol, discount_rate, risk_free, dividende_ex_date=dividende_ex_date, dividende_montant=dividende_montant)
    option = Option(maturite = expiry, prix_exercice = strike, call = True, date_pricing = today, americaine=False)

    arbre = Arbre(nb_pas, donnée, option, pruning = True)
        
    arbre.pricer_arbre()
    
    done = time.time()
    diff_temps = done - start
    
    print(f"Prix option {arbre.prix_option}")
    print(f'Temps pricing (secondes): {round(diff_temps, 1)}')
    # arbre.visualize_tree() #marche pour un nombre de pas < 11