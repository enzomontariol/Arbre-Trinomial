
import numpy as np
from scipy.stats import norm

def Verif_input(optiontype,exercisetype):
    if optiontype not in ["Call","Put"] and exercisetype == "Européen": 
        return "Merci de rentrer Call ou Put"

def BS_Pricer(optiontype,exercisetype,S,K,r,time,sigma):
    Verif_input(optiontype,exercisetype)
    
    d1 = (np.log(S/K) + (r + 0.5 * sigma**2)*time) / (sigma*np.sqrt(time))
    d2 = d1 - sigma*np.sqrt(time)
    Nd1 = norm.cdf(d1, 0, 1)
    Nd2 = norm.cdf(d2, 0, 1)

    if optiontype == "Call":
        return S*Nd1 - K*np.exp(-r*time)*Nd2
    else:
        return -S*(1-Nd1) + K*np.exp(-r*time)*(1-Nd2)

#print(BS_Pricer('Call','European',100,100,2/100,1.002739,0.1))

def BS_Delta(optiontype,exercisetype,S,K,r,time,sigma,base):
    Verif_input(optiontype,exercisetype)
    d1 = (np.log(S/K) + (r + 0.5 * sigma**2)*time) / (sigma*np.sqrt(time))
    
    if optiontype not in ["Call"]:
        return norm.cdf(d1, 0, 1)
    else:
        return norm.cdf(d1, 0, 1) - 1
    
def BS_Gamma(optiontype,exercisetype,S,K,r,time,sigma,base):
    Verif_input(optiontype,exercisetype)
    d1 = (np.log(S/K) + (r + 0.5 * sigma**2)*time) / (sigma*np.sqrt(time))
    
    return norm.pdf(d1, 0, 1) / (S*sigma * np.sqrt(time))

def BS_Vega(optiontype,exercisetype,S,K,r,time,sigma,base):
    Verif_input(optiontype,exercisetype)
    d1 = (np.log(S/K) + (r + 0.5 * sigma**2)*time) / (sigma*np.sqrt(time))
    
    return S*norm.pdf(d1, 0, 1) * np.sqrt(time)

def BS_Theta(optiontype,exercisetype,S,K,r,time,sigma,base):
    Verif_input(optiontype,exercisetype)
    d1 = (np.log(S/K) + (r + 0.5 * sigma**2)*time) / (sigma*np.sqrt(time))
    d2 = d1 - sigma*np.sqrt(time)    
    if optiontype not in ["Call"]:
        return (-S*norm.pdf(d1, 0, 1)*sigma/(2*np.sqrt(time)) - r*K*np.exp(-r*time)*norm.cdf(d2, 0, 1))/base
    else:
        return (-S*norm.pdf(d1, 0, 1)*sigma/(2*np.sqrt(time)) + r*K*np.exp(-r*time)*norm.cdf(-d2, 0, 1))/base
        
def BS_Rho(optiontype,exercisetype,S,K,r,time,sigma,base):
    Verif_input(optiontype,exercisetype)
    d1 = (np.log(S/K) + (r + 0.5 * sigma**2)*time) / (sigma*np.sqrt(time))
    d2 = d1 - sigma*np.sqrt(time)

    if optiontype not in ["Call"]:
        return K*time*np.exp(-r*time)*norm.cdf(d2, 0, 1)
    else:
        return -K*time*np.exp(-r*time)*norm.cdf(-d2, 0, 1)

