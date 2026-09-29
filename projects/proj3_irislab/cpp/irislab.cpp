#include "irislab.hpp"

#include <cmath>

namespace irislab {

double delta_e(
    double l1,
    double a1,
    double b1,
    double l2,
    double a2,
    double b2
) {
    const double delta_l = l1 - l2;
    const double delta_a = a1 - a2;
    const double delta_b = b1 - b2;

    return std::sqrt(
        delta_l * delta_l
        + delta_a * delta_a
        + delta_b * delta_b
    );
}

}  // namespace irislab