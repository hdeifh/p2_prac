"""
    Equipo docente de Autómatas y Lenguajes Curso 2025-26
    Última modificación: 18 de septiembre de 2025
"""

from automaton import FiniteAutomaton

def _re_to_rpn(re_string):
    """
    Convert re to reverse polish notation (RPN).

    Does not check that the input re is syntactically correct.

    Args:
        re_string: Regular expression in infix notation. Type: str

    Returns:
        Regular expression in reverse polish notation. Type: str

    """
    stack = [] # List of strings
    rpn_string = ""
    for x in re_string:
        if x == "+":
            while len(stack) > 0 and stack[-1] != "(":
                rpn_string += stack.pop()
            stack.append(x)
        elif x == ".":
            while len(stack) > 0 and stack[-1] == ".":
                rpn_string += stack.pop()
            stack.append(x)
        elif x == "(":
            stack.append(x)
        elif x == ")":
            while stack[-1] != "(":
                rpn_string += stack.pop()
            stack.pop()
        else:
            rpn_string += x

    while len(stack) > 0:
        rpn_string += stack.pop()

    return rpn_string



class REParser():
    """Class for processing regular expressions in Kleene's syntax."""
    
    def __init__(self) -> None:
        self.state_counter = 0

    def _create_automaton_empty(self):
        """
        Create an automaton that accepts the empty language.

        Returns:
            Automaton that accepts the empty language. Type: FiniteAutomaton

        """
        # Create a single state that is not accepting and has no transitions
        state = str(self.state_counter)
        self.state_counter += 1
        states = {str(state)}
        symbols = set()
        transitions = dict()
        initial_state = str(state)
        final_states = set()
        return FiniteAutomaton(initial_state, states, symbols, transitions, final_states)

    def _create_automaton_lambda(self):
        """
        Create an automaton that accepts the empty string.

        Returns:
            Automaton that accepts the empty string. Type: FiniteAutomaton

        """
        # Create a single state that is both initial and final, with no transitions
        state = str(self.state_counter)
        self.state_counter += 1
        states = {state}
        symbols = set()
        transitions = dict()
        initial_state = state
        final_states = {state}
        return FiniteAutomaton(initial_state, states, symbols, transitions, final_states)


    def _create_automaton_symbol(self, symbol):
        """
        Create an automaton that accepts one symbol.

        Args:
            symbol: Symbol that the automaton should accept. Type: str

        Returns:
            Automaton that accepts a symbol. Type: FiniteAutomaton

        """
        state1 = str(self.state_counter)
        state2 = str(self.state_counter + 1)
        self.state_counter += 2
        states = {state1, state2}
        symbols = {symbol}
        transitions = {state1: {symbol: [state2]}}
        initial_state = state1
        final_states = {state2}
        return FiniteAutomaton(initial_state, states, symbols, transitions, final_states)


    def _create_automaton_star(self, automaton):
        """
        Create an automaton that accepts the Kleene star of another.

        Args:
            automaton: Automaton whose Kleene star must be computed. Type: FiniteAutomaton

        Returns:
            Automaton that accepts the Kleene star. Type: FiniteAutomaton
        """
        new_initial = str(self.state_counter)
        new_final = str(self.state_counter + 1)
        self.state_counter += 2

        # Copy states and symbols
        states = set(automaton.states)
        states.update({new_initial, new_final})
        symbols = set(automaton.symbols)

        # Deep copy transitions (flat mapping: state → symbol → single_state)
        transitions = {
            s: dict(t) for s, t in automaton.transitions.items()
        }

        # Helper to safely add a λ-transition
        def add_lambda(src, dst):
            if src not in transitions:
                transitions[src] = {}
            # If a λ transition already exists, turn it into a list of possible λ moves
            if "λ" in transitions[src]:
                # Turn it into a list or set if multiple are needed
                existing = transitions[src]["λ"]
                if isinstance(existing, list):
                    existing.append(dst)
                else:
                    transitions[src]["λ"] = [existing, dst]
            else:
                transitions[src]["λ"] = [dst]

        # λ-move from new initial to old initial (to start automaton)
        add_lambda(new_initial, automaton.initial_state)

        # λ-move from new initial to new final (to accept ε)
        add_lambda(new_initial, new_final)

        # λ-move from each old final to old initial (to repeat)
        for f in automaton.final_states:
            add_lambda(f, automaton.initial_state)

        # λ-move from each old final to new final (to stop)
        for f in automaton.final_states:
            add_lambda(f, new_final)

        initial_state = new_initial
        final_states = {new_final}

        return FiniteAutomaton(initial_state, states, symbols, transitions, final_states)

    def _create_automaton_union(self, automaton1, automaton2):
        """
        Create an automaton that accepts the union of two automata.

        Args:
            automaton1: First automaton of the union. Type: FiniteAutomaton.
            automaton2: Second automaton of the union. Type: FiniteAutomaton.

        Returns:
            Automaton that accepts the union. Type: FiniteAutomaton

        """
        offset = max(automaton1.states | automaton2.states) + 1 if automaton1.states or automaton2.states else 0
        # Offset automaton2 states to avoid collisions
        def offset_states(states, offset):
            return {s + offset for s in states}
        def offset_transitions(transitions, offset):
            new_trans = {}
            for (s, sym), dests in transitions.items():
                new_trans[(s + offset, sym)] = {d + offset for d in dests}
            return new_trans

        a1_states = set(automaton1.states)
        a1_trans = dict(automaton1.transitions)
        a1_init = automaton1.initial_state
        a1_finals = set(automaton1.final_states)

        a2_states = offset_states(automaton2.states, offset)
        a2_trans = offset_transitions(automaton2.transitions, offset)
        a2_init = automaton2.initial_state + offset
        a2_finals = {s + offset for s in automaton2.final_states}

        new_initial = str(self.state_counter)
        new_final = str(self.state_counter + 1)
        self.state_counter += 2

        states = a1_states | a2_states | {new_initial, new_final}
        symbols = set(automaton1.symbols) | set(automaton2.symbols)
        transitions = {}
        transitions.update(a1_trans)
        transitions.update(a2_trans)

        # λ-move from new initial to both automata's initials
        transitions.setdefault((new_initial, "λ"), set()).update({a1_init, a2_init})
        # λ-move from both automata's finals to new final
        for f in a1_finals:
            transitions.setdefault((f, "λ"), set()).add(new_final)
        for f in a2_finals:
            transitions.setdefault((f, "λ"), set()).add(new_final)

        initial_state = new_initial
        final_states = {new_final}
        return FiniteAutomaton(initial_state, states, symbols, transitions, final_states)

    def _create_automaton_concat(self, automaton1, automaton2):
        """
        Create an automaton that accepts the concatenation of two automata (NFA-compatible).

        Args:
            automaton1: First automaton of the concatenation. Type: FiniteAutomaton
            automaton2: Second automaton of the concatenation. Type: FiniteAutomaton

        Returns:
            Automaton that accepts the concatenation. Type: FiniteAutomaton
        """
        # Compute offset for renumbering automaton2 states
        a1_state_ints = [int(s) for s in automaton1.states]
        offset = max(a1_state_ints) + 1 if a1_state_ints else 0

        def offset_state(s):
            return str(int(s) + offset)

        def offset_transitions(trans):
            new_trans = {}
            for s, sym_dict in trans.items():
                new_s = offset_state(s)
                new_trans[new_s] = {}
                for sym, dest_list in sym_dict.items():
                    # Ensure dest_list is always a list
                    if not isinstance(dest_list, list):
                        dest_list = [dest_list]
                    new_trans[new_s][sym] = [offset_state(d) for d in dest_list]
            return new_trans

        # Copy automaton1 transitions (make sure values are lists)
        a1_trans = {}
        for s, sym_dict in automaton1.transitions.items():
            a1_trans[s] = {}
            for sym, dest in sym_dict.items():
                if isinstance(dest, list):
                    a1_trans[s][sym] = dest[:]
                else:
                    a1_trans[s][sym] = [dest]

        # Offset automaton2
        a2_trans = offset_transitions(automaton2.transitions)

        # Merge states, symbols, and transitions
        states = set(automaton1.states) | {offset_state(s) for s in automaton2.states}
        symbols = set(automaton1.symbols) | set(automaton2.symbols)
        transitions = {**a1_trans, **a2_trans}

        # λ-move from each final of automaton1 to initial of automaton2
        a2_init = offset_state(automaton2.initial_state)
        for f in automaton1.final_states:
            if f not in transitions:
                transitions[f] = {}
            if "λ" not in transitions[f]:
                transitions[f]["λ"] = []
            if a2_init not in transitions[f]["λ"]:
                transitions[f]["λ"].append(a2_init)

        initial_state = automaton1.initial_state
        final_states = {offset_state(s) for s in automaton2.final_states}

        return FiniteAutomaton(initial_state, states, symbols, transitions, final_states)

    def create_automaton(
        self,
        re_string,
    ):
        """
        Create an automaton from a regex.

        Args:
            re_string: String with the regular expression in Kleene notation. Type: str

        Returns:
            Automaton equivalent to the regex. Type: FiniteAutomaton

        """
        if not re_string:
            return self._create_automaton_empty()
        
        rpn_string = _re_to_rpn(re_string)

        stack = [] # list of FiniteAutomatons

        self.state_counter = 0
        for x in rpn_string:
            if x == "*":
                aut = stack.pop()
                stack.append(self._create_automaton_star(aut))
            elif x == "+":
                aut2 = stack.pop()
                aut1 = stack.pop()
                stack.append(self._create_automaton_union(aut1, aut2))
            elif x == ".":
                aut2 = stack.pop()
                aut1 = stack.pop()
                stack.append(self._create_automaton_concat(aut1, aut2))
            elif x == "λ":
                stack.append(self._create_automaton_lambda())
            else:
                stack.append(self._create_automaton_symbol(x))

        return stack.pop()
