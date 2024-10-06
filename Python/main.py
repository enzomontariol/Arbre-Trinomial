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
          
if __name__ == '__main__' : 
    now = dt.datetime.now()
    result = main()  
    print(f"Résultat au bout de : {dt.datetime.now() - now}")
    print (f"Le prix de l'option est : {result}")