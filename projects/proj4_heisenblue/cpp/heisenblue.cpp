#include "heisenblue.hpp"

#include <algorithm>

namespace {

double clamp_ratio(double value, double upper_bound) {
    if (upper_bound <= 0.0) {
        return 0.0;
    }
    return std::clamp(value / upper_bound, 0.0, 1.0);
}

}  // namespace

namespace heisenblue {

double calculate_blue_score(
    double molecular_weight,
    int aromatic_rings,
    int heavy_atoms,
    int hetero_atoms,
    int rotatable_bonds
) {
    const double weight_component = clamp_ratio(molecular_weight, 400.0) * 35.0;
    const double aromatic_component = clamp_ratio(static_cast<double>(aromatic_rings), 4.0) * 20.0;
    const double heavy_atom_component = clamp_ratio(static_cast<double>(heavy_atoms), 30.0) * 20.0;
    const double hetero_component = clamp_ratio(static_cast<double>(hetero_atoms), 8.0) * 25.0;
    const double flexibility_component = (1.0 - clamp_ratio(static_cast<double>(rotatable_bonds), 10.0)) * 15.0;

    const double score = weight_component + aromatic_component + heavy_atom_component
        + hetero_component + flexibility_component;

    return std::clamp(score, 0.0, 100.0);
}

}  // namespace heisenblue
