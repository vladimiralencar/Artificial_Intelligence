# Esse script é uma implementação de agentes em Python
# Neste script você encontra a especificação da classe Python que cria o Agente
# No Jupyter Notebook anexo, você encontra a utilização do Agente

from grid import *
from statistics import mean
import random
import copy
import collections


# Classe que representa objetos físicos que podem aparecer em um ambiente.
# Cada "coisa" pode ter um atributo .__name__ usado para output
class Thing(object):

    def __repr__(self):
        return '<{}>'.format(getattr(self, '__name__', self.__class__.__name__))

    def is_alive(self):
        "Coisas que estão vivas' devem retornar True."
        return hasattr(self, 'alive') and self.alive

    def show_state(self):
        "Exibe o estado interno do agente. Subclasses devem substituir."
        print("Não sei como mostrar o estado.")

    def display(self, canvas, x, y, width, height):
        "Mostre uma imagem desta 'coisa na tela."
        pass


class Agent(Thing):

    """Um Agente é uma subclasse da classe Thing, que deve conter uma função que recebe um argumento, 
     a percepção, e retorna uma ação. (O que conta como uma percepção ou ação
     dependerá do ambiente específico em que o agente existir.)
     Note que 'programa' é um slot, não um método. Se fosse um método,
     então o programa poderia "enganar" e olhar para os aspectos do agente.
     Isso não deve ser feito. Um programa de agente que precisa de um modelo do mundo (e do
     próprio agente) terá que construir e manter seu próprio modelo.
     Há um slot opcional, .performance, que é um número que dá
     a medida de desempenho do agente em seu ambiente.."""

    def __init__(self, program=None):
        self.alive = True
        self.bump = False
        self.holding = []
        self.performance = 0
        if program is None:
            def program(percept):
                return eval(input('Percept={}; action? ' .format(percept)))
        assert isinstance(program, collections.Callable)
        self.program = program

    def can_grab(self, thing):
        """Retorna True se este agente pode pegar essa coisa.
         Substituir para subclasses apropriadas de Agente e Coisa."""
        return False


def TraceAgent(agent):
    """Acompanha o programa do agente para imprimir sua entrada e saída. Isso deixará
     Você ver o que o agente está fazendo no ambiente."""
    old_program = agent.program

    def new_program(percept):
        action = old_program(percept)
        print('{} percebe {} e faz {}'.format(agent, percept, action))
        return action
    agent.program = new_program
    return agent


def TableDrivenAgentProgram(table):
    """Esse agente seleciona uma ação baseada na sequência de percepção.
     É prático apenas para domínios minúsculos.
     Para personalizá-lo, forneça como tabela um dicionário de todos os pares
     {Percept_sequence: action}.["""
    percepts = []

    def program(percept):
        percepts.append(percept)
        action = table.get(tuple(percepts))
        return action
    return program


def RandomAgentProgram(actions):
    "Um agente que escolhe uma ação aleatoriamente, ignorando todas as percepções."
    return lambda percept: random.choice(actions)


def SimpleReflexAgentProgram(rules, interpret_input):
    "Este agente toma medidas baseadas apenas na percepção."
    def program(percept):
        state = interpret_input(percept)
        rule = rule_match(state, rules)
        action = rule.action
        return action
    return program


def ModelBasedReflexAgentProgram(rules, update_state):
    "Esse agente toma ação com base no percepto e estado."
    def program(percept):
        program.state = update_state(program.state, program.action, percept)
        rule = rule_match(program.state, rules)
        action = rule.action
        return action
    program.state = program.action = None
    return program


def rule_match(state, rules):
    "Encontre a primeira regra que corresponda ao estado."
    for rule in rules:
        if rule.matches(state):
            return rule


# Ambiente

