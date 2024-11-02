#%% Imports

from enum import Enum

#%% Classes enum

class ConventionBaseCalendaire(Enum) :
    _365 = 365
    _360 = 360
    
class TypeBarriere(Enum) : 
    knock_in = "Knock-in"
    knock_out = "Knock-out"
    
class DirectionBarriere(Enum) : 
    up = "Up"
    down = "Down"