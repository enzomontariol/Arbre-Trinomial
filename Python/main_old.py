#%% Imports

import datetime as dt

from Classes.module_marche import DonneeMarche
from Classes.module_option import Option
from Python.Classes.module_arbre_noeud import Arbre
from Classes.module_enums import MethodeConstructionArbre


def main(methode_construction : MethodeConstructionArbre = MethodeConstructionArbre.vanille) -> float : 
    today = dt.date.today()
    today_1y = dt.date(today.year+1, today.month, today.day)

    spot = 100 #st.session_state["StockPrice"]
    vol = 0.2 #st.session_state["Volatilite"]
    discount_rate = risk_free = 0.04 #st.session_state["TauxInteret"]
    dividende_ex_date = dt.date(today.year+1, today.month-6, today.day) #st.session_state["ExDateDividende"]
    dividende_montant = 4 #st.session_state["Dividende"]

    strike = 100 #st.session_state["Strike"]
    expiry = today_1y #st.session_state["Maturite"]

    nb_pas = 400 #st.session_state["NbStep"]

    #pricing_date = st.session_state["PricingDate"]
    #type_option = st.session_state["Optiontype"]
    #type_exercise = st.session_state["Exercicetype"]


    donnée = DonneeMarche(today, spot, vol, discount_rate, risk_free, dividende_ex_date=dividende_ex_date, dividende_montant=dividende_montant)
    option = Option(maturite = expiry, prix_exercice = strike, call = True, date_pricing = today)

    arbre = Arbre(nb_pas, donnée, option)
    
    arbre.pricer_arbre()  

    return arbre.prix_option
          
##################################################################
##################################################################
##################################################################
### mettre des valeurs par défaut pour alpha et base
# Active le mode large

import streamlit as st

from datetime import datetime, date, timedelta
import numpy as np 
import pandas as pd

import sys
import os

# import résultat du VBA
from mainVBA import greekstab, VBAtabAnalysis
chemin = r'C:\Users\lince\Downloads\Trinomial_VBA_FINAL_VERSION.xlsm'

# Ajouter le chemin absolu du dossier contenant fichier.py
chemin_fichier = os.path.abspath("Classes")
sys.path.append(chemin_fichier)
# Importer une fonction depuis fichier.py
from module_black_scholes import BS_Pricer, BS_Delta, BS_Gamma, BS_Vega, BS_Theta, BS_Rho

#from main import main
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

tab1, tab2, tab3, tab4, tab5, tab6= st.tabs(["Caractéristiques", "Plus d'options", "Comparaison avec Black-Scholes","Comparaison Python-VBA","📈 Chart","Greeks"])

# Utilisation des colonnes pour contrôler l'espacement et la "largeur"
#col1, col2, col3 = st.columns([1, 1, 1])  # Ajuste les valeurs pour contrôler la largeur relative


with tab1 :
    st.subheader("Caractéristique du marché, de l'option et du modèle")
    col1, col2, col3 = st.columns(3)  # Ajuste les valeurs pour contrôler la largeur relative

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
        st.number_input("Entrez le nombre de pas de l'arbre :", format="%.0f", key ="NbStep")
        
with tab2 : 

    st.subheader("Plus de paramètre modulable")
    col1, col2, col3 = st.columns(3)  # Ajuste les valeurs pour contrôler la largeur relative

    with col1:
        # on garde le format float, pour garder la possibilité de mettre 365.25
        st.number_input("Entrez le paramètre alpha :", format="%.0f", key ="AlphaParameter",value=3.0)
        st.number_input("Entrez la base annuelle (en nombre de jours):", format="%.0f", key ="YearBase",value=365.0)

    with col2:
        Options = ['Oui','Non']
        st.selectbox("Elagage de l'arbre :", Options, key ="Pruning")

BS_Argument = (st.session_state["Optiontype"], st.session_state["Exercicetype"],
                     st.session_state["StockPrice"], st.session_state["Strike"],
                     st.session_state["TauxInteret"], (st.session_state["Maturite"] - st.session_state["PricingDate"]).days,
                     st.session_state["Volatilite"])

