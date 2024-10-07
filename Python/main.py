#%% Imports

import datetime as dt

from Classes.module_marche import DonneeMarche
from Classes.module_option import Option
from Classes.module_arbre import Arbre
from Classes.module_enums import MethodeConstructionArbre


def main(methode_construction : MethodeConstructionArbre = MethodeConstructionArbre.vanille) -> float : 
    today = dt.date.today()
    today_1y = dt.date(today.year+1, today.month, today.day)

    spot = 100
    vol = 0.2
    discount_rate = risk_free = 0.04
    dividende_ex_date = dt.date(today.year+1, today.month-6, today.day)
    dividende_montant = 4

    strike = 100
    expiry = today_1y

    nb_pas = 2000

    donnée = DonneeMarche(today, spot, vol, discount_rate, risk_free, dividende_ex_date=dividende_ex_date, dividende_montant=dividende_montant)
    option = Option(maturite = expiry, prix_exercice = strike, call = True, date_pricing = today)

    arbre = Arbre(nb_pas, donnée, option)

    if methode_construction == MethodeConstructionArbre.vanille : 
        arbre.planter_arbre_vanille()
    else :  
        arbre.planter_arbre_speed()
    
    arbre.pricer_arbre()  

    return arbre.prix_option
          
##################################################################
##################################################################
##################################################################
### mettre des valeurs par défaut pour alpha et base
# Active le mode large

import streamlit as st

from datetime import datetime
import numpy as np 

from main import main
#st.set_page_config(layout="wide")

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

tab1, tab2, tab3 = st.tabs(["Caractéristiques", "Plus d'options", "📈 Chart"])
data = np.random.randn(10, 1)

# Utilisation des colonnes pour contrôler l'espacement et la "largeur"
#col1, col2, col3 = st.columns([1, 1, 1])  # Ajuste les valeurs pour contrôler la largeur relative

with tab1 :
    st.subheader("Caractéristique du marché, de l'option et du modèle")
    col1, col2, col3 = st.columns(3)  # Ajuste les valeurs pour contrôler la largeur relative

    with col1:
        StockPrice = st.number_input("Entrez le prix de départ du sous-jacent :", format="%.2f")
        Volatilité = st.number_input("Entrez le niveau de volatilité :", format="%.2f")
        TauxInteret = st.number_input("Entrez le niveau de taux d'intérêt :", format="%.2f")
        Dividende = st.number_input("Entrez le montant de dividende :", format="%.2f")
        ExDateDividende = st.date_input("Entrez la date de dividende :")
    
    with col2:
        Maturité = st.date_input("Entrez une date de maturité :")
        Options = ['Call','Put']
        Optiontype = st.selectbox("Choisissez le type de l'option :", Options)
        Options = ['Européen','Americain']
        Exercicetype = st.selectbox("Choisissez le type de l'exercice :", Options)
        Strike = st.number_input("Entrez le prix d'exercice de l'option :", format="%.2f")
    
    with col3:
        PricingDate = st.date_input("Entrez une date de pricing :")
        NbStep = st.number_input("Entrez le nombre de pas de l'arbre :", format="%.0f")

with tab2 : 

    st.subheader("Plus de paramètre modulable")
    col1, col2, col3 = st.columns(3)  # Ajuste les valeurs pour contrôler la largeur relative

    with col1:
        AlphaParameter = st.number_input("Entrez le paramètre alpha :", format="%.0f")#,placeholder="salu")
        YearBase = st.number_input("Entrez la base annuelle :", format="%.0f")

with tab3:
    st.subheader("A tab with a chart")
    st.line_chart(data)

def test():
    st.write("code lanceeeeeeeeeer", StockPrice)

if st.button("Lancer le Code"):
    result = test()
    st.write(f"Veuillez remplir tous les champs correctement.{result}")


#######################################################################
#######################################################################
#######################################################################
#######################################################################
          
if __name__ == '__main__' : 
    now = dt.datetime.now()
    result = main()  
    print(f"Résultat au bout de : {dt.datetime.now() - now}")
    print (f"Le prix de l'option est : {result}")