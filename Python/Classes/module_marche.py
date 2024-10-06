#%% Imports

import datetime as dt
from dataclasses import dataclass

#%% Classes

@dataclass
class DonneeMarche : 
    """Classe utilisée pour représenter les données de marché.
    """
    
    date_debut : dt.date
    prix_spot : float
    volatilite : float
    taux_interet : float 
    taux_actualisation : float
