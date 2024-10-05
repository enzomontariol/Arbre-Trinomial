#%% Imports

from enum import Enum

#%% Classes enum

class ConventionBaseCalendaire(Enum) :
    _365 = 365
    _360 = 360
    
class MethodeConstructionArbre(Enum) : 
    vanille = "vanille"
    speed = "speed"