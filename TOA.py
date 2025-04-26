import collections
import sys
import re 

class NFA:
    """Represents an Epsilon NFA."""
    def __init__(self, states, alphabet, transitions, start_state, accept_states):
        self.states = set(states)
        self.alphabet = set(alphabet)
        self.transitions = transitions 
        self.start_state = start_state
        self.accept_states = set(accept_states)
        self._epsilon_closures = {} 

        if self.start_state not in self.states:

            raise ValueError(f"Start state '{self.start_state}' must be one of the defined states {self.states}.")
        if not self.accept_states.issubset(self.states):
             raise ValueError(f"Accept states {self.accept_states} must be a subset of defined states {self.states}.")

        for _, symbol in self.transitions.keys():
             if symbol is not None and symbol not in self.alphabet:
                 raise ValueError(f"Symbol '{symbol}' used in transitions but not in defined alphabet {self.alphabet}.")

        self._compute_all_epsilon_closures()

    def _compute_epsilon_closure(self, state):
        """Computes the epsilon closure for a single state using BFS."""
        if state in self._epsilon_closures:
            return self._epsilon_closures[state]

        closure = {state}
        queue = collections.deque([state])
        visited = {state}

        while queue:
            current_state = queue.popleft()
            epsilon_neighbors = self.transitions.get((current_state, None), set())

            for neighbor in epsilon_neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    closure.add(neighbor)
                    queue.append(neighbor)

        self._epsilon_closures[state] = frozenset(closure)
        return self._epsilon_closures[state]

    def _compute_all_epsilon_closures(self):
        """Pre-computes epsilon closures for all states."""
        for state in self.states:
            self._compute_epsilon_closure(state) 

    def _get_epsilon_closure_set(self, states_set):
        """Computes the epsilon closure for a set of states."""
        full_closure = set()
        for s in states_set:

            full_closure.update(self._epsilon_closures.get(s, {s})) 
        return full_closure

    def accepts(self, input_string):
        """Checks if the NFA accepts the given input string."""
        current_states = self._get_epsilon_closure_set({self.start_state})

        for symbol in input_string:

            if symbol not in self.alphabet:
                print(f"Warning: Input symbol '{symbol}' is not in the NFA's alphabet {self.alphabet}. String will be rejected.")
                return False 

            next_states_after_symbol = set()     
            for state in current_states:
                next_states_for_state = self.transitions.get((state, symbol), set())
                next_states_after_symbol.update(next_states_for_state)

            current_states = self._get_epsilon_closure_set(next_states_after_symbol)

            if not current_states:
                return False 

        return not current_states.isdisjoint(self.accept_states)

    def __str__(self):
        """String representation for debugging."""

        transitions_str = "\n    ".join(f"{k}: {v}" for k, v in sorted(self.transitions.items()))
        return (
            f"NFA(\n"
            f"  States: {sorted(list(self.states))}\n"
            f"  Alphabet: {sorted(list(self.alphabet))}\n"
            f"  Transitions:\n    {transitions_str}\n"
            f"  Start State: {self.start_state}\n"
            f"  Accept States: {sorted(list(self.accept_states))}\n"
            f")"
        )

