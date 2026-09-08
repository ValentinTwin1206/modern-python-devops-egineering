#include "redsticks.hpp"

#include <pybind11/pybind11.h>

namespace py = pybind11;

PYBIND11_MODULE(_native, module) {
    module.doc() = "Native lipstick-shade harmony scoring for redsticks.";
    module.def(
        "harmony_score",
        &redsticks::harmony_score,
        py::arg("eye_r"),
        py::arg("eye_g"),
        py::arg("eye_b"),
        py::arg("shade_r"),
        py::arg("shade_g"),
        py::arg("shade_b")
    );
}
