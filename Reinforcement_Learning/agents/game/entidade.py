#! /usr/bin/env python


# Módulo que define as entidades do jogo

import random

from enumeration import Status, Entity, Action, CardinalDirection
from movimento import turn, move_forward



class Room:

  """Representa um único quarto da caverna."""

  def __init__(self, wumpus=Status.Absent, pit=Status.Absent, gold=Status.Absent):
    
    """Inicializa o status do quarto.
    Por padrão, o quarto é seguro e sem ouro."""
    
    self.wumpus = wumpus
    self.pit = pit
    self.gold = gold


  def __repr__(self):

    """Retorna a representação de sequência de caracteres dessa instância."""
    
    return str([self.wumpus.value, self.pit.value, self.gold.value])


  def is_safe(self, danger=None):
    
    """Retorna True se a sala não contém nem o Wumpus nem um poço."""
    
    if danger is None:
      return self.wumpus == Status.Absent and self.pit == Status.Absent
    if danger == Entity.Wumpus:
      return self.wumpus == Status.Absent
    if danger == Entity.Pit:
      return self.pit == Status.Absent
    raise ValueError


  def is_unsafe(self, danger=None):
    
    """Retorna True se a sala não contém o Wumpus ou um poço."""
    
    return self.is_dangerous(danger) or self.is_deadly(danger)

  
  def is_dangerous(self, danger=None):
    
    """Retorna True se a sala pode conter o Wumpus ou um poço."""
    
    if danger is None:
      return self.wumpus == Status.LikelyPresent or self.pit == Status.LikelyPresent
    if danger == Entity.Wumpus:
      return self.wumpus == Status.LikelyPresent
    if danger == Entity.Pit:
      return self.pit == Status.LikelyPresent
    raise ValueError


  def is_deadly(self, danger=None):
    
    """Retorna True se a sala contiver o Wumpus ou um poço."""
    
    if danger is None:
      return self.wumpus == Status.Present or self.pit == Status.Present
    if danger == Entity.Wumpus:
      return self.wumpus == Status.Present
    if danger == Entity.Pit:
      return self.pit == Status.Present
    raise ValueError


  @property
  def is_explored(self):
    
    """Retorna True é a sala já foi explorada."""
    
    assert self.gold != Status.LikelyPresent
    return self.gold != Status.Unknown


  @property
  def is_unexplored(self):
    
    """Retorna True é a sala não foi explorada."""
    
    return not self.is_explored



class Agent:

  """Representa o agente que explora a caverna."""

  def __init__(self):
  
    """Inicializa o agente com parâmetros default."""
  
    self.location = (0, 0)
    self.direction = 1
    self.has_gold = False
    self.has_arrow = True


  def __repr__(self):
    
    """Retorna a representação de string dessa instância."""
    
    return str([self.location, self.direction, self.has_gold, self.has_arrow])

  
  def __str__(self):
    info = 'Localização: {}\n'.format(self.location)
    info += 'Direção: {}\n'.format(CardinalDirection(self.direction).name)
    info += 'Tem ouro? {}\n'.format(self.has_gold)
    info += 'Tem a flecha? {}'.format(self.has_arrow)
    return info


  def perform(self, action, cave, kb):

    """Executa uma ação. Retorna True se a ação mata o Wumpus, caso contrário False."""

    kind, rotations = action
    if kind == Action.Move:
      self.move(rotations)
    elif kind == Action.Shoot:
      if rotations is not None:
        self.direction = turn(self.direction, rotations)
      return self.shoot(cave, kb)
    elif kind == Action.Grab:
      cave[self.location].gold = Status.Absent
      self.has_gold = True
    elif kind == Action.Turn:
      self.direction = turn(self.direction, rotations)
    return False


  def move(self, rotations):
   
    """Move o agente."""
   
    for steps in rotations:
      self.direction = turn(self.direction, steps)
      self.location = move_forward(self.location, self.direction)


  def shoot(self, cave, kb):

    """Atira a flecha e verifica se o Wumpus foi atingido."""

    x, y = self.location
    width, height = cave.size

    # Remove a flecha
    self.has_arrow = False

    # Atira de acordo com a direção atual
    if self.direction == 0:
      
      # Segue os quartos acima
      i = y
      while i >= 0:
        kb[x, i].wumpus = Status.Absent
        if cave[x, i].wumpus == Status.Present:
          cave[x, i].wumpus = Status.Absent
          kb.kill_wumpus()
          return True
        i -= 1
    elif self.direction == 1:
      
      # Segue os quartos à direita
      i = x
      while i < width:
        kb[i, y].wumpus = Status.Absent
        if cave[i, y].wumpus == Status.Present:
          cave[i, y].wumpus = Status.Absent
          kb.kill_wumpus()
          return True
        i += 1
    elif self.direction == 2:
      
      # Segue os quartos abaixo
      i = y
      while i < height:
        kb[x, i].wumpus = Status.Absent
        if cave[x, i].wumpus == Status.Present:
          cave[x, i].wumpus = Status.Absent
          kb.kill_wumpus()
          return True
        i += 1
    else:
      
      # Segue os quartos à esquerda
      i = x
      while i >= 0:
        kb[i, y].wumpus = Status.Absent
        if cave[i, y].wumpus == Status.Present:
          cave[i, y].wumpus = Status.Absent
          kb.kill_wumpus()
          return True
        i -= 1
    
    # A flecha não atingiu o Wumpus
    return False



