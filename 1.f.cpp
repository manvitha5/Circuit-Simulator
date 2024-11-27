#include <iostream>
#include <vector>
#include <memory>
#include <cmath>
#include <complex>

using namespace std;

const double PI = 3.14159;
using Complex = complex<double>;

// Base class for all circuit elements
class CircuitElement {
public:
    virtual Complex calculateImpedance(double frequency) const = 0;
    virtual void display(int indent = 0) const = 0;
    virtual ~CircuitElement() = default;
};

// Derived class for individual components (Resistor, Capacitor, Inductor)
class Component : public CircuitElement {
    string type;
    double value;

public:
    Component(string t, double v) : type(t), value(v) {}

    Complex calculateImpedance(double frequency) const override {
        if (type == "resistor") {
            return {value, 0};  // Real impedance for resistors
        } else if (type == "capacitor") {
            return {0, -1 / (2 * PI * frequency * value)};  // Imaginary part is negative
        } else if (type == "inductor") {
            return {0, 2 * PI * frequency * value};  // Imaginary part is positive
        }
        return {0, 0};  // Default (invalid type)
    }

    void display(int indent = 0) const override {
        cout << string(indent, ' ') << type << " (" << value;
        if (type == "resistor") cout << " ohms)";
        else if (type == "capacitor") cout << " F)";
        else if (type == "inductor") cout << " H)";
        cout << endl;
    }
};

// Derived class for series and parallel groups
class Group : public CircuitElement {
    string configuration;
    vector<shared_ptr<CircuitElement>> elements;

public:
    Group(string config) : configuration(config) {}

    void addElement(shared_ptr<CircuitElement> element) {
        elements.push_back(element);
    }

    Complex calculateImpedance(double frequency) const override {
        if (configuration == "series") {
            Complex totalImpedance = {0, 0};
            for (const auto& element : elements) {
                totalImpedance += element->calculateImpedance(frequency);
            }
            return totalImpedance;
        } else if (configuration == "parallel") {
            Complex inverseTotal = {0, 0};
            for (const auto& element : elements) {
                Complex impedance = element->calculateImpedance(frequency);
                if (impedance != Complex(0, 0)) {
                    inverseTotal += 1.0 / impedance;
                }
            }
            return inverseTotal != Complex(0, 0) ? 1.0 / inverseTotal : Complex(0, 0);
        }
        return {0, 0};
    }

    void display(int indent = 0) const override {
        cout << string(indent, ' ') << "Configuration: " << configuration << endl;
        for (const auto& element : elements) {
            element->display(indent + 2);
        }
    }
};

// Function to create a circuit by user input
shared_ptr<CircuitElement> createCircuit() {
    cout << "Enter circuit type (series or parallel): ";
    string config;
    cin >> config;

    auto group = make_shared<Group>(config);

    cout << "Enter the number of elements in this group: ";
    int numElements;
    cin >> numElements;

    for (int i = 0; i < numElements; i++) {
        cout << "\nIs this a (c)omponent or a (g)roup? ";
        char choice;
        cin >> choice;

        if (choice == 'c') {
            cout << "Enter component type (resistor, capacitor, or inductor): ";
            string type;
            cin >> type;

            cout << "Enter component value (ohms for resistor, F for capacitor, H for inductor): ";
            double value;
            cin >> value;

            if (type == "resistor" || type == "capacitor" || type == "inductor") {
                group->addElement(make_shared<Component>(type, value));
            } else {
                cout << "Invalid component type, please enter 'resistor', 'capacitor', or 'inductor'." << endl;
                i--;
            }
        } else if (choice == 'g') {
            cout << "\nCreating a nested group:" << endl;
            group->addElement(createCircuit());
        } else {
            cout << "Invalid choice, please enter 'c' for component or 'g' for group." << endl;
            i--;
        }
    }
    return group;
}

int main() {
    cout << "Welcome to the C++ Circuit Simulator!\n";

    double frequency;
    cout << "Enter operating frequency (Hz): ";
    cin >> frequency;

    double voltage;
    cout << "Enter the voltage of the source (V): ";
    cin >> voltage;

    auto circuit = createCircuit();

    cout << "\n--- Circuit Configuration ---\n";
    circuit->display();

    Complex totalImpedance = circuit->calculateImpedance(frequency);
    cout << "\nTotal Impedance of the Circuit at " << frequency << " Hz: " << totalImpedance << " ohms\n";

    Complex totalCurrent = voltage / totalImpedance;
    cout << "Total Current in the Circuit: " << abs(totalCurrent) << " A (magnitude)\n";

    return 0;
}
