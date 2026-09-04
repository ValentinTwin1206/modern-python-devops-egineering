#include "heisenblue.hpp"

#include <pybind11/pybind11.h>

namespace py = pybind11;

PYBIND11_MODULE(_native, module) {
    module.doc() = "Native Blue Score calculations for HeisenBlue.";
    module.def(
        "calculate_blue_score",
        &heisenblue::calculate_blue_score,
        py::arg("molecular_weight"),
        py::arg("aromatic_rings"),
        py::arg("heavy_atoms"),
        py::arg("hetero_atoms"),
        py::arg("rotatable_bonds")
    );
}
