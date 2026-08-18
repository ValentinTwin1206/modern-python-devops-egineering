#pragma once

#if defined(_WIN32) || defined(__CYGWIN__)
    #if defined(HEISENBLUE_BUILD_SHARED)
        #define HEISENBLUE_API __declspec(dllexport)
    #else
        #define HEISENBLUE_API __declspec(dllimport)
    #endif
#else
    #define HEISENBLUE_API __attribute__((visibility("default")))
#endif

namespace heisenblue {

HEISENBLUE_API double calculate_blue_score(
    double molecular_weight,
    int aromatic_rings,
    int heavy_atoms,
    int hetero_atoms,
    int rotatable_bonds
);

}  // namespace heisenblue
