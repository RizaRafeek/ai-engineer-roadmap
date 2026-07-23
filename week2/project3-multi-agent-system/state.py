from typing import TypedDict
from enum import Enum

class SpecialistType(str, Enum):                   #Enum restricts the claass to fall amomg any of the specified classes only
    code = "code"
    research = "research"
    data_analysis ="data_analysis"

class RouterState(TypedDict):
    user_message : str 
    specialist: SpecialistType
    reasoning: str
    final_answer: str