def parse_grammar(grammar_lines, declared_non_terminals, declared_terminals, declared_start_symbol):
    """
    Parses lines of regular grammar rules, validating against declared symbols.
    Format: 'S -> aA | b' or 'A -> epsilon'
    Returns: grammar_dict {'NonTerminal': [(terminal/None, NextNonTerminal/None), ...]}
    Raises ValueError if rules violate declarations or format.
    """
    grammar = collections.defaultdict(list)

    if not declared_non_terminals:
        raise ValueError("Non-terminal set cannot be empty.")
    if declared_start_symbol not in declared_non_terminals:
        raise ValueError(f"Declared start symbol '{declared_start_symbol}' is not in the set of declared non-terminals {declared_non_terminals}.")
    if not declared_terminals.isdisjoint(declared_non_terminals):
        overlap = declared_terminals.intersection(declared_non_terminals)
        raise ValueError(f"Terminals and non-terminals must be disjoint. Overlap: {overlap}")

    defined_non_terminals_in_rules = set() 

    for line_num, line in enumerate(grammar_lines, 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if "->" not in line:
            raise ValueError(f"Rule {line_num}: Invalid format (missing '->'): {line}")

        head, body = line.split("->", 1)
        head = head.strip()

        if not head:
             raise ValueError(f"Rule {line_num}: Rule head cannot be empty.")
        if head not in declared_non_terminals:
            raise ValueError(f"Rule {line_num}: Head symbol '{head}' is not in the declared non-terminals {declared_non_terminals}.")

        defined_non_terminals_in_rules.add(head)

        productions = [p.strip() for p in body.split("|")]
        if not productions or any(not p for p in productions):
             raise ValueError(f"Rule {line_num}: Rule body for '{head}' cannot be empty or contain empty productions between '|'. Use 'epsilon'.")

        for prod in productions:
            if prod.lower() == "epsilon" or prod == "ε":

                grammar[head].append((None, None)) 
            elif len(prod) == 1:

                terminal = prod
                if terminal not in declared_terminals:
                     raise ValueError(f"Rule {line_num}: Symbol '{terminal}' in production '{prod}' for '{head}' is not in the declared terminals {declared_terminals}.")
                grammar[head].append((terminal, None)) 
            elif len(prod) >= 2: 

                 if len(prod) == 2:
                    terminal = prod[0]
                    next_non_terminal = prod[1]

                    if terminal not in declared_terminals:
                        raise ValueError(f"Rule {line_num}: Symbol '{terminal}' in production '{prod}' for '{head}' is not in the declared terminals {declared_terminals}.")
                    if next_non_terminal not in declared_non_terminals:
                         raise ValueError(f"Rule {line_num}: Symbol '{next_non_terminal}' in production '{prod}' for '{head}' is not in the declared non-terminals {declared_non_terminals}.")

                    grammar[head].append((terminal, next_non_terminal))
                 else: 
                     raise ValueError(f"Rule {line_num}: Invalid production format '{prod}' in rule for '{head}'. Expected 'terminal', 'epsilon', or 'terminal NonTerminal' (e.g., aB).")

            else: 
                raise ValueError(f"Rule {line_num}: Unexpected production format '{prod}' for '{head}'.")

    return dict(grammar)

FINAL_STATE_MARKER = "_FINAL_" 

def build_nfa_from_grammar(grammar_dict, non_terminals, terminals, start_symbol):
    """
    Builds an ε-NFA from a parsed regular grammar.
    Uses the provided sets of non_terminals, terminals, and the start_symbol.
    """

    nfa_states = set(non_terminals)
    if FINAL_STATE_MARKER in nfa_states:

         raise ValueError(f"The internal final state marker '{FINAL_STATE_MARKER}' clashes with a declared non-terminal. Please rename the non-terminal.")
    nfa_states.add(FINAL_STATE_MARKER)

    nfa_alphabet = set(terminals) 
    nfa_transitions = collections.defaultdict(set)
    nfa_start_state = start_symbol 
    nfa_accept_states = {FINAL_STATE_MARKER} 

    for head_state, productions in grammar_dict.items():

        for terminal, next_state in productions:
            if terminal is None and next_state is None:

                nfa_transitions[(head_state, None)].add(FINAL_STATE_MARKER)
            elif terminal is not None and next_state is None:

                nfa_transitions[(head_state, terminal)].add(FINAL_STATE_MARKER)
            elif terminal is not None and next_state is not None:

                nfa_transitions[(head_state, terminal)].add(next_state)
            else:

                 raise RuntimeError(f"Internal error: Unexpected parsed production format ({terminal}, {next_state}) for state '{head_state}'.")

    nfa = NFA(nfa_states, nfa_alphabet, dict(nfa_transitions), nfa_start_state, nfa_accept_states)
    return nfa

def get_symbols_from_input(prompt):
    """Helper to get space-separated symbols from user input."""
    user_input = input(prompt).strip()
    if not user_input:
        return set()

    symbols = set(re.split(r'\s+', user_input))

    return symbols

def main():
    """Main function to run the parser and NFA simulation."""
    print("Regular Grammar to NFA Converter")
    print("--------------------------------")
    print("Define the grammar components first.")

    try:

        terminals = get_symbols_from_input("Enter Terminal symbols (space-separated, e.g., a b 0 1): ")
        if not terminals:
            print("Error: At least one terminal symbol must be provided.", file=sys.stderr)
            return

        non_terminals = get_symbols_from_input("Enter Non-Terminal symbols (space-separated, e.g., S A B): ")
        if not non_terminals:
            print("Error: At least one non-terminal symbol must be provided.", file=sys.stderr)
            return

        start_symbol = input("Enter the Start Symbol (must be one of the non-terminals): ").strip()
        if not start_symbol:
             print("Error: A start symbol must be provided.", file=sys.stderr)
             return
        if start_symbol not in non_terminals:
             print(f"Error: Start symbol '{start_symbol}' is not in the declared non-terminals {non_terminals}.", file=sys.stderr)
             return

        if not terminals.isdisjoint(non_terminals):
             print(f"Error: Terminals and Non-Terminals cannot overlap. Overlap: {terminals.intersection(non_terminals)}", file=sys.stderr)
             return

        print("\n--- Grammar Definition ---")
        print(f"Terminals (Σ): {terminals}")
        print(f"Non-Terminals (V): {non_terminals}")
        print(f"Start Symbol (S): {start_symbol}")
        print("--------------------------")

        print("\nEnter grammar rules (one per line, e.g., 'S -> aA | b').")
        print("Use 'epsilon' or 'ε' for the empty string production.")
        print("Ensure symbols used match the declared terminals and non-terminals.")
        print("Press Enter on an empty line to finish grammar input.")
        print("--------------------------------")

        grammar_lines = []
        while True:
            try:
                line = input("> ")
                if not line:
                    break
                grammar_lines.append(line)
            except EOFError:
                break

        if not grammar_lines:
            print("No grammar rules entered. Exiting.")
            return

        grammar_dict = parse_grammar(grammar_lines, non_terminals, terminals, start_symbol)
        print("\n--- Grammar Parsed Successfully ---")

        nfa = build_nfa_from_grammar(grammar_dict, non_terminals, terminals, start_symbol)
        print("\n--- NFA Constructed ---")

        print(f"NFA States: {nfa.states}")
        print(f"NFA Alphabet: {nfa.alphabet}")
        print(f"NFA Start State: {nfa.start_state}")
        print(f"NFA Accept States: {nfa.accept_states}")

        print("\n--- String Acceptance Check ---")
        print("Enter strings to check (one per line). Press Enter on an empty line to exit.")
        while True:
            try:
                input_string = input("String? ")
                if not input_string and input_string != "": 
                    break

                is_valid_input = all(char in nfa.alphabet for char in input_string)

                if not is_valid_input:
                    invalid_chars = {char for char in input_string if char not in nfa.alphabet}
                    print(f"String '{input_string}': Rejected (Contains symbols not in alphabet: {invalid_chars})")
                else:

                    is_accepted = nfa.accepts(input_string)
                    result = "Accepted" if is_accepted else "Rejected"
                    print(f"String '{input_string}': {result}")

            except EOFError:
                break

    except ValueError as e:
        print(f"\nError: {e}", file=sys.stderr)
    except Exception as e:
         print(f"\nAn unexpected error occurred: {e}", file=sys.stderr)

    print("\nExiting.")

if __name__ == "__main__":
    main()