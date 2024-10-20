# note: faire les commentaires et renommer variable
# mettre arg facultative dans main pour alpha et base
# modifié les inputs des fonctions ?

import streamlit as st
import datetime as dt
from datetime import datetime, date, timedelta
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
import time
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# import résultat du VBA
from mainVBA import VBAprice, VBAdata, VBAEmpiriqueGreeks
cheminVBA = r'C:\Users\lince\Downloads\Trinomial_VBA_FINAL_VERSION.xlsm'

# import des fonctions Black Scholes
from Classes.module_black_scholes import BS_Pricer, BS_Delta, BS_Gamma, BS_Vega, BS_Theta, BS_Rho

from Classes.module_grecques_empiriques import GrecquesEmpiriques
# import fonction principale
from main import main

st.set_page_config(layout="wide")

st.markdown("""
    <style>
    /* Changer la couleur de fond de la page */
    .stApp {
        background-color: #215C98;
    }

    /* Changer la couleur des titres */
    .stApp h1, h2, h3 {
        color: #FFFFFF; 
    }

    /* Changer la couleur des textes */
    .stApp p {
        color: #FFFFFF; /* Gris foncé */
    }

    /* Personnalisation des boutons */
    button {
        background-color: #DAE9F8; /* Vert */
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
    }

    button:hover {
        background-color: #DAE9F8;
    }

    </style>
    """, unsafe_allow_html=True)


# Titre de l'application
st.title("Trinomial Tree")

# Bloque le run du script entier à chaque intéraction de l'utilisateur
if 'run_code' not in st.session_state:
    st.session_state.run_code = False

if 'run_analyse' not in st.session_state:
    st.session_state.run_analyse = False

if 'run_greeks' not in st.session_state:
    st.session_state.run_greeks = False

# Création de 6 onglets
#memo, tab1, tab2, tab3, tab4, tab5, tab6, tab7= st.tabs(["Memo","Caractéristiques", "Plus d'options", "Graphique", "Comparaison avec Black-Scholes","Comparaison Python-VBA","📈 Chart","Greeks"])

memo, tab1, tab2, tab3, tab4, tab5, tab7= st.tabs(["Memo","Caractéristiques", "Plus d'options", "Graphique", "Comparaison avec Black-Scholes","Comparaison Python-VBA","Greeks"])

###########################################################################
################################ Mémo 1 ###################################
########################################################################### 

with memo:
    st.subheader("Mémo")
    st.write("expliquer si on a fait des trucs different en python et vba (pour la construction),  expliquer les resultats differents et en terme de temps")
    
    st.write("Section 1")
    st.divider()
    st.write("Section 2")
    st.markdown("""
    - **Facile à utiliser** : Aucun besoin de HTML, CSS ou JavaScript.
    - **Interactive** : Parfait pour la visualisation de données et les applications de Machine Learning.
    """)
    st.info("Essayez d'ajouter vos propres widgets et contenu interactif.")

###########################################################################
###################### Onglet 1 : Inputs Utilisateur ######################
########################################################################### 


with tab1 :
    st.subheader("Caractéristique du marché, de l'option et du modèle")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.number_input("Entrez le prix de départ du sous-jacent (en €):", format="%.2f", key ="StockPrice",value=100.0)
        st.number_input("Entrez le niveau de volatilité (en %):", format="%.2f", key ="Volatilite",value=0.02)
        st.number_input("Entrez le niveau de taux d'intérêt (en %):", format="%.2f", key ="TauxInteret",value=0.02)
        st.number_input("Entrez le montant de dividende (en €):", format="%.2f", key ="Dividende",value=0.0)
        st.date_input("Entrez la date de dividende :", key ="ExDateDividende")
    
    with col2:
        st.date_input("Entrez une date de maturité :", key ="Maturite",value=datetime.today()+ timedelta(days=10))
        Optionstype = ['Call','Put']
        st.selectbox("Choisissez le type de l'option :", Optionstype, key ="Optiontype")
        Options = ['Européen','Americain']
        st.selectbox("Choisissez le type de l'exercice :", Options, key ="Exercicetype")
        st.number_input("Entrez le prix d'exercice de l'option (en €):", format="%.2f", key ="Strike",value=100.0)
    
    with col3:
        st.date_input("Entrez une date de pricing :", key ="PricingDate")
        st.number_input("Entrez le nombre de pas de l'arbre :",  min_value=1, value=10, step=1, key ="NbStep")

    if st.button("Lancer le pricing", key = "run1"):
        st.session_state.run_code = True  

