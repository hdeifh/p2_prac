"""
    Equipo docente de Autómatas y Lenguajes Curso 2025-26
    Última modificación: 18 de septiembre de 2025
"""

from collections import deque
from graphviz import Digraph
# from utils import is_deterministic

"""
    Podéis implementar cualquier función auxiliar que consideréis necesaria
"""

class FiniteAutomaton:
    def __init__(self, initial_state, states, symbols, transitions, final_states):
        """
        Constructor for a finite automaton (NFA-compatible).

        args:
            initial_state: The automaton's starting state
            states: a set of all states
            symbols: alphabet of symbols
            transitions: dictionary of transitions {state: {symbol: [dest_states]}}
            final_states: a set of states that can be accepted
        """
        self.initial_state = initial_state
        self.states = states
        self.symbols = symbols
        # Ensure transitions store lists of destination states
        self.transitions = {}
        for s, sym_dict in transitions.items():
            self.transitions[s] = {}
            for sym, dest in sym_dict.items():
                if isinstance(dest, list):
                    self.transitions[s][sym] = dest
                else:
                    self.transitions[s][sym] = [dest]
        self.final_states = final_states

    def add_transition(self, start_state, symbol, end_state):
        """
        Adds a transition to the automaton (supports multiple destinations)
        """
        if start_state not in self.transitions:
            self.transitions[start_state] = {}
        if symbol not in self.transitions[start_state]:
            self.transitions[start_state][symbol] = []
        self.transitions[start_state][symbol].append(end_state)

    def _lambda_closure(self, states):
        """
        Computes the λ-closure (or None-closure) of a set of states
        """
        stack = list(states)
        closure = set(states)
        while stack:
            state = stack.pop()
            for sym in ("λ", None):
                if state in self.transitions and sym in self.transitions[state]:
                    for next_state in self.transitions[state][sym]:
                        if next_state not in closure:
                            closure.add(next_state)
                            stack.append(next_state)
        return closure

    def accepts(self, cadena):
        """
        Checks if the NFA accepts a given string
        """
        current_states = self._lambda_closure({self.initial_state})

        for symbol in cadena:
            next_states = set()
            for state in current_states:
                if state in self.transitions and symbol in self.transitions[state]:
                    for dest in self.transitions[state][symbol]:
                        next_states.update(self._lambda_closure({dest}))
            current_states = next_states
            if not current_states:
                return False

        return any(state in self.final_states for state in current_states)
    
    def to_deterministic(self):
        """   
        Turns automaton into a deterministic DFA
        """

        symbols = set()
        for s in self.symbols:
            if s not in (None, 'λ'):
                symbols.add(s)
        
        closure = set(self._lambda_closure({self.initial_state}))
        
        def name_state(states):
            if not states:
                return "∅"
            "we sort to only get deterministic names"
            return "_".join(sorted(states))

        unchecked_states = [closure]
        dfa_states = {name_state(closure)}
        dfa_transitions = {}
        dfa_final_states = set()

        for s in closure:
            if s in self.final_states:
                dfa_final_states.add(name_state(closure))
                break
        
        while unchecked_states:
            current = unchecked_states.pop()
            current_name = name_state(current)
            if current_name not in dfa_transitions:
                dfa_transitions[current_name] = {}

            for symbol in symbols:
                next_states = set()
                for state in current:
                    if state in self.transitions and symbol in self.transitions[state]:
                        for dest in self.transitions[state][symbol]:
                            next_states.update(self._lambda_closure({dest}))
                next_name = name_state(next_states)
                dfa_transitions[current_name][symbol] = [next_name]

                if next_name not in dfa_states:
                    dfa_states.add(next_name)
                    unchecked_states.append(next_states)

                    for s in next_states:
                        if s in self.final_states:
                            dfa_final_states.add(next_name)
                            break
                "revise (dead states)"
                if "∅" in dfa_states:
                    if "∅" not in dfa_transitions:
                        dfa_transitions["∅"] = {}
                    for symbol in symbols:
                        dfa_transitions["∅"][symbol] = ["∅"]
                    
                return FiniteAutomaton(
                    initial_state=name_state(closure),
                    states=dfa_states,
                    symbols=symbols,
                    transitions=dfa_transitions,
                    final_states=dfa_final_states
                )


    
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

        print('x')
        dot.render(path+filename, view=view)
