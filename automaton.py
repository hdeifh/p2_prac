"""
    Equipo docente de Autómatas y Lenguajes Curso 2025-26
    Última modificación: 18 de septiembre de 2025
"""

from collections import deque
# from graphviz import Digraph
from utils import is_deterministic

"""
    Podéis implementar cualquier función auxiliar que consideréis necesaria
"""

class FiniteAutomaton:
    def __init__(self, initial_state, states, symbols, transitions, final_states):
        """
        Constructor for a finite automaton.

        args:
        initial_state: The automaton's starting state
        states: a set of all states
        symbols: alphabet of symbols
        transitions: dictionary of transitions
        final_states: a set of states that can be accepted
        """
        self.initial_state = initial_state
        self.states = states
        self.symbols = symbols
        self.transitions = transitions
        self.final_states = final_states
        
    def add_transition(self, start_state, symbol, end_state):
        """
        Adds a transition to the automaton


        args:
        start_state: The initial state of the transition
        symbol: symbol that triggers the transition
        final_states: The destination state of the transition
        """
        if start_state not in self.transitions:
            self.transitions[start_state] = {}
        self.transitions[start_state][symbol] = end_state

    def accepts(self, cadena):
        """
        Checks if the automaton will accept a given string


        args:
        cadena: input string

        returns:
            True if automaton accepts the string
            False if it doesn't
        """
        state = self.initial_state
        for symbol in cadena:
            while True:
                # If the current symbol is valid from this state, consume it
                if state in self.transitions and symbol in self.transitions[state]:
                    state = self.transitions[state][symbol]
                    break  # go to next input symbol
                # If input is None, then assume that None represents null transitions
                elif state in self.transitions and None in self.transitions[state]:
                    state = self.transitions[state][None]
                    continue  # retry with same symbol in new state
                else:
                    return False

        # After consuming all symbols, double-check that there are any null transitions left
        while state in self.transitions and None in self.transitions[state]:
            state = self.transitions[state][None]

        return state in self.final_states
    
    def to_deterministic(self):
        """   
        Turns automaton into a deterministic DFA
        """
        pass

    def to_minimized(self):
        """
        Turns automaton inta a minimized DFA
        """
        pass
        
    def draw(self, path="./images/", filename="automata.png", view=False):
        """
        Draws the automaton

        Args:
        path: pathfile to save the resulting image
        fiilename: name of the image
        view: if true, opens the image after being generated
        """
        dot = Digraph(comment="Automata", format="png")
        dot.attr(rankdir="LR")

        # Nodo invisible para punto inicial
        dot.node("", shape="none")

        # Almacenar estados
        for state in self.states:
            if state in self.final_states:
                dot.node(state, shape="doublecircle")
            else:
                dot.node(state, shape="circle")
        
        # Flecha al estado inicial
        dot.edge("", self.initial_state)

        # Almacenar transiciones
        for state_ini in self.transitions:
            for symbol in self.transitions[state_ini]:
                for state_fin in self.transitions[state_ini][symbol]:
                    dot.edge(state_ini, state_fin, symbol if symbol is not None else "λ")

        dot.render(path+filename, view=view)