###########################################################################
############# Onglet 2 : Inputs additionnels Utilisateur ##################
###########################################################################  
      
with tab2 : 
    st.subheader("Plus de paramètre modulable")
    col1, col2, col3 = st.columns(3) 

    with col1:
        # on garde le format float, pour garder la possibilité de mettre 365.25
        st.number_input("Entrez le paramètre alpha :", format="%.0f", key ="AlphaParameter",value=3.0)
        st.number_input("Entrez la base annuelle (en nombre de jours):", format="%.0f", key ="YearBase",value=365.0)

    with col2:
        Options = ['Oui','Non']
        st.selectbox("Elagage de l'arbre :", Options, key ="Pruning")
    
    if st.button("Lancer le pricing", key = "run2"):
        st.session_state.run_code = True  

###########################################################################
################## Prix option via Arbre Trinomial ########################
########################################################################### 

Main_Argument = (st.session_state["StockPrice"], st.session_state["Volatilite"], 
                     st.session_state["TauxInteret"], st.session_state["Strike"],
                     st.session_state["ExDateDividende"], st.session_state["Dividende"],
                     st.session_state["Maturite"],
                     st.session_state["PricingDate"],
                     st.session_state["Optiontype"], st.session_state["Exercicetype"],
                    st.session_state["AlphaParameter"],st.session_state["YearBase"],
                    st.session_state["Pruning"],st.session_state["NbStep"])

# price si l'utilisateur à cliquer sur le bouton
if st.session_state.run_code:
    now = dt.datetime.now()
    Arbre, OptionPricePython, TimePricePython = main(*Main_Argument)
    # GreeksResult = GrecquesEmpiriques(Arbre)
    # GreeksResultList = [GreeksResult.approxime_delta(),GreeksResult.approxime_gamma(),GreeksResult.approxime_vega(),
    #                     GreeksResult.approxime_theta(),GreeksResult.approxime_rho()]
    result = OptionPricePython
    st.write(f"Résultat au bout de : {dt.datetime.now() - now}")
    st.write (f"Le prix de l'option est : {result}")
    st.write(st.session_state)
    st.session_state.run_code = False
    st.session_state.run_analyse = False
else:
    OptionPricePython, TimePricePython = np.nan, np.nan


###########################################################################
################## Onglet 3 : Arbre Trinomial Display #####################
###########################################################################  

with tab3 : 
    st.subheader("Arbre Trinomiale")
    #Arbre.visualize_tree()
    # Tracer l'arbre binomial avec les prix sur l'axe des ordonnées et les étapes sur l'axe des abscisses


###########################################################################
################## Onglet 4 : Black-Scholes Comparaison ###################
###########################################################################  

BS_Argument = (st.session_state["Optiontype"], st.session_state["Exercicetype"],
                     st.session_state["StockPrice"], st.session_state["Strike"],
                     st.session_state["TauxInteret"], st.session_state["Maturite"], 
                     st.session_state["PricingDate"],
                     st.session_state["Volatilite"])
BSPriceValue, BSTimeValue = BS_Pricer(*BS_Argument) #### pb: prix faux

# prend les mêmes arguments que l'analyse en VBA
Main_Argument_Analysis = (100, 0.02, 0.02, 101,
                     st.session_state["ExDateDividende"], st.session_state["Dividende"],
                     date(2024,10,23), date(2024,1,13),
                     'Call', 'Européen', 3, 365,'Oui')

StepList = [5] + [x for x in range(10,101,10)] + [x for x in range(120,401,20)] + [x for x in range(450,551,50)]
PythonValues = [main(*Main_Argument_Analysis,x) for x in StepList]
 
# lance l'analyse que si l'utilisateur clique sur le bouton
# if st.session_state.run_analyse:
#     PythonValues = [main(*Main_Argument_Analysis,x) for x in StepList]
#     st.session_state.run_analyse = False
# else: 
#     PythonValues = [[np.nan,np.nan,np.nan] for x in StepList]

# Analyse en Python
OptionPricePythonList = [x[1] for x in PythonValues]
TimePricePythonList = [x[2] for x in PythonValues] #### pb: à diviser par 100?

# Récupération des valeurs du fichier excel
BSTab, StepTab, StrikeTab = VBAdata(cheminVBA)
ResultatGreeksVBA, TrinomialPriceVBA, TrinomialTimeVBA, BSPriceVBA, BSTimeVBA = VBAprice(cheminVBA)

