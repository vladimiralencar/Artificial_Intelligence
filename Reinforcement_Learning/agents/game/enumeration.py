#! /usr/bin/env python


# Módulo usado para definir status

import enum

class Status(enum.Enum):
  """Enumerações usadas para indicar o status de quarto."""
  Unknown = -1
  Absent = 0
  Present = 1
  LikelyPresent = 2


class Entity(enum.Enum):
  """Enumeração de Entidades."""
  Wumpus = 0
  Pit = 1
  Gold = 2


class Action(enum.Enum):
  """Enumeração de ações possíveis do agente."""
  Move = 0
  Shoot = 1
  Grab = 2
  Turn = 3


class Goal(enum.Enum):
  """Enumera os objetivos do agente."""
  SeekGold = 0
  BackToEntry = 1


class CardinalDirection(enum.Enum):
  """Enumera as direções cardinais."""
  North = 0
  East = 1
  South = 2
  West = 3