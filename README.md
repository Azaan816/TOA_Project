# Regular Grammar Parser

This Python script converts a user-defined **regular grammar** (specifically, a right-linear grammar) into an equivalent **Epsilon Nondeterministic Finite Automaton (ε-NFA)**. It then allows you to test input strings against the constructed NFA to determine if they are accepted by the language defined by the grammar.

## Features

*   **Parses Regular Grammar Rules:** Takes grammar rules defined by the user.
*   **Grammar Validation:** Checks if the provided grammar adheres to the rules of a right-linear grammar and uses only the declared terminals and non-terminals.
*   **Handles Epsilon Productions:** Correctly interprets `epsilon` or `ε` productions.
*   **Constructs ε-NFA:** Builds the corresponding NFA, including states, alphabet, transitions (including epsilon transitions), start state, and accept states.
*   **ε-Closure Calculation:** Efficiently computes epsilon closures using Breadth-First Search (BFS).
*   **String Acceptance Simulation:** Simulates the NFA's behavior on given input strings to check for acceptance.
*   **Interactive Command-Line Interface:** Guides the user through defining the grammar components and testing strings.
*   **Input Validation:** Checks for valid symbols in input strings and warns if they are not part of the NFA's alphabet.

## What is a Regular Grammar?

A regular grammar is a formal grammar that describes a regular language. This script specifically handles **right-linear grammars**, where the production rules are restricted to the following forms:

1.  `A -> aB` (A non-terminal yields a terminal followed by a non-terminal)
2.  `A -> a` (A non-terminal yields a single terminal)
3.  `A -> ε` or `A -> epsilon` (A non-terminal yields the empty string)

Where:
*   `A`, `B` are non-terminal symbols.
*   `a` is a terminal symbol.
*   `ε` represents the empty string.

These grammars are equivalent in expressive power to Finite Automata (NFAs and DFAs).

## How it Works

1.  **Grammar Definition:** The user provides the set of terminal symbols (Σ), non-terminal symbols (V), and the start symbol (S).
2.  **Rule Parsing:** The script parses the grammar rules provided by the user line by line. It validates each rule against the declared symbols and the allowed right-linear format.
3.  **NFA Construction:**
    *   Each non-terminal symbol in the grammar becomes a state in the NFA.
    *   An additional, unique final state (internally named `_FINAL_`) is created.
    *   The start symbol of the grammar becomes the start state of the NFA.
    *   The set of accept states contains only the special `_FINAL_` state.
    *   Grammar rules are translated into NFA transitions:
        *   `A -> aB` creates a transition from state `A` to state `B` on input symbol `a`.
        *   `A -> a` creates a transition from state `A` to the `_FINAL_` state on input symbol `a`.
        *   `A -> epsilon` (or `A -> ε`) creates an epsilon transition (a transition on no input symbol) from state `A` to the `_FINAL_` state.
4.  **ε-Closure Pre-computation:** Before simulation, the epsilon closure for each state is computed and stored. The epsilon closure of a state `q` is the set of all states reachable from `q` by following only epsilon transitions (including `q` itself).
5.  **String Simulation:**
    *   The NFA starts in the epsilon closure of the start state.
    *   For each symbol in the input string, the NFA determines the set of possible next states by:
        *   Finding all states reachable from the current set of states via a transition on the input symbol.
        *   Computing the epsilon closure of this new set of states.
    *   If, after processing the entire string, any of the NFA's current states are accept states, the string is accepted. Otherwise, it's rejected.

## Sample Output
<img src="https://github.com/Azaan816/TOA_Project/blob/main/SampleOutput.jpg"></img>
## Requirements

*   Python 3.x

No external libraries beyond the Python standard library (`collections`, `sys`, `re`) are required.

## Installation

1.  Clone the repository or download the Python script (`.py` file).
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```
    (Replace `your-username/your-repo-name` with the actual repository path)
2.  Alternatively, just save the provided Python code as a `.py` file (e.g., `TOA.py`).

## Usage

Run the script from your terminal:

```bash
python TOA.py
