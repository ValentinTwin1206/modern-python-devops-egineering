#pragma once

#if defined(_WIN32) || defined(__CYGWIN__)
    #if defined(IRISCOLOR_BUILD_SHARED)
        #define IRISCOLOR_API __declspec(dllexport)
    #else
        #define IRISCOLOR_API __declspec(dllimport)
    #endif
#else
    #define IRISCOLOR_API __attribute__((visibility("default")))
#endif

namespace iriscolor {

/// Calculate the CIE76 perceptual color difference between two CIELAB colors.
///
/// Each color is represented by its L*, a*, and b* components. The returned
/// Delta E value is the Euclidean distance between the two colors in CIELAB
/// color space.
///
/// A smaller value indicates greater perceptual similarity.
///
/// This function implements:
///
///     Delta E*ab = sqrt(
///         (L1 - L2)^2
///       + (a1 - a2)^2
///       + (b1 - b2)^2
///     )
///
IRISCOLOR_API double delta_e(
    double l1,
    double a1,
    double b1,
    double l2,
    double a2,
    double b2
);

}  // namespace iriscolor