#include <iostream>
#include <vector>
#include <string>

using namespace std;

// Edge structure
struct Edge {
    int startNode, endNode;  // Nodes
    string type;            // Component type
    double value;           // Component value
};

// Input edges
void inputSeriesParallel(vector<Edge>& edges) {
    int numGroups;
    cout << "Enter number of groups: ";
    cin >> numGroups;

    for (int i = 0; i < numGroups; i++) {
        cout << "\n(s)eries or (p)arallel: ";
        char groupType;
        cin >> groupType;

        int groupSize;
        cout << "Enter group size: ";
        cin >> groupSize;

        cout << "Enter components (start node, end node, type, value):\n";
        for (int j = 0; j < groupSize; j++) {
            Edge edge;
            cin >> edge.startNode >> edge.endNode >> edge.type >> edge.value;

            // Handle parallel
            if (groupType == 'p' || groupType == 'P') {
                edge.startNode = edges.size();
                edge.endNode = edges.size() + 1;
            }

            edges.push_back(edge);
        }
    }
}

// Build incidence matrix
void buildIncidenceMatrix(const vector<Edge>& edges, int numNodes, vector<vector<int>>& incidenceMatrix) {
    incidenceMatrix.assign(numNodes, vector<int>(edges.size(), 0));

    for (size_t i = 0; i < edges.size(); i++) {
        incidenceMatrix[edges[i].startNode][i] = 1;  // Start node
        incidenceMatrix[edges[i].endNode][i] = -1;  // End node
    }
}

// Tie-set matrix
void calculateTieSetMatrix(const vector<Edge>& edges, int numNodes, vector<vector<int>>& tieSetMatrix) {
    int numLoops = edges.size() - (numNodes - 1);  // Loops
    if (numLoops <= 0) return;

    tieSetMatrix.assign(numLoops, vector<int>(edges.size(), 0));

    for (int i = 0; i < numLoops; i++) {
        tieSetMatrix[i][i] = 1;  // Trivial loops
    }

    cout << "Tie-Set Matrix:\n";
    for (const auto& row : tieSetMatrix) {
        for (int val : row) cout << val << " ";
        cout << endl;
    }
}

// Cut-set matrix
void calculateCutSetMatrix(const vector<Edge>& edges, int numNodes, vector<vector<int>>& cutSetMatrix) {
    cutSetMatrix.assign(numNodes - 1, vector<int>(edges.size(), 0));

    for (int i = 0; i < numNodes - 1; i++) {
        cutSetMatrix[i][i] = 1;  // Trivial cuts
    }

    cout << "Cut-Set Matrix:\n";
    for (const auto& row : cutSetMatrix) {
        for (int val : row) cout << val << " ";
        cout << endl;
    }
}

int main() {
    vector<Edge> edges;      // Components
    int numNodes;            // Nodes

    cout << "Circuit Calculator\n";

    // Input components
    inputSeriesParallel(edges);

    cout << "Enter total nodes: ";
    cin >> numNodes;

    // Incidence matrix
    vector<vector<int>> incidenceMatrix;
    buildIncidenceMatrix(edges, numNodes, incidenceMatrix);

    cout << "\n--- Incidence Matrix ---\n";
    for (const auto& row : incidenceMatrix) {
        for (int val : row) cout << val << " ";
        cout << endl;
    }

    // Display components
    cout << "\n--- Components ---\n";
    for (size_t i = 0; i < edges.size(); i++) {
        cout << "Edge " << i + 1 << ": " << edges[i].type << " (" << edges[i].value;
        if (edges[i].type == "resistor") cout << " ohms";
        else if (edges[i].type == "capacitor") cout << " F";
        else if (edges[i].type == "inductor") cout << " H";
        cout << ")\n";
    }

    // Tie-set matrix
    vector<vector<int>> tieSetMatrix;
    calculateTieSetMatrix(edges, numNodes, tieSetMatrix);

    // Cut-set matrix
    vector<vector<int>> cutSetMatrix;
    calculateCutSetMatrix(edges, numNodes, cutSetMatrix);

    return 0;
}