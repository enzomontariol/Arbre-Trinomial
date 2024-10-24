#%% Imports

from enum import Enum

#%% Classes enum

class ConventionBaseCalendaire(Enum) :
    _365 = 365
    _360 = 360
    
class TypeBarriere(Enum) : 
    knock_in = "knock-in"
    knock_out = "knock-out"
    
class DirectionBarriere(Enum) : 
    up = "up"
    down = "down"