BSPriceValue = BS_Pricer(*BS_Argument)


dfVBA = VBAtabAnalysis(chemin)

with tab3:

    # Exemple de DataFrame
    # recup les données d'excel
    result = 10
    # mettre valeur bs en phrase?
    st.write("Selon la formule de Black-Scholes en python, le prix de l'option est ", BSPriceValue," .")
    st.write("Selon la formule de Black-Scholes en VBA, le prix de l'option est ", result," .")

    data = {
        'Steps': dfVBA['Steps'].tolist(),
        'Tree Price Python': [x for x in range(len(dfVBA))],
        'Tree Price VBA': dfVBA['Trinomial Tree Price'].tolist(),

        'Tree Time Python': [x for x in range(len(dfVBA))],
        'Tree Time VBA': dfVBA['Trinomial Tree Time'].tolist(),

        'Convergence Price BS - Python': [x for x in range(len(dfVBA))],
        'Convergence Price BS - VBA': dfVBA['Convergence avec Black-Scholes'].tolist(),

        'Convergence Time BS - Python': [x for x in range(len(dfVBA))],
        'Convergence Time BS - VBA': dfVBA['Time Gap avec Black-Scholes'].tolist(),
    }

    df = pd.DataFrame(data)
    df.set_index('Steps', inplace=True)
    st.dataframe(df)


with tab4:

    # Exemple de DataFrame
    # recup les données d'excel
    result = 10
    # mettre valeur bs en phrase?
    st.write("Selon la formule de Black-Scholes en python, le prix de l'option est ", result," .")
    st.write("Selon la formule de Black-Scholes en VBA, le prix de l'option est ", result," .")
    
    data = {
        'Steps': dfVBA['Steps'].tolist(),
        'Trinomial Tree Price Python': [x for x in range(len(dfVBA))],
        'Trinomial Tree Price VBA': dfVBA['Trinomial Tree Price'].tolist(),

        'Trinomial Tree Time Python': [x for x in range(len(dfVBA))],
        'Trinomial Tree Time VBA': dfVBA['Trinomial Tree Time'].tolist(),

        'Convergence Price Python - VBA': [x for x in range(len(dfVBA))],
        'Convergence Time Python - VBA': [x for x in range(len(dfVBA))],
    }

    df = pd.DataFrame(data)
    df.set_index('Steps', inplace=True)
    st.dataframe(df)

data = np.random.randn(10, 1)

with tab5:
    # Exemple de données
    data = {
        'Steps': dfVBA['Steps'].tolist(),
        'Trinomial Tree Price Python': [x for x in range(len(dfVBA))],
        'Trinomial Tree Price VBA': dfVBA['Trinomial Tree Price'].tolist(),

        'Trinomial Tree Time Python': [x for x in range(len(dfVBA))],
        'Trinomial Tree Time VBA': dfVBA['Trinomial Tree Time'].tolist(),

        'Convergence Price Python - VBA': [x for x in range(len(dfVBA))],
        'Convergence Time Python - VBA': [x for x in range(len(dfVBA))],
    }

    df = pd.DataFrame(data)

    # Définir la colonne 'Date' comme index
    df.set_index('Steps', inplace=True)

    # Affichage du graphique
    st.subheader("A tab with a chart")
    st.line_chart(df)

    # Création du DataFrame
    df = pd.DataFrame(data).set_index('Steps')

    # Sélection des courbes à afficher
    selected_curves = st.multiselect("Choisissez les courbes :", options=df.columns, default=df.columns.tolist())

    # Affichage du graphique
    if selected_curves:  # Vérifie si des courbes sont sélectionnées
        st.line_chart(df[selected_curves])
    else:
        st.write("Aucune courbe sélectionnée.")

    # Création du DataFrame
    df = pd.DataFrame(data).set_index('Steps')

    # Affichage des cases à cocher pour chaque courbe
    st.subheader("Sélectionnez les courbes à afficher")

    col1, col2, col3 = st.columns(3)  # Ajuste les valeurs pour contrôler la largeur relative

    with col1:
        k = int(len(df.columns))
        selected_curves = [curve for curve in df.columns[:-2] if st.checkbox(f"Afficher {curve}", value=True, key=f"Courbe_{curve}")]
    with col2:
        selected_curves = selected_curves + [curve for curve in df.columns[-2:] if st.checkbox(f"Afficher {curve}", value=True, key=f"Courbe_{curve}")]
    #with col3:
        #selected_curves = selected_curves + [curve for curve in df.columns[2*k/3:] if st.checkbox(f"Afficher {curve}", value=True, key=f"Courbe_{curve}")]

    #selected_curves = [curve for curve in df.columns[:-2] if st.checkbox(f"Afficher {curve}", value=True)]

    # Affichage du graphique
    st.subheader("Graphique des courbes sélectionnées")
    if selected_curves:  # Vérifie si des courbes sont sélectionnées
        st.line_chart(df[selected_curves])
    else:
        st.write("Aucune courbe sélectionnée.")





