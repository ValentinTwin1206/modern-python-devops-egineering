#pragma once

namespace heisenblue {

double calculate_blue_score(
    double molecular_weight,
    int aromatic_rings,
    int heavy_atoms,
    int hetero_atoms,
    int rotatable_bonds
);

}  // namespace heisenblue