#! /usr/bin/env python


# Módulo de conhecimento do agente

import random

from enumeration import Status, Entity, Action, Goal
from movimento import neighbors, spins, known_path, path_to_spins



def perceive(kb, loc):

  """Retorna uma tupla que contém as percepções locais do agente.
   Devolve nenhuma se o agente foi morto pelo Wumpus ou caiu em um poço."""

  if kb[loc].pit == Status.Present or kb[loc].wumpus == Status.Present:
    
    # O agente foi morto e não há percepções
    return None
  
  # Construir percepções
  wumpus, pit, gold = (Status.Absent,) * 3
  
  # Olhar células vizinhas para atualizar as percepções
  for room in [kb[l] for l in neighbors(loc)]:
    
    # Verifique se o wumpus está nesta sala
    if room.wumpus == Status.Present:
      wumpus = Status.Present
    elif room.wumpus == Status.LikelyPresent and wumpus != Status.Present:
      wumpus = Status.LikelyPresent
    
    # Verifique se há poços nesta sala
    if room.pit == Status.Present:
      pit = Status.Present
    elif room.pit == Status.LikelyPresent and pit != Status.Present:
      pit = Status.LikelyPresent
  
  # Verifique se o ouro está nesta célula
  if kb[loc].gold == Status.Present:
    gold = Status.Present  
  
  # Retorna percepções como tupla
  return wumpus, pit, gold


def tell(kb, perceptions, loc):

  """Atualizar o conhecimento de acordo com a percepção e localização."""
  # O agente está vivo e percebeu algo assim:
  # Não há poços nem o Wumpus neste quarto
  
  kb[loc].wumpus = kb[loc].pit = Status.Absent
  wumpus, pit, gold = perceptions
  near = [kb[l] for l in neighbors(loc)]
  
  # Iterar sobre salas vizinhas não seguras
  for room in (r for r in near if not r.is_safe()):
    
    # Analisar a percepção Wumpus
    if room.wumpus != Status.Absent:
      if wumpus == Status.Absent:
        room.wumpus = Status.Absent
      elif wumpus == Status.LikelyPresent:
    
        # Verificar se este é o único local onde o Wumpus pode estar
        if len([r for r in near if r.is_dangerous(Entity.Wumpus)]) == 1:
          room.wumpus = Status.Present
      elif room.wumpus == Status.Unknown:
        if any(r.is_deadly(Entity.Wumpus) for r in near):
    
          # O agente sabe o local Wumpus -> ele não pode estar nesta sala
          room.wumpus = Status.Absent
        elif all(r.is_safe(Entity.Wumpus) for r in near if r != room):
    
          # Todos os outros vizinhos são seguros -> o Wumpus deve estar nesta sala
          room.wumpus = Status.Present
        else:
          room.wumpus = Status.LikelyPresent
    
    # Analisar a percepção dos poços
    if room.pit != Status.Absent:
      if pit == Status.Absent:
        room.pit = Status.Absent
      elif pit == Status.LikelyPresent:
        
        # Verifique se este é o único lugar onde o poço pode estar
        if len([r for r in near if r.is_dangerous(Entity.Pit)]) == 1:
          room.pit = Status.Present
      elif room.pit == Status.Unknown:
        if all(r.is_safe(Entity.Pit) for r in near if r != room):
        
          # Todos os outros vizinhos estão seguros -> o poço deve estar nesta sala
          room.pit = Status.Present
        else:
          room.pit = Status.LikelyPresent
  
  # Analisa a percepção do ouro
  kb[loc].gold = gold


def update(kb, loc):
  
  """Atualizar o conhecimento."""
  # Atualiza o conhecimento de acordo com todas as células já exploradas
  
  for l in [x for x in kb.explored]:
    tell(kb, perceive(kb, l), l)


def ask(kb, loc, direction, goal):
  
  """Retorna uma ação de acordo com o estado atual do conhecimento.
   A ação é uma tupla: o primeiro elemento é o tipo da ação, 
   o segundo elemento é uma lista de movimento se o tipo é Action.Move ou atirar, 
   e o terceiro (caso contrário), é none."""
  
  # Se o agente está procurando ouro
  
  if goal == Goal.SeekGold:
    
    # Verifica se esta sala contém o ouro
    if kb[loc].gold == Status.Present:
      return Action.Grab, None
    
    # Obtém o primeiro quarto vizinho seguro e inexplorado (se houver)
    state = lambda r: r.is_safe() and r.is_unexplored
    dest = next((l for l in neighbors(loc) if state(kb[l])), None)
    if dest:
      return Action.Move, (spins(loc, direction, dest),)
    
    # Obtém qualquer espaço seguro e inexplorado (se o agente pode alcançá-lo)
    state = lambda r, l: r.is_safe() and any(kb[x].is_explored for x in neighbors(l))
    dest = next((l for l in kb.unexplored if state(kb[l], l)), None)
    if dest:
      path = known_path(kb, loc, dest)
      return Action.Move, path_to_spins(path, direction)
    
    # Obtém uma sala vizinha que pode conter o Wumpus, mas sem poços
    state = lambda r: r.is_safe(Entity.Pit) and r.is_unsafe(Entity.Wumpus)
    dest = next((l for l in neighbors(loc) if state(kb[l])), None)
    if dest:
      return Action.Shoot, spins(loc, direction, dest)
    
    # Obtém um quarto que podem conter o Wumpus mas não poços
    state = lambda r: r.is_safe(Entity.Pit) and r.is_unsafe(Entity.Wumpus)
    dest = next((l for l in kb.unexplored if state(kb[l])), None)
    if dest:
    
      # Obtém uma célula vizinha explorada 
      dest = next((l for l in neighbors(dest) if kb[l].is_explored))
      path = known_path(kb, loc, dest)
      return Action.Move, path_to_spins(path, direction)
    
    # Obtém um quarto vizinho que pode conter o Wumpus
    state = lambda r: r.is_dangerous(Entity.Wumpus)
    dest = next((l for l in neighbors(loc) if state(kb[l])), None)
    if dest:
      return Action.Shoot, spins(loc, direction, dest)
    
    # Obtém um quarto vizinho que pode conter um poço
    rooms = [l for l in kb.unexplored if kb[l].is_dangerous(Entity.Pit)]
    if rooms:
      dest = random.choice(rooms)
      path = known_path(kb, loc, dest)
      return Action.Move, path_to_spins(path, direction)
    
    # Obtém uma célula inexplorada
    dest = next((l for l in kb.unexplored), None)
    if dest:
      path = known_path(kb, loc, dest)
      return Action.Move, path_to_spins(path, direction)
  elif goal == Goal.BackToEntry:
    
    # Voltar para a entrada
    path = known_path(kb, loc, (0, 0))
    return Action.Move, path_to_spins(path, direction)
  
  # Incapaz de encontrar uma ação
  return None
