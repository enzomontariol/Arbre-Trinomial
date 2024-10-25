#%% Imports

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D
import numpy as np
    
from module_arbre_noeud import Arbre
  
  
#%% Classes  
    
class Arbre_Graph :
    def __init__(self, arbre : Arbre, dimension_chart : tuple = (16, 12)):
        """Initialisation de la classe Arbre_Graph

        Args:
            arbre (Arbre): l'arbre pour lequel nous souhaitons réaliser le graphique
            dimension_chart (tuple, optional): la dimension de la fen^tre de sortie de notre graphique. Défaut à (16, 12).
        """
        self.arbre = arbre
        self.dimension_chart = dimension_chart
         
        #Dans le cas où l'arbre fournit en input n'aurait pas été pricé
        if self.arbre.prix_option is None : 
            self.arbre.pricer_arbre()
            
        if self.arbre.nb_pas > 10 : 
            raise ValueError("Nombre de pas dans l'arbre trop important pour être affiché. Veuillez choisir un nombre de pas inférieur à 10.")
        
    def afficher_arbre(self) -> None:
        """Fonction nous permettant de réaliser le graphique en positionnant les nœuds selon le prix sous-jacent."""
        
        # Initialisation de l'objet issu de la librairie networkx
        G = nx.DiGraph()
        labels = {}
        positions = {}
        queue = [(self.arbre.racine, 0)]
        
        # le niveau de la barrière
        niveau_barriere = self.arbre.option.barriere.niveau_barriere

        # Déterminer le prix max et min des sous-jacents pour ajuster l'échelle
        prix_min, prix_max = float('inf'), float('-inf')
        
        while queue:
            noeud, x = queue.pop(0)
            
            # Utilisation du prix sous-jacent pour la coordonnée y
            y = noeud.prix_sj

            # Mise à jour des limites des prix
            prix_min = min(prix_min, y)
            prix_max = max(prix_max, y)
            
            # Création d'un label pour chaque nœud : valeur_intrinseque, prix_sj, p_cumule
            noeud_label = f"{noeud.valeur_intrinseque:.2f}\n{noeud.prix_sj:.2f}\n{noeud.p_cumule:.6f}"
            labels[noeud] = noeud_label
            positions[noeud] = (x, y)
            G.add_node(noeud)
            
            # Nous itérons sur chaque futur nœud (bas, centre, haut)
            for direction, futur in zip(["bas", "centre", "haut"], [noeud.futur_bas, noeud.futur_centre, noeud.futur_haut]):
                if futur is not None:
                    # Probabilité correspondante à chaque direction
                    if direction == "bas":
                        prob = noeud.p_bas
                    elif direction == "centre":
                        prob = noeud.p_mid
                    elif direction == "haut":
                        prob = noeud.p_haut
                    else:
                        prob = 0  # au cas où, ne devrait pas arriver
                    
                    # Formatage de la probabilité
                    prob_label = f"{prob:.4f}"
                    
                    # Ajout de la ligne avec la probabilité en label
                    G.add_edge(noeud, futur, label=prob_label)
                    
                    # Ajout du nœud futur à la queue pour itérer dessus 
                    queue.append((futur, x + 1))
        
        plt.figure(figsize=self.dimension_chart)
        
        # Ajuster les limites de l'axe des y selon les prix sous-jacents
        y_margin = (prix_max - prix_min) * 0.05  # Ajout d'une marge de 10% en haut et en bas
        plt.ylim(prix_min - y_margin, prix_max + y_margin)

        # Dessiner les nœuds et leurs labels
        nx.draw_networkx_nodes(G, pos=positions, node_size=2500, node_color='lightblue')
        nx.draw_networkx_labels(G, pos=positions, labels=labels, font_size=10)
        
        # Extraction des labels des lignes
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edges(G, pos=positions, arrows=True, arrowstyle='-|>', arrowsize=20)
        nx.draw_networkx_edge_labels(G, pos=positions, edge_labels=edge_labels, font_color='red', font_size=8, label_pos=0.3)
        
        # Ajout d'une ligne horizontale pour représenter la barrière à son niveau correct
        plt.axhline(y=niveau_barriere, color='green', linestyle='--', label=f'Barrière : {niveau_barriere:.2f}')
        
        # Ajout d'un titre au graphique, on fait s'adapter le titre à ce qu'on graphe
        
        if self.arbre.option.call : 
            type_option = "call"
        else : 
            type_option = "put"
            
        if self.arbre.option.americaine : 
            exercice_option = "américaine"
        else : 
            exercice_option = "européenne"
            
        strike = self.arbre.option.prix_exercice
        
        barriere_titre=""
        
        if self.arbre.option.barriere.direction_barriere : 
            barriere_titre = f", barrière {self.arbre.option.barriere.type_barriere.value} {self.arbre.option.barriere.direction_barriere.value} {self.arbre.option.barriere.niveau_barriere}"
        
        plt.title(f"Arbre Trinomial, option {type_option} {exercice_option}, strike {strike}{barriere_titre}", fontsize=16)

        # Ajout d'une légende
        
        #casq barrière
        if self.arbre.option.barriere.direction_barriere : 
            legend_elements = [
                Line2D([0], [0], marker='o', color='w', label='Noeud:',
                    markerfacecolor='lightblue', markersize=15),
                Line2D([0], [0], label="Valeur intrinsèque (Haut)", color='w'),
                Line2D([0], [0], label="Prix Sous-Jacent (Centre)", color='w'),
                Line2D([0], [0], label="Probabilité cumulée (Bas)", color='w'),
                Line2D([0], [0], color='red', lw=2, label='Probabilité de passage'),
                Line2D([0], [0], color='green', lw=2, linestyle='--', label=f'Barrière : {niveau_barriere:.2f}')
            ]
            
        #Cas sans barrière
        else : 
            legend_elements = [
                Line2D([0], [0], marker='o', color='w', label='Noeud:',
                    markerfacecolor='lightblue', markersize=15),
                Line2D([0], [0], label="Valeur intrinsèque (Haut)", color='w'),
                Line2D([0], [0], label="Prix Sous-Jacent (Centre)", color='w'),
                Line2D([0], [0], label="Probabilité cumulée (Bas)", color='w'),
                Line2D([0], [0], color='red', lw=2, label='Probabilité de passage')
            ]

        plt.legend(handles=legend_elements, loc='upper left', fontsize=10)
        
        plt.tight_layout()
        plt.show()
