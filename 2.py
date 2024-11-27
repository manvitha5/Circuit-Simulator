from sympy import symbols, Matrix,inverse_laplace_transform, simplify
from sympy.abc import t

def take_circuit_input():
    """
    Function to take user input for the circuit components and connections.
    Returns a list of components and the number of nodes.
    """
    print("Enter the number of nodes (including ground as Node 0):")
    n = int(input("Number of nodes: "))

    components = []
    print("\nEnter the circuit components and their connections:")
    print("Format: [Component_Type] [Value] [Node1] [Node2]")
    print("Examples: R 4 1 2  (Resistor 4Ω between Node 1 and Node 2)")
    print("          C 0.25 1 0  (Capacitor 0.25F between Node 1 and Ground)")
    print("          V 5 2 0  (Voltage Source 5V between Node 2 and Ground)")

    while True:
        inp = input("Enter component (or type 'done' to finish): ").strip()
        if inp.lower() == "done":
            break
        parts = inp.split()
        if len(parts) != 4:
            print("Invalid format. Please enter [Type] [Value] [Node1] [Node2].")
            continue
        comp_type, value, node1, node2 = parts
        components.append({
            "type": comp_type.upper(),
            "value": float(value),
            "node1": int(node1),
            "node2": int(node2)
        })

    return n, components


def build_impedance_matrix(n, components):
    """
    Builds the impedance matrix based on the circuit components and connections.
    Returns the impedance matrix (Z) and voltage vector (V).
    """
    s = symbols('s')  # Laplace variable
    Z = Matrix.zeros(n, n)  # Initialize impedance matrix
    V = Matrix.zeros(n, 1)  # Initialize voltage source vector

    for comp in components:
        comp_type = comp["type"]
        value = comp["value"]
        node1 = comp["node1"]
        node2 = comp["node2"]

        # Define component impedance
        if comp_type == "R":
            impedance = value
        elif comp_type == "L":
            impedance = s * value
        elif comp_type == "C":
            impedance = 1 / (s * value)
        elif comp_type == "V":
            # Voltage source directly affects the voltage vector
            if node1 > 0:
                V[node1, 0] += value
            if node2 > 0:
                V[node2, 0] -= value
            continue
        else:
            print(f"Unknown component type: {comp_type}")
            continue

        # Add impedance to the matrix
        if node1 > 0:
            Z[node1, node1] += 1 / impedance
        if node2 > 0:
            Z[node2, node2] += 1 / impedance
        if node1 > 0 and node2 > 0:
            Z[node1, node2] -= 1 / impedance
            Z[node2, node1] -= 1 / impedance

    # Add a small resistance to ground to prevent singular matrix
    Z[0, 0] = 1e-6  # Tiny resistance at ground (Node 0)

    return Z, V


def solve_circuit():
    """
    Solves the circuit using the impedance matrix method and user input.
    Converts the node voltages from the s-domain to the time domain.
    """
    print("Welcome to the Circuit Solver!")
    n, components = take_circuit_input()

    print("\nBuilding impedance matrix...")
    Z, V = build_impedance_matrix(n, components)
    print("Impedance Matrix (Z):")
    print(Z)
    print("Voltage Vector (V):")
    print(V)

    print("\nChecking if matrix is invertible...")
    determinant = Z.det()
    if determinant == 0:
        print("Matrix inversion failed: Matrix det == 0; not invertible.")
        print("The circuit might be singular (e.g., short circuit, improper grounding, or redundant connections).")
        return

    print("\nSolving for node voltages in the s-domain...")
    node_voltages_s = Z.inv() * V
    print("Node Voltages in the s-domain:")
    for i, voltage in enumerate(node_voltages_s):
        print(f"Node {i}: {simplify(voltage)}")

    print("\nConverting node voltages to the time domain using inverse Laplace transform...")
    node_voltages_t = []
    for v in node_voltages_s:
        v_time = simplify(inverse_laplace_transform(v, symbols('s'), t))
        v_time_clean = v_time.replace(DiracDelta(t), 0)  # Remove DiracDelta if present
        node_voltages_t.append(v_time_clean)

    print("Node Voltages in the time domain:")
    for i, voltage in enumerate(node_voltages_t):
        print(f"Node {i}: {voltage}")


if _name_ == "_main_":
    solve_circuit()