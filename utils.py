class Piece:
  def __init__(self, position:int=None, name:str=None, symbol:int=None):
    self._position = position
    self._name = name
    self._symbol = symbol
  
  @property
  def name(self):
    return self._name
    
  @property
  def position(self): 
    return self._position
  
  @position.setter
  def set_position(self, position:int): 
    self._position = position
  
class Position: 
  def __init__(self, name:str, position_idx:dict=None): 
    self.name = name
    self.index = None if position_idx is None else position_idx[name.lower()]