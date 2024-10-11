#%% Imports

from enum import Enum

#%% Classes enum

class ConventionBaseCalendaire(Enum) :
    _365 = 365
    _360 = 360
    
class MethodeConstructionArbre(Enum) : 
    vanille = "vanille"
    speed = "speed"
    
class OptionTypeBS (Enum) : 
    call = "call"
    put = "put"

class ExerciseType (Enum) : 
    europeen = "europeen"
    americain = "americain"
