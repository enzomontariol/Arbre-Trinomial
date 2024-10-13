# note: faire les commentaires et renommer variable
# mettre arg facultative dans main pour alpha et base
# modifié les inputs des fonctions ?

import streamlit as st
import datetime as dt
from datetime import datetime, date, timedelta
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import time

# import résultat du VBA
from mainVBA import VBAprice, VBAdata
cheminVBA = r'C:\Users\lince\Downloads\Trinomial_VBA_FINAL_VERSION.xlsm'

# import des fonctions Black Scholes
from Classes.module_black_scholes import BS_Pricer, BS_Delta, BS_Gamma, BS_Vega, BS_Theta, BS_Rho

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

# Création de 6 onglets
memo, tab1, tab2, tab3, tab4, tab5, tab6, tab7= st.tabs(["Memo","Caractéristiques", "Plus d'options", "Graphique", "Comparaison avec Black-Scholes","Comparaison Python-VBA","📈 Chart","Greeks"])

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

OptionPricePython, TimePricePython = main(*Main_Argument)

###########################################################################
################## Onglet 3 : Arbre Trinomial Display #####################
###########################################################################  

with tab3 : 
    st.subheader("Arbre Trinomiale")

# Tracer l'arbre binomial avec les prix sur l'axe des ordonnées et les étapes sur l'axe des abscisses


###########################################################################
################## Onglet 4 : Black-Scholes Comparaison ###################
###########################################################################  

BS_Argument = (st.session_state["Optiontype"], st.session_state["Exercicetype"],
                     st.session_state["StockPrice"], st.session_state["Strike"],
                     st.session_state["TauxInteret"], st.session_state["Maturite"], 
                     st.session_state["PricingDate"],
                     st.session_state["Volatilite"])
BSPriceValue, BSTimeValue = BS_Pricer(*BS_Argument)

Main_Argument = (st.session_state["StockPrice"], st.session_state["Volatilite"], 
                     st.session_state["TauxInteret"], st.session_state["Strike"],
                     st.session_state["ExDateDividende"], st.session_state["Dividende"],
                     st.session_state["Maturite"], 
                     st.session_state["PricingDate"],
                     st.session_state["Optiontype"], st.session_state["Exercicetype"],
                    st.session_state["AlphaParameter"],st.session_state["YearBase"],
                    st.session_state["Pruning"]) #, NbStep)

StepList = [5] + [x for x in range(10,101,10)] + [x for x in range(120,401,20)] + [x for x in range(450,551,50)]
PythonValues = [main(*Main_Argument,x) for x in StepList]
OptionPricePythonList = [x[0] for x in PythonValues]
TimePricePythonList = [x[1] for x in PythonValues]

dfVBA = VBAdata(cheminVBA)

ResultatGreeksVBA, TrinomialPriceVBA, TrinomialTimeVBA, BSPriceVBA, BSTimeVBA = VBAprice(cheminVBA)

data = {
        'Steps': dfVBA['Steps'].tolist(),
        'Tree Price Python': OptionPricePythonList,
        'Tree Price VBA': dfVBA['Trinomial Tree Price'].tolist(),

        'Tree Time Python': TimePricePythonList,
        'Tree Time VBA': dfVBA['Trinomial Tree Time'].tolist(),

        'Convergence Price BS - Python': [x - BSPriceValue for x in OptionPricePythonList],
        'Convergence Price BS - VBA': dfVBA['Convergence avec Black-Scholes'].tolist(),

        'Convergence Time BS - Python': [x - BSTimeValue for x in TimePricePythonList],
        'Convergence Time BS - VBA': dfVBA['Time Gap avec Black-Scholes'].tolist(),
    }

df = pd.DataFrame(data)
df.set_index('Steps', inplace=True)

with tab4:
    st.write("Avec la formule de Black-Scholes en python, le prix de l'option est ", BSPriceValue,
             " et est calculé en ", BSTimeValue, ' seconds.')
    st.write("Avec la formule de Black-Scholes en VBA, le prix de l'option est ", BSPriceVBA,
             " et est calculé en ", BSTimeVBA, ' seconds.')
    
    st.dataframe(df)
    
###########################################################################
#################### Onglet 5 : Python-VBA Comparaison ####################
###########################################################################  

data = {
        'Steps': dfVBA['Steps'].tolist(),
        'Trinomial Tree Price Python': OptionPricePythonList,
        'Trinomial Tree Price VBA': dfVBA['Trinomial Tree Price'].tolist(),

        'Trinomial Tree Time Python': TimePricePythonList,
        'Trinomial Tree Time VBA': dfVBA['Trinomial Tree Time'].tolist(),

        'Convergence Price Python - VBA': [a - b for a, b in zip(OptionPricePythonList, dfVBA['Trinomial Tree Price'].tolist())] ,
        'Convergence Time Python - VBA': [a - b for a, b in zip(TimePricePythonList, dfVBA['Trinomial Tree Time'].tolist())],
    }

df = pd.DataFrame(data)
df.set_index('Steps', inplace=True)

with tab5:
    st.write("L'arbre Trinomial en python, le prix de l'option est ", OptionPricePython,
             " et est calculé en ", TimePricePython, ' seconds.')
    st.write("L'arbre Trinomial en VBA, le prix de l'option est ", TrinomialPriceVBA,
             " et est calculé en ", TrinomialTimeVBA, ' seconds.')

    st.dataframe(df)


###########################################################################
#################### Onglet 6 : Graphique Performance #####################
###########################################################################  

with tab6:
    # Exemple de données
    data = {
        'Steps': dfVBA['Steps'].tolist(),
        'Trinomial Tree Price Python': [np.nan for x in range(len(dfVBA))],
        'Trinomial Tree Price VBA': dfVBA['Trinomial Tree Price'].tolist(),

        'Trinomial Tree Time Python': [np.nan for x in range(len(dfVBA))],
        'Trinomial Tree Time VBA': dfVBA['Trinomial Tree Time'].tolist(),

        'Convergence Price Python - VBA': [np.nan for x in range(len(dfVBA))],
        'Convergence Time Python - VBA': [np.nan for x in range(len(dfVBA))],
    }

    df = pd.DataFrame(data).set_index('Steps')

    # Sélection des courbes à afficher
    selected_curves = st.multiselect("Choisissez les courbes :", options=df.columns, default=df.columns.tolist())

    # Affichage du graphique
    if selected_curves:  # Vérifie si des courbes sont sélectionnées
        st.line_chart(df[selected_curves])
    else:
        st.write("Aucune courbe sélectionnée.")


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

data = {
    'Greeks': ['Delta', 'Gamma', 'Vega','Theta','Rho'],
    'Black-Scholes Python': [BS_Delta_cal, BS_Gamma_cal, BS_Vega_cal,BS_Theta_cal,BS_Rho_cal],
    'Black-Scholes VBA': ResultatGreeksVBA,
    'Variation Empirique Python': [np.nan for x in range(5)],
    'Variation Empirique VBA': [np.nan for x in range(5)],
}

df = pd.DataFrame(data)
df.set_index('Greeks', inplace=True)

with tab7:
    st.dataframe(df)


if st.button("Lancer le Code"):
    now = dt.datetime.now()
    result = OptionPricePython
    st.write(f"Résultat au bout de : {dt.datetime.now() - now}")
    st.write (f"Le prix de l'option est : {result}")
    
    st.write(st.session_state)
    
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
