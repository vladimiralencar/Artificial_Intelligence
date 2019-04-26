#! /usr/bin/env python


# Módulo que define os movimentos do agente

# Objeto DELTA usado para mover o agente e alcançar seus vizinhos
DELTA = (0, -1), (1, 0), (0, 1), (-1, 0)


def neighbors(location, size=(4, 4)):
  
  """Retorna um gerador para os quartos vizinhos."""
  
  x, y = location
  width, height = size
  
  #  célula acima
  if y - 1 >= 0:
    yield x, y - 1
  
  # célula à direita
  if x + 1 < width:
    yield x + 1, y
  
  # célula abaixo
  if y + 1 < height:
    yield x, y + 1
  
  # célula à esquerda
  if x - 1 >= 0:
    yield x - 1, y


def neighbor(location, direction, size=(4, 4)):
  
  """Obter o vizinho de acordo com a localização e direção."""
  
  x, y = location
  width, height = size
  dx, dy = DELTA[direction]
  
  # Verifica se o vizinho está dentro da caverna
  if 0 <= x + dx < width and 0 <= y + dy < height:
    return x + dx, y + dy


def turn(direction, steps):
  
  """Retorna a nova direção."""
  
  return (direction + steps) % len(DELTA)


def move_forward(location, direction):
  
  """Retorna o novo local."""
  
  return neighbor(location, direction)


def spins(source, direction, destination):

  """Obtém o número de rotações necessárias para ter a sala de destino à frente."""

  assert source in neighbors(destination)
  
  # Calcula a diferença entre os locais
  diff = tuple([a - b for a, b in zip(destination, source)])
  rot = DELTA.index(diff) - direction
  rot = rot if rot != 3 else -1
  
  # Retorna o número mínimo de rotações (sentido horário vs sentido anti-horário)
  return rot


def known_path_rec(kb, loc, dest, path, visited):

  """Algoritmo de Busca: Pesquisa em profundidade que constrói um caminho explorado para o destino."""

  if loc == dest:
    return True
  
  # Gerador de vizinhos explorados (mas ainda não visitados pela pesquisa)
  neighborhood = (l for l in neighbors(loc) if l not in visited 
                  and (kb[l].is_explored or l == dest))
  
  # Iterar sobre cada vizinho
  for n in neighborhood:
    
    # Adiciona o nó ao caminho
    path.append(n)
    visited.add(n)
    
    # Chamada recursiva
    if known_path_rec(kb, n, dest, path, visited):
      return True
    
    # Backtrack: este nó não conduz ao destino
    visited.remove(n)
    path.remove(n)
  return False


def known_path(kb, loc, dest):
  
  """Retorna um caminho explorado para o destino."""
  
  path = [loc]
  visited = set()
  visited.add(loc)
  
  # Retorna o caminho ou nenhum se o caminho não foi encontrado
  if known_path_rec(kb, loc, dest, path, visited):
    return tuple(path)


def path_to_spins(path, direction):
  
  """Obtém uma lista de rotações que um agente deve executar para seguir o caminho."""
  
  # Verifica a presença de um caminho válido
  assert path is not None
  rotations = []
  
  # Segue o caminho e calcula os passos necessários para girar e depois avançar
  # até alcançar a última localização do caminho
  i = 0
  while i < len(path) - 1:
    rot = spins(path[i], direction, path[i + 1])
    rotations.append(rot)
    direction = (direction + rot) % len(DELTA)
    i += 1
  return tuple(rotations)