data = {
        'Steps': StepTab['Steps'].tolist(),
        'Tree Price Python': OptionPricePythonList,
        'Tree Price VBA': StepTab['Trinomial Tree Price'].tolist(),

        # graph
        'Convergence Price BS - Python': [(OptionPricePythonList[i] - BSPriceValue)*StepList[i] for i in range(len(OptionPricePythonList))],
        'Convergence Price BS - VBA': StepTab['Convergence avec Black-Scholes'].tolist(),
    }

df = pd.DataFrame(data)
df.set_index('Steps', inplace=True)

with tab4:
    st.write("Avec la formule de Black-Scholes en python, le prix de l'option est ", BSPriceValue,
             " et est calculé en ", BSTimeValue, ' seconds.')
    st.write("Avec la formule de Black-Scholes en VBA, le prix de l'option est ", BSPriceVBA,
             " et est calculé en ", BSTimeVBA, ' seconds.')
    
    col1, col2 = st.columns(2) 

    with col1:
        st.dataframe(df)

    with col2:
        # Création du graphique avec deux axes y
        fig = go.Figure()
        # Tracer la première colonne (Colonne_1) sur le premier axe y
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Convergence Price BS - VBA'],
            name='Convergence Price BS - VBA',
            mode='lines',
            line=dict(color='blue')
        ))

        # Tracer la deuxième colonne (Colonne_2) sur le second axe y
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Convergence Price BS - Python'],
            name='Convergence Price BS - Python',
            mode='lines',
            line=dict(color='red'),
            yaxis='y2'
        ))

        # Mise en forme des axes
        fig.update_layout(
            title={
                'text': 'Graphique avec deux axes y',
                'x': 0.5,  # Position horizontale du titre (0.5 = centré)
                'xanchor': 'center'  # Ancrer le texte au centre
            },
            xaxis_title='Indice du DataFrame',
            yaxis_title='Colonne 1',
            
            # Configuration du second axe y
            yaxis2=dict(
                title='Colonne 2',
                overlaying='y',  # Superposer les deux axes
                side='right'  # Deuxième axe à droite
            ),

            # Positionner la légende en dessous
            legend=dict(
                orientation="h",  # Légende horizontale
                yanchor="top", 
                y=-0.2,
                xanchor="center",
                x=0.5
                ),
            
            # Ajuster la taille du graphique
            width=610,  # Largeur en pixels
            height=400  # Hauteur en pixels
        )

        # Affichage du graphique dans Streamlit
        st.plotly_chart(fig)

    if st.button("Lancer l'analyse"):
        st.session_state.run_analyse = True  # Met à jour l'état quand on clique sur le bouton

    
###########################################################################
#################### Onglet 5 : Python-VBA Comparaison ####################
###########################################################################  

data = {
        'Steps': StepTab['Steps'].tolist(),
        'Trinomial Tree Time Python': TimePricePythonList,
        'Trinomial Tree Time VBA': StepTab['Trinomial Tree Time'].tolist(),
        'Convergence Time Python - VBA': [a - b for a, b in zip(TimePricePythonList, StepTab['Trinomial Tree Time'].tolist())],
    }

df = pd.DataFrame(data).set_index('Steps')

with tab5:
    st.write("L'arbre Trinomial en python, le prix de l'option est ", OptionPricePython,
             " et est calculé en ", TimePricePython, ' seconds.')
    st.write("L'arbre Trinomial en VBA, le prix de l'option est ", TrinomialPriceVBA,
             " et est calculé en ", TrinomialTimeVBA, ' seconds.')

    col1, col2 = st.columns(2) 

    with col1:
        st.dataframe(df, width=800)

    with col2:
        # Création du graphique avec deux axes y
        fig = go.Figure()

        # Tracer la première colonne (Colonne_1) sur le premier axe y
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Trinomial Tree Time Python'],
            name='Trinomial Tree Time Python',
            mode='lines',
            line=dict(color='blue')
        ))

        # Tracer la deuxième colonne (Colonne_2) sur le second axe y
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Trinomial Tree Time VBA'],
            name='Trinomial Tree Time VBA',
            mode='lines',
            line=dict(color='red'),
        ))

        # Mise en forme des axes
        fig.update_layout(
            title={
                'text': 'Graphique avec deux axes y',
                'x': 0.5,  # Position horizontale du titre (0.5 = centré)
                'xanchor': 'center'  # Ancrer le texte au centre
            },
            xaxis_title='Indice du DataFrame',
            yaxis_title='Colonne 1',
            
            # Configuration du second axe y
            yaxis2=dict(
                title='Colonne 2',
                overlaying='y',  # Superposer les deux axes
                side='right'  # Deuxième axe à droite
            ),

            # Positionner la légende en dessous
            legend=dict(
                orientation="h",  # Légende horizontale
                yanchor="top", 
                y=-0.2,
                xanchor="center",
                x=0.5
                ),
            
            # Ajuster la taille du graphique
            width=610,  # Largeur en pixels
            height=400  # Hauteur en pixels
        )

        # Affichage du graphique dans Streamlit
        st.plotly_chart(fig)
    
    if st.button("Lancer la comparaison"):
        st.session_state.run_vba_python = True 



