#%% Imports
import datetime as dt
from dataclasses import dataclass

#%% Classes

@dataclass
class Option : 
    """Classe utilisée pour représenter une option et ses paramètres.
    """
    
    maturite : dt.date
    prix_exercice : float
    americaine : bool = False
    call : bool = True
    date_pricing : dt.date = dt.date.today() 