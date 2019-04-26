#! /usr/bin/env python3


# Módulo Game

import sys
import random

from enumeration import Goal, Status, Action
from entidade import Room, Agent, Knowledge, Cave
from conhecimento import perceive, tell, update, ask



def print_intro():
  print('\n')
  print('*******************************')
  print('Caçada ao Wumpus')
  print('Inteligência Artificial em Ação')
  print('*******************************')
  print('\n')


def print_actions():
  print('1) Mover para frente')
  print('2) Virar a esquerda')
  print('3) Virar a direita')
  print('4) Pegar')
  print('5) Atirar')


def print_perceptions(perceptions):
  wumpus, pit, gold = perceptions
  if wumpus == Status.Present:
    print('Você percebeu um stench.')
  if pit == Status.Present:
    print('Você percebeu uma brisa.')
  if gold == Status.Present:
    print('Você percebeu um brilho.')
  if perceptions == (Status.Absent,) * 3:
    print('Sem percepções.')
  print()


def parse_action(action):
  if action == 1:
    return Action.Move, (0,)
  elif action == 2:
    return Action.Turn, -1
  elif action == 3:
    return Action.Turn, 1
  elif action == 4:
    return Action.Grab, None
  elif action == 5:
    return Action.Shoot, None


def print_cave(loc):
  print(' __________________')
  y = 0
  while y < 4:
    x = 0
    while x < 4:
      print('|_X_|' if (x, y) == loc else '|___|', end='')
      x += 1
    print()
    y += 1
  print()



if __name__ == '__main__':

  # Init seed
  if '-seed' in sys.argv:
    seed = int(sys.argv[sys.argv.index('-seed') + 1])
    random.seed(seed)
  
  # Define as entidades
  cave = Cave()
  kb = Knowledge()
  agent = Agent()
  
  # Mostra a introdução
  print_intro()
  
  # Executa o jogo
  while True:
    print('Agente:\n{}'.format(agent))
    print_cave(agent.location)
    
    # Percepção na localidade corrente
    perceptions = perceive(cave, agent.location)
    if perceptions is None:
      print('Game Over. Você Morreu!')
      break

    # Ativa o módulo de Inteligência Artificial  
    print_perceptions(perceptions)

    if '-ai' in sys.argv:
      tell(kb, perceptions, agent.location)
      update(kb, agent.location)
      goal = Goal.SeekGold if not agent.has_gold else Goal.BackToEntry
      action = ask(kb, agent.location, agent.direction, goal)
      print('Ação:\n{} {}\n'.format(*action))
      input('Pressione Enter para a Próxima Ação!')
    else:
      print_actions()
      action = int(input('Qual sua Próxima Ação? '))
      print()
      action = parse_action(action)
    
    # Realiza ação
    if agent.perform(action, cave, kb):
      print('Você percebeu um grito.\n')
    
    # Verifica se o jogo terminou e o agente venceu
    if agent.has_gold and agent.location == (0, 0):
      print_cave(agent.location)
      print('Você Venceu!!')
      break