###########################################################################
########################### Onglet 7 : Grecques ###########################
########################################################################### 

Greeks_Argument = (st.session_state["Optiontype"], st.session_state["Exercicetype"],
                     st.session_state["StockPrice"], st.session_state["Strike"],
                     st.session_state["TauxInteret"], st.session_state["Maturite"], st.session_state["PricingDate"],
                     st.session_state["Volatilite"], st.session_state["YearBase"])

BS_Delta_cal = BS_Delta(*Greeks_Argument)
BS_Gamma_cal = BS_Gamma(*Greeks_Argument)
BS_Vega_cal = BS_Vega(*Greeks_Argument)
BS_Theta_cal = BS_Theta(*Greeks_Argument)
BS_Rho_cal = BS_Rho(*Greeks_Argument)

GreeksEmpiriqueVBA = VBAEmpiriqueGreeks(cheminVBA)

# if not st.session_state.run_code:
GreeksResultList = [np.nan for x in range(5)]
#     st.session_state.run_code = True


data = {
    'Greeks': ['Delta', 'Gamma', 'Vega','Theta','Rho'],
    'Black-Scholes Python': [BS_Delta_cal, BS_Gamma_cal, BS_Vega_cal,BS_Theta_cal,BS_Rho_cal],
    'Black-Scholes VBA': ResultatGreeksVBA,
    'Variation Empirique Python': GreeksResultList,
    'Variation Empirique VBA': GreeksEmpiriqueVBA,
}

df = pd.DataFrame(data)
df.set_index('Greeks', inplace=True)

with tab7:
    st.dataframe(df)

    if st.button("Actualiser le tableau"):
        st.session_state.run_greeks = True  
    
#######################################################################
#######################################################################
#######################################################################
#######################################################################

exit()
"""MainVBAArgument = (StockPrice = st.session_state["StockPrice"],
                Volatilite = st.session_state["Volatilite"],
                TauxInteret = st.session_state["TauxInteret"], 
                Strike = st.session_state["Strike"],
                ExDateDividende = st.session_state["ExDateDividende"], 
                Dividende = st.session_state["Dividende"], 
                Maturite = st.session_state["Maturite"], 
                NbStep = st.session_state["NbStep"],
                PricingDate = st.session_state["PricingDate"], 
                Optiontype = st.session_state["Optiontype"], 
                Exercicetype = st.session_state["Exercicetype"], 
                Alpha = st.session_state["AlphaParameter"], 
                BaseYear = st.session_state["YearBase"],
                Elagage = st.session_state["Pruning"])"""


###########################################################################
#################### Onglet 6 : Graphique Performance #####################
###########################################################################  

with tab6:
    # Exemple de données
    data = {
        'Steps': StepTab['Steps'].tolist(),
        'Trinomial Tree Price Python': [np.nan for x in range(len(StepTab))],
        'Trinomial Tree Price VBA': StepTab['Trinomial Tree Price'].tolist(),

        'Trinomial Tree Time Python': [np.nan for x in range(len(StepTab))],
        'Trinomial Tree Time VBA': StepTab['Trinomial Tree Time'].tolist(),

        'Convergence Price Python - VBA': [np.nan for x in range(len(StepTab))],
        'Convergence Time Python - VBA': [np.nan for x in range(len(StepTab))],
    }

    df = pd.DataFrame(data).set_index('Steps')

    # Sélection des courbes à afficher
    selected_curves = st.multiselect("Choisissez les courbes :", options=df.columns, default=df.columns.tolist())

    # Affichage du graphique
    if selected_curves:  # Vérifie si des courbes sont sélectionnées
        st.line_chart(df[selected_curves])
    else:
        st.write("Aucune courbe sélectionnée.")

