#pragma once

#if defined(_WIN32) || defined(__CYGWIN__)
    #if defined(REDSTICKS_BUILD_SHARED)
        #define REDSTICKS_API __declspec(dllexport)
    #else
        #define REDSTICKS_API __declspec(dllimport)
    #endif
#else
    #define REDSTICKS_API __attribute__((visibility("default")))
#endif

namespace redsticks {

/// Score how well a lipstick shade harmonizes with an eye color.
///
/// Both colors are given as sRGB channels in the range [0, 255]. The score
/// is computed in CIELAB/LCh space from complementary-hue proximity, a
/// chroma bonus, and a lightness-clash penalty, and is clamped to [0, 100].
REDSTICKS_API double harmony_score(
    double eye_r,
    double eye_g,
    double eye_b,
    double shade_r,
    double shade_g,
    double shade_b
);

}  // namespace redsticks
