#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <iostream>
#include <vector>
#include <omp.h>

namespace py = pybind11;

// Function to check if adding vertex v to set is safe or not
bool isSafe(int v, const std::vector<int>& set, const std::vector<std::vector<int>>& adj) {
    for (int i = 0; i < set.size(); i++) {
        if (adj[v][set[i]]) {
            return false;
        }
    }
    return true;
}

void findLargestSet(int index, int n, std::vector<int>& set, std::vector<int>& bestSet, const std::vector<std::vector<int>>& adj) {
    if (index == n) {
        if (set.size() > bestSet.size()) {
            bestSet = set;  // Update the best set found
        }
        return;
    }

    findLargestSet(index + 1, n, set, bestSet, adj);

    if (isSafe(index, set, adj)) {
        set.push_back(index);
        findLargestSet(index + 1, n, set, bestSet, adj);
        set.pop_back();
    }
}

std::vector<int> getIndependenceGraphVertices(const std::vector<std::vector<int>>& adj) {
    std::vector<int> bestSet;

    #pragma omp parallel
    {
        std::vector<int> localBestSet;
        std::vector<int> localSet;

        #pragma omp for
        for (int i = 0; i < adj.size(); i++) {
            localSet.clear();
            findLargestSet(i, adj.size(), localSet, localBestSet, adj);

            #pragma omp critical
            {
                if (localBestSet.size() > bestSet.size()) {
                    bestSet = localBestSet;
                }
            }
        }
    }

    return bestSet;
}

PYBIND11_MODULE(independence_graph, m) {
    m.def("get_independence_graph_vertices", &getIndependenceGraphVertices, "Get vertices in the largest independent set", py::arg("adj"));
}
