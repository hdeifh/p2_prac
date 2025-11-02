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
    
    # Standalone helper function
    def null_transition(self, transitions, src, dst):
        """
        Add a λ-transition from src to dst in the transitions dictionary.

        Args:
            transitions: dict representing automaton transitions
            src: source state
            dst: destination state
        """
        if src not in transitions:
            transitions[src] = {}
        if "λ" in transitions[src]:
            existing = transitions[src]["λ"]
            if isinstance(existing, list):
                if dst not in existing:
                    existing.append(dst)
            else:
                if existing != dst:
                    transitions[src]["λ"] = [existing, dst]
        else:
            transitions[src]["λ"] = [dst]


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

        # λ-move from new initial to old initial (to start automaton)
        self.null_transition(transitions, new_initial, automaton.initial_state)

        # λ-move from new initial to new final (to accept ε)
        self.null_transition(transitions, new_initial, new_final)

        # λ-move from each old final to old initial (to repeat)
        for f in automaton.final_states:
            self.null_transition(transitions, f, automaton.initial_state)

        # λ-move from each old final to new final (to stop)
        for f in automaton.final_states:
            self.null_transition(transitions, f, new_final)

        initial_state = new_initial
        final_states = {new_final}

        return FiniteAutomaton(initial_state, states, symbols, transitions, final_states)

    def _create_automaton_union(self, automaton1, automaton2):
        """
        Create an automaton that accepts the union of two automata by creating
        a new start and end state, with λ-transitions.

        Args:
            automaton1: First automaton. Type: FiniteAutomaton.
            automaton2: Second automaton. Type: FiniteAutomaton.

        Returns:
            Automaton that accepts the union. Type: FiniteAutomaton
        """
        # Merge states and symbols
        states = automaton1.states | automaton2.states
        symbols = automaton1.symbols | automaton2.symbols
        transitions = {**automaton1.transitions, **automaton2.transitions}

        # Create new start and end states
        new_start = str(self.state_counter)  # or any method your class uses
        new_end = str(self.state_counter + 1)
        self.state_counter += 2
        states.update([new_start, new_end])

        # Add λ-transitions from new start to original initial states
        self.null_transition(transitions, new_start, automaton1.initial_state)
        self.null_transition(transitions, new_start, automaton2.initial_state)

        # Add λ-transitions from original final states to new end state
        for f in automaton1.final_states:
            self.null_transition(transitions, f, new_end)
        for f in automaton2.final_states:
            self.null_transition(transitions, f, new_end)

        # The new final state is the only final state
        final_states = {new_end}

        return FiniteAutomaton(new_start, states, symbols, transitions, final_states)

    def _create_automaton_concat(self, automaton1, automaton2):
        """
        Create an automaton that accepts the concatenation of two automata
        by connecting the final states of automaton1 to the initial state of automaton2.

        Args:
            automaton1: First automaton. Type: FiniteAutomaton
            automaton2: Second automaton. Type: FiniteAutomaton

        Returns:
            Automaton that accepts the concatenation. Type: FiniteAutomaton
        """
        # Merge states, symbols, and transitions
        states = automaton1.states | automaton2.states
        symbols = automaton1.symbols | automaton2.symbols
        transitions = {**automaton1.transitions, **automaton2.transitions}

        # Connect final states of automaton1 to initial state of automaton2
        for f in automaton1.final_states:
            self.null_transition(transitions, f, automaton2.initial_state)

        # Final states are the final states of automaton2
        final_states = automaton2.final_states

        # Initial state is the initial of automaton1
        initial_state = automaton1.initial_state

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