class Environment(object):

    """Classe abstrata que representa um ambiente. Classes de Ambiente 'Real'
     vão herdar dessa classe. Seu Ambiente normalmente precisará implementar:

         Percept: Define a percepção que um agente vê.
         Execute_action: Define os efeitos da execução de uma ação. Atualize também o slot agent.performance.

     O ambiente mantém uma lista de .things e .agents (que é um subconjunto
     das coisas). Cada agente tem um slot de desempenho, inicializado a 0.
     Cada coisa tem um slot de localização, mesmo que alguns ambientes não
     precisem disso."""

    def __init__(self):
        self.things = []
        self.agents = []

    # lista de classes do ambiente
    def thing_classes(self):
        return []  

    def percept(self, agent):
        '''
            Retorna a percepção que o agente vê. Pode ser implementado com base no ambiente.
        '''
        raise NotImplementedError

    def execute_action(self, agent, action):
        "Altera o mundo (ambiente)"
        raise NotImplementedError

    def default_location(self, thing):
        "Localização padrão para colocar uma nova Coisa."
        return None

    def exogenous_change(self):
        "Verifica se há mudança espontânea no mundo"
        pass

    def is_done(self):
        "Por padrão, o programa encerra quando não podemos encontrar um agente vivo."
        return not any(agent.is_alive() for agent in self.agents)

    def step(self):
        """Executar o ambiente para um passo de tempo."""
        if not self.is_done():
            actions = []
            for agent in self.agents:
                if agent.alive:
                    actions.append(agent.program(self.percept(agent)))
                else:
                    actions.append("")
            for (agent, action) in zip(self.agents, actions):
                self.execute_action(agent, action)
            self.exogenous_change()

    def run(self, steps=1000):
        "Execute o ambiente para determinado número de etapas de tempo."
        for step in range(steps):
            if self.is_done():
                return
            self.step()

    def list_things_at(self, location, tclass=Thing):
        "Devolva todas as coisas exatamente em um determinado local."
        return [thing for thing in self.things
                if thing.location == location and isinstance(thing, tclass)]

    def some_things_at(self, location, tclass=Thing):
        """Retorna true se pelo menos uma das coisas no local
         for uma instância de classe tclass (ou uma subclasse)."""
        return self.list_things_at(location, tclass) != []

    def add_thing(self, thing, location=None):
        """Adicione uma coisa ao ambiente, definindo sua localização. Para
         Conveniência, se a coisa é um programa do agente nós fazemos um agente novo
         Para ele."""
        if not isinstance(thing, Thing):
            thing = Agent(thing)
        assert thing not in self.things, "Don't add the same thing twice"
        thing.location = location if location is not None else self.default_location(thing)
        self.things.append(thing)
        if isinstance(thing, Agent):
            thing.performance = 0
            self.agents.append(thing)

    def delete_thing(self, thing):
        """Remove uma coisa no ambiente."""
        try:
            self.things.remove(thing)
        except ValueError as e:
            print(e)
            print("  in Environment delete_thing")
            print("  Thing to be removed: {} at {}" .format(thing, thing.location))
            print("  from list: {}" .format([(thing, thing.location) for thing in self.things]))
        if thing in self.agents:
            self.agents.remove(thing)

class Direction():
    '''Uma classe de direção para agentes que querem mover-se em um plano 2D'''

    R = "right"
    L = "left"
    U = "up"
    D = "down"

    def __init__(self, direction):
        self.direction = direction

    def __add__(self, heading):
        if self.direction == self.R:
            return{
                self.R: Direction(self.D),
                self.L: Direction(self.U),
            }.get(heading, None)
        elif self.direction == self.L:
            return{
                self.R: Direction(self.U),
                self.L: Direction(self.L),
            }.get(heading, None)
        elif self.direction == self.U:
            return{
                self.R: Direction(self.R),
                self.L: Direction(self.L),
            }.get(heading, None)
        elif self.direction == self.D:
            return{
                self.R: Direction(self.L),
                self.L: Direction(self.R),
            }.get(heading, None)

    def move_forward(self, from_location):
        x, y = from_location
        if self.direction == self.R:
            return (x+1, y)
        elif self.direction == self.L:
            return (x-1, y)
        elif self.direction == self.U:
            return (x, y-1)
        elif self.direction == self.D:
            return (x, y+1)


class Obstacle(Thing):

    """Algo que pode causar um impacto, impedindo um agente de
     mover-se para o mesmo espaço em que está."""
    pass


class Wall(Obstacle):
    pass


def compare_agents(EnvFactory, AgentFactories, n=10, steps=1000):
    """Compara vários agentes em n instâncias de um ambiente."""
    envs = [EnvFactory() for i in range(n)]
    return [(A, test_agent(A, steps, copy.deepcopy(envs)))
            for A in AgentFactories]


def test_agent(AgentFactory, steps, envs):
    "Retornar a pontuação média de execução de um agente em cada um dos ambientes, para as etapas"
    def score(env):
        agent = AgentFactory()
        env.add_thing(agent)
        env.run(steps)
        return agent.performance
    return mean(map(score, envs))



