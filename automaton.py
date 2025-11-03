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
            
            # This is the initial state of the DFA: the lambda-closure of the NFA's start state
            closure = set(self._lambda_closure({self.initial_state}))
            
            def name_state(states):
                if not states:
                    return "∅" # Name for the empty set (dead state)
                "we sort to only get deterministic names"
                return "_".join(sorted(states))

            unchecked_states = [closure] # Worklist of DFA states (as sets of NFA states) to process
            dfa_states = {name_state(closure)} # Set of DFA state names we've seen
            dfa_transitions = {}
            dfa_final_states = set()

            # Check if the initial DFA state is a final state
            for s in closure:
                if s in self.final_states:
                    dfa_final_states.add(name_state(closure))
                    break
            
            while unchecked_states:
                current = unchecked_states.pop() # Get a DFA state (set of NFA states) to process
                current_name = name_state(current)
                if current_name not in dfa_transitions:
                    dfa_transitions[current_name] = {}

                for symbol in symbols:
                    next_states = set() # This will be the new DFA state
                    # Calculate the set of NFA states set from 'current' on 'symbol'
                    for state in current:
                        if state in self.transitions and symbol in self.transitions[state]:
                            for dest in self.transitions[state][symbol]:
                                # For each NFA state set, add its lambda-closure
                                next_states.update(self._lambda_closure({dest}))
                    
                    next_name = name_state(next_states)
                    # Add the transition to the DFA
                    dfa_transitions[current_name][symbol] = [next_name]

                    # If this is a new DFA state we haven't seen before...
                    if next_name not in dfa_states:
                        dfa_states.add(next_name) # Add it to our set of states
                        unchecked_states.append(next_states) # Add it to the worklist to be processed

                        # Check if this new DFA state is a final state
                        for s in next_states:
                            if s in self.final_states:
                                dfa_final_states.add(next_name)
                                break
                
                # **FIX 1:** The "dead states" logic block that was here has been removed.
                # It was redundant, as the main loop correctly processes the "∅" state.
                        
            # **FIX 2:** The return statement has been moved *outside* the 'while' loop.
            # It now runs only after all states have been processed.
            return FiniteAutomaton(
                initial_state=name_state(closure),
                states=dfa_states,
                symbols=symbols,
                transitions=dfa_transitions,
                final_states=dfa_final_states
            )
    


    def to_minimized(self):
        """
        Minimiza un DFA usando el método clásico de refinamiento de clases de equivalencia.
        """

        # --- 1️⃣ Eliminar estados inaccesibles (BFS) ---
        set = set()
        queue = deque([self.initial_state])

        while queue:
            state = queue.popleft()
            if state in set:
                continue
            set.add(state)
            for sym, dests in self.transitions.get(state, {}).items():
                if dests:
                    for d in dests:
                        if d not in set:
                            queue.append(d)


        states = set
        symbols = [s for s in self.symbols if s not in (None, 'λ')]
        transitions = {}
        for s in states:
            transitions[s] = {}
            for sym in symbols:
                dests = self.transitions.get(s, {}).get(sym, [])
                transitions[s][sym] = dests[0] if dests else None

        finals = {s for s in self.final_states if s in states}
        class_map = {s: (1 if s in finals else 0) for s in states}

        changed = True
        while changed:
            changed = False
            new_classes = {}
            signatures = {}
            next_class = 0

            for state in sorted(states):
                signature = (class_map[state],) + tuple(
                    class_map.get(transitions[state][sym], -1) for sym in symbols
                )
                if signature not in signatures:
                    signatures[signature] = next_class
                    next_class += 1

                new_classes[state] = signatures[signature]

            if new_classes != class_map:
                class_map = new_classes
                changed = True

        class_names = {cls: f"C{cls}" for cls in set(class_map.values())}

        min_states = set(class_names.values())
        min_initial = class_names[class_map[self.initial_state]]
        min_finals = {class_names[class_map[s]] for s in finals}


        min_transitions = {}
        for s in states:
            src = class_names[class_map[s]]
            if src not in min_transitions:
                min_transitions[src] = {}
            for sym in symbols:
                dest = transitions[s][sym]
                if dest is not None:
                    dest_cls = class_names[class_map[dest]]
                    min_transitions[src][sym] = [dest_cls]


        return FiniteAutomaton(
            initial_state=min_initial,
            states=min_states,
            symbols=set(symbols),
            transitions=min_transitions,
            final_states=min_finals
        )


        
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
