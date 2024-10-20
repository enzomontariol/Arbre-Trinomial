#%% Imports

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D
    
from Classes.module_arbre import Arbre
  
  
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
        """Fonction nous permettant de réaliser le graphique
        """
        
        #Initialisation de l'objet issu de la librairie networkx
        G = nx.DiGraph()
        labels = {}
        positions = {}
        queue = [(self.arbre.racine, 0, 0)]
        
        while queue:
            noeud, x, y = queue.pop(0)
            
            # Création d'un label pour chaque noeuds:
            # 1. valeur_intrinseque
            # 2. prix_sj
            # 3. p_cumule
            noeud_label = f"{noeud.valeur_intrinseque:.2f}\n{noeud.prix_sj:.2f}\n{noeud.p_cumule:.6f}"
            labels[noeud] = noeud_label
            positions[noeud] = (x, y)
            G.add_node(noeud)
            
            # Nous iterons sur chaque futur noeud
            for direction, futur in zip(["bas", "centre", "haut"], [noeud.futur_bas, noeud.futur_centre, noeud.futur_haut]):
                if futur is not None:
                    # Nous prenons la probabilité correspondante à chaque noeud
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
                    
                    # Nous ajoutons une ligne avec la proba en label
                    G.add_edge(noeud, futur, label=prob_label)
                    
                    # Ajout du noeud futur à la queue pour itérer dessus 
                    queue.append((futur, x + 1, y - 1 if direction == "bas" else y + 1 if direction == "haut" else y))
        
        plt.figure(figsize=self.dimension_chart)
        
        # graph le noeud avec le label correspondant
        nx.draw_networkx_nodes(G, pos=positions, node_size=2500, node_color='lightblue')
        nx.draw_networkx_labels(G, pos=positions, labels=labels, font_size=10)
        
        # extraction des labels des lignes
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edges(G, pos=positions, arrows=True, arrowstyle='-|>', arrowsize=20)
        nx.draw_networkx_edge_labels(G, pos=positions, edge_labels=edge_labels, font_color='red', font_size=8, label_pos=0.3)

        # Ajout d'un titre au graphique
        plt.title("Arbre Trinomial", fontsize=16)

        # Ajout d'une légende
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label='Noeud:',
                markerfacecolor='lightblue', markersize=15),
            Line2D([0], [0], label="Valeur intrinsèque (Haut)", color='w'),
            Line2D([0], [0], label="Prix Sous-Jacent (Centre)", color='w'),
            Line2D([0], [0], label="Probabilité cumulée (Bas)", color='w'),
            Line2D([0], [0], color='red', lw=2, label='Probabilité de passage')
        ]

        plt.legend(handles=legend_elements, loc='upper left', fontsize=10)
        
        # plt.axis('off')  # On cache les axes
        plt.tight_layout()
        plt.show()