#%% Imports

import datetime as dt

from Classes.module_marche import DonneeMarche
from Classes.module_option import Option
from Classes.module_arbre import Arbre
from Classes.module_enums import MethodeConstructionArbre


def main(methode_construction : MethodeConstructionArbre = MethodeConstructionArbre.vanille) -> float : 
    # today = dt.date.today()
    today = dt.date(2024,1,1)
    today_1y = dt.date(today.year+1, today.month, today.day)

    spot = 132
    vol = 0.23
    discount_rate = risk_free = 0.04

    strike = 200
    expiry = today_1y

    nb_pas = 100

    donnée = DonneeMarche(today, spot, vol, discount_rate, risk_free)
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