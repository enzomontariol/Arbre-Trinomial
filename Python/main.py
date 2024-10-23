#%% Imports
import time
import datetime as dt
from datetime import date, datetime
import matplotlib.pyplot as plt
import numpy as np
from Classes.module_marche import DonneeMarche
from Classes.module_option import Option
from Python.Classes.module_arbre_noeud import Arbre
from Classes.module_enums import MethodeConstructionArbre


def main(StockPrice: float, Volatilite: float, TauxInteret: float, Strike: float,
         ExDateDividende: date, Dividende: float, Maturite: date,  
         PricingDate: date, 
         Optiontype: str, Exercicetype: str, 
         Alpha: int, BaseYear: float, Elagage: str,
         NbStep: int,
         methode_construction : MethodeConstructionArbre = MethodeConstructionArbre.vanille) -> float : 
    
    spot = StockPrice
    vol = Volatilite
    discount_rate = risk_free = TauxInteret
    dividende_ex_date = ExDateDividende
    dividende_montant = Dividende

    strike = Strike
    maturite = Maturite

    nb_pas = NbStep

    pricing_date = PricingDate
    type_option = Optiontype

    if type_option == 'Call':
        type_option = True
    else:
        type_option = False

    if Exercicetype == 'Americain':
        Exercicetype = True
    else:
        Exercicetype = False

    type_exercise = Exercicetype

    donnée = DonneeMarche(date_debut = pricing_date, prix_spot = spot, 
                          volatilite = vol,
                          taux_interet = risk_free, taux_actualisation = discount_rate,
                          dividende_ex_date=dividende_ex_date, dividende_montant=dividende_montant)
    
    option = Option(maturite = maturite, prix_exercice = strike, 
                    call = type_option, americaine = type_exercise, date_pricing = pricing_date)

    arbre = Arbre(nb_pas, donnée, option)
    
    start_time = time.time()
    arbre.pricer_arbre()  
    execution_time = time.time() - start_time

    print("Ok: Arbre")
    return arbre, arbre.prix_option, execution_time


spot = 100 
vol = 0.21
discount_rate = risk_free = 0.03
dividende_ex_date = date(2024, 6,15) 
dividende_montant = 3

typee = 'Call'

strike = 101 #Strike
expiry = date(2024, 12, 26) 
USEUU = 'Européen'

datestart = date(2024, 3, 1)

a,b,c = main(StockPrice = spot, Volatilite = vol, TauxInteret = risk_free, Strike = strike,
          ExDateDividende = dividende_ex_date, Dividende = dividende_montant, Maturite = expiry, PricingDate = datestart, 
          Optiontype = typee, Exercicetype = USEUU, Alpha = 3, BaseYear= 365, Elagage= 'Oui',NbStep =  300)

print(b,c)
exit()

a,bpos,c = main(StockPrice = spot*(1+0.01), Volatilite = vol, TauxInteret = risk_free, Strike = strike,
          ExDateDividende = dividende_ex_date, Dividende = dividende_montant, Maturite = expiry, PricingDate = datestart, 
          Optiontype = typee, Exercicetype = USEUU, Alpha = 3, BaseYear= 365, Elagage= 'Oui',NbStep =  300)


a,bneg,c = main(StockPrice = spot*(1-0.01), Volatilite = vol, TauxInteret = risk_free, Strike = strike,
          ExDateDividende = dividende_ex_date, Dividende = dividende_montant, Maturite = expiry, PricingDate = datestart, 
          Optiontype = typee, Exercicetype = USEUU, Alpha = 3, BaseYear= 365, Elagage= 'Oui',NbStep =  300)

print(bpos,bneg)


from Classes.module_grecques_empiriques import GrecquesEmpiriques

GreeksResult = GrecquesEmpiriques(a,var_s=0.01)
print(GreeksResult.approxime_delta())
print(GreeksResult.approxime_vega())



# marche pas, faut rentrer l'arbre en argument
def plot_binomial_tree(arbre):
    tree = arbre
    
    fig, ax = plt.subplots(figsize=(8, 6))
    n = 3#arbre.nb_step
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

# %%
