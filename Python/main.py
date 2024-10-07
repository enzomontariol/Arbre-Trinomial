#%% Imports

import datetime as dt

from Classes.module_marche import DonneeMarche
from Classes.module_option import Option
from Classes.module_arbre import Arbre
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
        st.number_input("Entrez le prix de départ du sous-jacent :", format="%.2f", key ="StockPrice")
        st.number_input("Entrez le niveau de volatilité :", format="%.2f", key ="Volatilite")
        st.number_input("Entrez le niveau de taux d'intérêt :", format="%.2f", key ="TauxInteret")
        st.number_input("Entrez le montant de dividende :", format="%.2f", key ="Dividende")
        st.date_input("Entrez la date de dividende :", key ="ExDateDividende")
    
    with col2:
        st.date_input("Entrez une date de maturité :", key ="Maturite")
        Optionstype = ['Call','Put']
        st.selectbox("Choisissez le type de l'option :", Optionstype, key ="Optiontype")
        Options = ['Européen','Americain']
        st.selectbox("Choisissez le type de l'exercice :", Options, key ="Exercicetype")
        st.number_input("Entrez le prix d'exercice de l'option :", format="%.2f", key ="Strike")
    
    with col3:
        st.date_input("Entrez une date de pricing :", key ="PricingDate")
        st.number_input("Entrez le nombre de pas de l'arbre :", format="%.0f", key ="NbStep")

with tab2 : 

    st.subheader("Plus de paramètre modulable")
    col1, col2, col3 = st.columns(3)  # Ajuste les valeurs pour contrôler la largeur relative

    with col1:
        st.number_input("Entrez le paramètre alpha :", format="%.0f", key ="AlphaParameter")
        st.number_input("Entrez la base annuelle :", format="%.0f", key ="YearBase")

with tab3:
    st.subheader("A tab with a chart")
    st.line_chart(data)

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