Greeks_Argument = (st.session_state["Optiontype"], st.session_state["Exercicetype"],
                     st.session_state["StockPrice"], st.session_state["Strike"],
                     st.session_state["TauxInteret"], (st.session_state["Maturite"] - st.session_state["PricingDate"]).days,
                     st.session_state["Volatilite"], st.session_state["YearBase"])

BS_Delta_cal = BS_Delta(*Greeks_Argument)
BS_Gamma_cal = BS_Gamma(*Greeks_Argument)
BS_Vega_cal = BS_Vega(*Greeks_Argument)
BS_Theta_cal = BS_Theta(*Greeks_Argument)
BS_Rho_cal = BS_Rho(*Greeks_Argument)

with tab6:

    # Exemple de DataFrame
    # recup les données d'excel
    data = {
        'Greeks': ['Delta', 'Gamma', 'Vega','Theta','Rho'],
        'Black-Scholes Python': [BS_Delta_cal, BS_Gamma_cal, BS_Vega_cal,BS_Theta_cal,BS_Rho_cal],
        'Black-Scholes VBA': greekstab(Greeks_Argument,chemin),
        'Variation Empirique Python': ['Paris', 'Lyon', 'Marseille','a','b'],
        'Variation Empirique VBA': ['Paris', 'Lyon', 'Marseille','a','b'],
    }

    df = pd.DataFrame(data)
    df.set_index('Greeks', inplace=True)
    st.dataframe(df)


if st.button("Lancer le Code"):
    now = dt.datetime.now()
    result = main()  
    print(f"Résultat au bout de : {dt.datetime.now() - now}")
    print (f"Le prix de l'option est : {result}")
    st.write("code lanceeeeeeeeeer", result, st.session_state["ExDateDividende"], type(st.session_state["ExDateDividende"]))
    st.write(st.session_state)
    print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    
#######################################################################
#######################################################################
#######################################################################
#######################################################################
exit()       
if __name__ == '__main__' : 
    now = dt.datetime.now()
    result = main()  
    print(f"Résultat au bout de : {dt.datetime.now() - now}")
    print (f"Le prix de l'option est : {result}")

""" inutile mais on sait jamais
Optiontype = st.session_state["Optiontype"]
Exercicetype = st.session_state["Exercicetype"]
StockPrice = st.session_state["StockPrice"]
Strike = st.session_state["Strike"]
TauxInteret = st.session_state["TauxInteret"]
Maturite = st.session_state["Maturite"]
PricingDate = st.session_state["PricingDate"]
Volatilite = st.session_state["Volatilite"]
YearBase = st.session_state["YearBase"]

Greeks_Argument = (Optiontype, Exercicetype,
                     StockPrice, Strike,
                     TauxInteret, (Maturite - PricingDate).days,
                     Volatilite, YearBase)
"""