class Knowledge:
 
  """Representa o conhecimento do agente sobre a caverna."""
  
  def __init__(self, size=(4, 4)):
 
    """Inicializa uma nova instância da classe Knowledge."""
 
    self.size = size
 
    # Inicialmente o agente não sabe nada
    w, h = self.size
    status = Status.Unknown, Status.Unknown, Status.Unknown
    self._rooms = [[Room(*status) for x in range(w)] for y in range(h)]
 
    # A entrada da caverna é segura e sem ouro
    self._rooms[0][0] = Room()


  def __repr__(self):
 
    """Retorna a representação de string dessa instância."""
 
    width, height = self.size
    plant = ''
    y = 0
    while y < height:
      x = 0
      while x < width:
        plant += '{}\t'.format(self._rooms[y][x])
        x += 1
      plant += '\n' if y != height - 1 else ''
      y += 1
    return plant


  def __getitem__(self, location):

    """Obtém a localidade do quarto."""

    x, y = location
    return self._rooms[y][x]


  def __setitem__(self, location, value):

    """Define a localidade do quarto."""

    x, y = location
    self._rooms[y][x] = value


  def rooms(self, condition=None):

    """Retorna um gerador de índices de células que cumprem a condição."""

    y = 0
    for path in self._rooms:
      x = 0
      for room in path:
        if condition is None or condition(room):
          yield x, y
        x += 1
      y += 1


  @property
  def explored(self):

    """Retorna um gerador de índices de salas já exploradas."""

    return self.rooms(lambda r: r.is_explored)


  @property
  def unexplored(self):

    """Retorna um gerador de índices de salas inexploradas."""

    return self.rooms(lambda r: not r.is_explored)


  def kill_wumpus(self):

    """Altera o status de qualquer sala de tal forma que não pode ser o Wumpus."""

    for path in self._rooms:
      for room in path:
        room.wumpus = Status.Absent



class Cave(Knowledge):
  
  """Representa a caverna onde o Wumpus vive."""

  def __init__(self, size=(4, 4)):
  
    """Inicializa uma nova instância da classe Cave."""
  
    self.size = size
  
    # A caverna contém uma matriz de quartos
    w, h = self.size
    self._rooms = [[Room() for x in range(w)] for y in range(h)]
    unsafe = [(x, y) for x in range(w) for y in range(h) if (x, y) != (0, 0)]
  
    # Coloca o Wumpus na caverna
    x, y = random.choice(unsafe)
    self._rooms[y][x].wumpus = Status.Present
  
    # Coloca o ouro na caverna
    x, y = random.choice(unsafe)
    self._rooms[y][x].gold = Status.Present
  
    # Coloca poços na caverna (com probabilidade 0,2)
    for x, y in unsafe:
      if random.random() <= 0.2:
        self._rooms[y][x].pit = Status.Present

  