#%% Imports
import datetime as dt
from dataclasses import dataclass

from module_barriere import Barriere

#%% Classes

@dataclass
class Option : 
    """Classe utilisée pour représenter une option et ses paramètres.
    """
    
    maturite : dt.date
    prix_exercice : float
    barriere : Barriere
    americaine : bool = False
    call : bool = True
    date_pricing : dt.date = dt.date.today() 
    