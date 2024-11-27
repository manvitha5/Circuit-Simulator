import tkinter as tk
from tkinter import messagebox, simpledialog
from sympy import symbols, simplify, inverse_laplace_transform, Heaviside, lambdify
import matplotlib.pyplot as plt
import numpy as np
from sympy import DiracDelta, I

# Global variables
components = []  # List of components
connections = []  # List of connections (series or parallel)

# Circuit Component Class
class CircuitComponent:
    def _init_(self, name, value, comp_type):
        self.name = name
        self.value = value
        self.comp_type = comp_type  # 'R', 'L', 'C', 'V', 'I'

# Add component function
def add_component(canvas, name, comp_type, x, y):
    """Adds a component to the circuit and displays it on the canvas."""
    # Ask user for value
    value = simpledialog.askfloat("Input", f"Enter value for {comp_type} {name}:")
    if value is None:
        return
    
    component = CircuitComponent(name, value, comp_type)
    components.append(component)
    
    # Draw component on canvas
    if comp_type in ['R', 'L', 'C']:
        canvas.create_rectangle(x, y, x+50, y+30, fill="lightblue", outline="black")
        canvas.create_text(x+25, y+15, text=f"{comp_type}\n{name}\n{value}", font=("Arial", 8))
    elif comp_type in ['V', 'I']:
        canvas.create_oval(x, y, x+50, y+50, fill="lightgreen", outline="black")
        canvas.create_text(x+25, y+25, text=f"{comp_type}\n{name}\n{value}", font=("Arial", 8))

# Add connection function
def add_connection(type_):
    """Adds a series or parallel connection."""
    if len(components) < 2:
        messagebox.showerror("Error", "You need at least two components to connect!")
        return
    
    connections.append(type_)
    messagebox.showinfo("Connection Added", f"Added {type_} connection between components!")

# Solve circuit
def solve_circuit():
    """Solve the circuit and compute voltages and currents for each component."""
    s, t = symbols('s t')  # Laplace and time variables
    Z = {}  # Impedance dictionary

    # Compute impedance for each component
    for comp in components:
        if comp.comp_type == 'R':
            Z[comp.name] = comp.value
        elif comp.comp_type == 'L':
            Z[comp.name] = s * comp.value
        elif comp.comp_type == 'C':
            Z[comp.name] = 1 / (s * comp.value)
        elif comp.comp_type in ['V', 'I']:
            Z[comp.name] = comp.value  # Source

    # Combine impedances based on connections
    total_impedance = None
    for i, conn in enumerate(connections):
        if conn == 'series':
            if total_impedance is None:
                total_impedance = Z[components[i].name] + Z[components[i + 1].name]
            else:
                total_impedance += Z[components[i + 1].name]
        elif conn == 'parallel':
            if total_impedance is None:
                total_impedance = 1 / (1 / Z[components[i].name] + 1 / Z[components[i + 1].name])
            else:
                total_impedance = 1 / (1 / total_impedance + 1 / Z[components[i + 1].name])

    if not any(comp.comp_type == 'V' for comp in components):
        messagebox.showerror("Error", "You need a voltage source in the circuit!")
        return

    V_source = next(comp for comp in components if comp.comp_type == 'V')
    total_current = V_source.value / total_impedance

    time = np.linspace(0, 5, 500)

    def plot_graph(component_name, voltage_values, current_values):
        """Helper function to plot voltage and current for a given component."""
        plt.figure()
        plt.plot(time, voltage_values, label="Voltage (V)", color="blue")
        plt.plot(time, current_values, label="Current (A)", color="orange")
        plt.title(f"Voltage and Current for {component_name}")
        plt.xlabel("Time (s)")
        plt.ylabel("Value")
        plt.legend()
        plt.grid()
        plt.show()

    # Create graphs for each component
    for comp in components:
        if comp.comp_type in ['R', 'L', 'C']:
            voltage_across = total_current * Z[comp.name]

            # Inverse Laplace Transform
            time_domain_voltage = inverse_laplace_transform(voltage_across, s, t) * Heaviside(t)
            time_domain_current = inverse_laplace_transform(total_current, s, t) * Heaviside(t)

            # Replace DiracDelta in symbolic expressions
            time_domain_voltage = time_domain_voltage.replace(
                lambda x: isinstance(x, DiracDelta), 
                lambda x: 0
            )
            time_domain_current = time_domain_current.replace(
                lambda x: isinstance(x, DiracDelta), 
                lambda x: 0
            )

            # Convert symbolic to numerical functions
            voltage_func = lambdify(t, simplify(time_domain_voltage), 'numpy')
            current_func = lambdify(t, simplify(time_domain_current), 'numpy')

            # Numerical data
            try:
                voltage_values = np.array([voltage_func(t_val) for t_val in time])
                current_values = np.array([current_func(t_val) for t_val in time])
            except Exception as e:
                print(f"Error generating values: {e}")
                messagebox.showerror("Error", f"Failed to generate values for {comp.name}: {e}")
                return

            # Add a button to display the graph for this component
            btn = tk.Button(frame, text=f"Show Graph for {comp.name}",
                            command=lambda v=voltage_values, c=current_values, n=comp.name: plot_graph(n, v, c))
            btn.grid(column=len(components), row=5 + components.index(comp))

# UI setup
root = tk.Tk()
root.title("Circuit Simulator")

# Create canvas for circuit visualization
canvas = tk.Canvas(root, width=600, height=400, bg="white")
canvas.pack()

# Controls
frame = tk.Frame(root)
frame.pack()

tk.Label(frame, text="Add Component").grid(row=0, column=0)
tk.Button(frame, text="Resistor", command=lambda: add_component(canvas, f"R{len(components)+1}", 'R', 50, 50)).grid(row=1, column=0)
tk.Button(frame, text="Inductor", command=lambda: add_component(canvas, f"L{len(components)+1}", 'L', 150, 50)).grid(row=1, column=1)
tk.Button(frame, text="Capacitor", command=lambda: add_component(canvas, f"C{len(components)+1}", 'C', 250, 50)).grid(row=1, column=2)
tk.Button(frame, text="Voltage Source", command=lambda: add_component(canvas, f"V{len(components)+1}", 'V', 350, 50)).grid(row=1, column=3)
tk.Button(frame, text="Current Source", command=lambda: add_component(canvas, f"I{len(components)+1}", 'I', 450, 50)).grid(row=1, column=4)

# Add connections
tk.Label(frame, text="Add Connection").grid(row=2, column=0)
tk.Button(frame, text="Series", command=lambda: add_connection('series')).grid(row=3, column=0)
tk.Button(frame, text="Parallel", command=lambda: add_connection('parallel')).grid(row=3, column=1)

# Solve and Plot
tk.Button(frame, text="Solve Circuit", command=solve_circuit).grid(row=4, column=0)

root.mainloop()