#%% Imports

import datetime as dt
from datetime import date
import matplotlib.pyplot as plt
import numpy as np
from Classes.module_marche import DonneeMarche
from Classes.module_option import Option
from Classes.module_arbre import Arbre
from Classes.module_enums import MethodeConstructionArbre


"""def main(StockPrice: float, Volatilite: float, TauxInteret: float, Strike: float,
         ExDateDividende: date, Dividende: float, Maturite: date, NbStep: float, 
         PricingDate: date, Optiontype: str, Exercicetype: str,
         methode_construction : MethodeConstructionArbre = MethodeConstructionArbre.vanille) -> float : 
"""
def main(methode_construction : MethodeConstructionArbre = MethodeConstructionArbre.vanille) -> float : 
    today = dt.date.today()
    today_1y = dt.date(today.year+1, today.month, today.day)

    spot = 100 #StockPrice
    vol = 0.2 #Volatilite
    discount_rate = risk_free = 0.04 #TauxInteret
    dividende_ex_date = dt.date(today.year+1, today.month-6, today.day) #ExDateDividende
    dividende_montant = 4 #Dividende

    strike = 100 #Strike
    expiry = today_1y #Maturite

    nb_pas = 400 #NbStep

    #pricing_date = PricingDate
    #type_option = Optiontype
    #type_exercise = Exercicetype

    donnée = DonneeMarche(today, spot, vol, discount_rate, risk_free, dividende_ex_date=dividende_ex_date, dividende_montant=dividende_montant)
    option = Option(maturite = expiry, prix_exercice = strike, call = True, date_pricing = today)

    arbre = Arbre(nb_pas, donnée, option)
    
    arbre.pricer_arbre()  

    print("Ok: Arbre")
    return arbre.prix_option

# marche pas, faut rentrer l'arbre en argument
def plot_binomial_tree(arbre):
    tree = arbre
    
    fig, ax = plt.subplots(figsize=(8, 6))
    n = arbre.nb_step
    # Tracer les arêtes et les noeuds
    for i in range(n):
        for j in range(i + 1):
            # Tracer les arêtes (montée et descente)
            ax.plot([i, i + 1], [tree[i, j], tree[i + 1, j]], color='blue')
            ax.plot([i, i + 1], [tree[i, j], tree[i + 1, j + 1]], color='blue')
    
    # Tracer les noeuds (prix)
    for i in range(n + 1):
        for j in range(i + 1):
            ax.scatter(i, tree[i, j], color='red')
            ax.text(i, tree[i, j], f"{tree[i, j]:.2f}", fontsize=9, ha='center', va='bottom')
    
    # Ajouter les labels et le titre
    ax.set_xlabel("Steps (t)")
    ax.set_ylabel("Price (S)")
    ax.set_title(f"Binomial Tree of Stock Prices with {n} Steps")
    st.pyplot(fig)

# Tracer l'arbre binomial

OptionPrice = main()
plot_binomial_tree(OptionPrice)

print(main())        
"""    
if __name__ == '__main__' : 
    now = dt.datetime.now()
    result = main()  
    print(f"Résultat au bout de : {dt.datetime.now() - now}")
    print (f"Le prix de l'option est : {result}")

inutile mais on sait jamais
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
