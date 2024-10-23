// Параллельный алгоритм нахождения числа независимости графа

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>  // This header allows automatic conversion for STL containers like std::vector
#include <iostream>
#include <vector>
#include <omp.h>

namespace py = pybind11;

// Function to check if adding vertex v to set is safe or not
bool isSafe(int v, std::vector<int>& set, std::vector<std::vector<int>>& adj) {
    for (int i = 0; i < set.size(); i++) {
        if (adj[v][set[i]]) {
            return false;
        }
    }
    return true;
}

// Recursive function to find the size of the largest independent set
int findLargestSet(int index, int n, std::vector<int>& set, std::vector<std::vector<int>>& adj) {
    if (index == n) {
        return set.size();
    }

    int res = findLargestSet(index + 1, n, set, adj);

    if (isSafe(index, set, adj)) {
        set.push_back(index);
        res = std::max(res, findLargestSet(index + 1, n, set, adj));
        set.pop_back();
    }

    return res;
}

int getIndependenceGraphNumber(std::vector<std::vector<int>> adj) {
    int result = 0;
    #pragma omp parallel
    {
        int localResult = 0;

        #pragma omp for
        for (int i = 0; i < adj.size(); i++) {
            std::vector<int> set;
            localResult = std::max(localResult, findLargestSet(i, adj.size(), set, adj));
        }

        #pragma omp critical
        {
            result = std::max(result, localResult);
        }
    }
    return result;
}

PYBIND11_MODULE(independence_graph, m) {
    m.def("get_independence_graph_number", &getIndependenceGraphNumber, "Get independence graph number", py::arg("adj"));
}
