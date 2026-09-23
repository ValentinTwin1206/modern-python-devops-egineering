#include "iriscolor.hpp"

#include <pybind11/pybind11.h>

namespace py = pybind11;

PYBIND11_MODULE(_native, module) {

    module.doc() =
        "Native perceptual color-analysis functions for IrisLab.";

    module.def(
        "delta_e",
        &iriscolor::delta_e,
        py::arg("l1"),
        py::arg("a1"),
        py::arg("b1"),
        py::arg("l2"),
        py::arg("a2"),
        py::arg("b2"),
        R"pbdoc(
            Calculate the CIE76 perceptual color difference.

            Both colors must be supplied as CIELAB L*, a*, b* values.

            A smaller Delta E value represents greater perceptual
            similarity between the two colors.
        )pbdoc"
    );
}