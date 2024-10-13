
import numpy as np
from scipy.stats import norm
from datetime import datetime, date, timedelta
import time

def Verif_input(Optiontype,Exercicetype):
    if Optiontype not in ["Call","Put"] and Exercicetype == "Européen": 
        return "Merci de rentrer Call ou Put"

def BS_Pricer(Optiontype,Exercicetype,StockPrice,Strike,TauxInteret,Maturite,PricingDate,Volatilite):
    start_time = time.time()
    Verif_input(Optiontype,Exercicetype)
    
    d1 = (np.log(StockPrice/Strike) + (TauxInteret + 0.5 * Volatilite**2)*(Maturite-PricingDate).days) / (Volatilite*np.sqrt((Maturite-PricingDate).days))
    d2 = d1 - Volatilite*np.sqrt((Maturite-PricingDate).days)
    Nd1 = norm.cdf(d1, 0, 1)
    Nd2 = norm.cdf(d2, 0, 1)

    if Optiontype == "Call":
        BSPrice = StockPrice*Nd1 - Strike*np.exp(-TauxInteret*(Maturite-PricingDate).days)*Nd2
    else:
        BSPrice = -StockPrice*(1-Nd1) + Strike*np.exp(-TauxInteret*(Maturite-PricingDate).days)*(1-Nd2)
    BSTime = time.time() - start_time
    
    return BSPrice, BSTime
#print(BS_Pricer('Call','European',100,100,2/100,1.002739,0.1))

def BS_Delta(Optiontype,Exercicetype,StockPrice,Strike,TauxInteret,Maturite,PricingDate,Volatilite,base):
    Verif_input(Optiontype,Exercicetype)
    d1 = (np.log(StockPrice/Strike) + (TauxInteret + 0.5 * Volatilite**2)*(Maturite-PricingDate).days) / (Volatilite*np.sqrt((Maturite-PricingDate).days))
    
    if Optiontype not in ["Call"]:
        return norm.cdf(d1, 0, 1)
    else:
        return norm.cdf(d1, 0, 1) - 1
    
def BS_Gamma(Optiontype,Exercicetype,StockPrice,Strike,TauxInteret,Maturite,PricingDate,Volatilite,base):
    Verif_input(Optiontype,Exercicetype)
    d1 = (np.log(StockPrice/Strike) + (TauxInteret + 0.5 * Volatilite**2)*(Maturite-PricingDate).days) / (Volatilite*np.sqrt((Maturite-PricingDate).days))
    
    return norm.pdf(d1, 0, 1) / (StockPrice*Volatilite * np.sqrt((Maturite-PricingDate).days))

def BS_Vega(Optiontype,Exercicetype,StockPrice,Strike,TauxInteret,Maturite,PricingDate,Volatilite,base):
    Verif_input(Optiontype,Exercicetype)
    d1 = (np.log(StockPrice/Strike) + (TauxInteret + 0.5 * Volatilite**2)*(Maturite-PricingDate).days) / (Volatilite*np.sqrt((Maturite-PricingDate).days))
    
    return StockPrice*norm.pdf(d1, 0, 1) * np.sqrt((Maturite-PricingDate).days)

def BS_Theta(Optiontype,Exercicetype,StockPrice,Strike,TauxInteret,Maturite,PricingDate,Volatilite,base):
    Verif_input(Optiontype,Exercicetype)
    d1 = (np.log(StockPrice/Strike) + (TauxInteret + 0.5 * Volatilite**2)*(Maturite-PricingDate).days) / (Volatilite*np.sqrt((Maturite-PricingDate).days))
    d2 = d1 - Volatilite*np.sqrt((Maturite-PricingDate).days)    
    if Optiontype not in ["Call"]:
        return (-StockPrice*norm.pdf(d1, 0, 1)*Volatilite/(2*np.sqrt((Maturite-PricingDate).days)) - TauxInteret*Strike*np.exp(-TauxInteret*(Maturite-PricingDate).days)*norm.cdf(d2, 0, 1))/base
    else:
        return (-StockPrice*norm.pdf(d1, 0, 1)*Volatilite/(2*np.sqrt((Maturite-PricingDate).days)) + TauxInteret*Strike*np.exp(-TauxInteret*(Maturite-PricingDate).days)*norm.cdf(-d2, 0, 1))/base
        
def BS_Rho(Optiontype,Exercicetype,StockPrice,Strike,TauxInteret,Maturite,PricingDate,Volatilite,base):
    Verif_input(Optiontype,Exercicetype)
    d1 = (np.log(StockPrice/Strike) + (TauxInteret + 0.5 * Volatilite**2)*(Maturite-PricingDate).days) / (Volatilite*np.sqrt((Maturite-PricingDate).days))
    d2 = d1 - Volatilite*np.sqrt((Maturite-PricingDate).days)

    if Optiontype not in ["Call"]:
        return Strike*(Maturite-PricingDate).days*np.exp(-TauxInteret*(Maturite-PricingDate).days)*norm.cdf(d2, 0, 1)
    else:
        return -Strike*(Maturite-PricingDate).days*np.exp(-TauxInteret*(Maturite-PricingDate).days)*norm.cdf(-d2, 0, 1)

