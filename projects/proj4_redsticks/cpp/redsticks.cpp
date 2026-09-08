#include "redsticks.hpp"

#include <algorithm>
#include <cmath>

namespace {

constexpr double kPi = 3.14159265358979323846;

struct Lab {
    double l;
    double a;
    double b;
};

// Convert one sRGB channel [0, 255] to linear light [0, 1].
double linearize(double channel) {
    const double c = std::clamp(channel / 255.0, 0.0, 1.0);
    return (c <= 0.04045) ? c / 12.92 : std::pow((c + 0.055) / 1.055, 2.4);
}

// CIE XYZ -> Lab component transfer function.
double lab_transfer(double t) {
    constexpr double epsilon = 216.0 / 24389.0;
    constexpr double kappa = 24389.0 / 27.0;
    return (t > epsilon) ? std::cbrt(t) : (kappa * t + 16.0) / 116.0;
}

// Convert an sRGB color [0, 255] per channel to CIELAB (D65 white point).
Lab to_lab(double r, double g, double b) {
    const double rl = linearize(r);
    const double gl = linearize(g);
    const double bl = linearize(b);

    const double x = (0.4124564 * rl + 0.3575761 * gl + 0.1804375 * bl) / 0.95047;
    const double y = 0.2126729 * rl + 0.7151522 * gl + 0.0721750 * bl;
    const double z = (0.0193339 * rl + 0.1191920 * gl + 0.9503041 * bl) / 1.08883;

    const double fx = lab_transfer(x);
    const double fy = lab_transfer(y);
    const double fz = lab_transfer(z);

    return Lab{116.0 * fy - 16.0, 500.0 * (fx - fy), 200.0 * (fy - fz)};
}

// Hue angle of a Lab color in degrees [0, 360).
double hue_degrees(const Lab& lab) {
    const double angle = std::atan2(lab.b, lab.a) * 180.0 / kPi;
    return (angle < 0.0) ? angle + 360.0 : angle;
}

// Chroma (colorfulness) of a Lab color.
double chroma(const Lab& lab) {
    return std::hypot(lab.a, lab.b);
}

}  // namespace

namespace redsticks {

double harmony_score(
    double eye_r,
    double eye_g,
    double eye_b,
    double shade_r,
    double shade_g,
    double shade_b
) {
    const Lab eye = to_lab(eye_r, eye_g, eye_b);
    const Lab shade = to_lab(shade_r, shade_g, shade_b);

    // Complementary-hue proximity: best when the shade sits opposite the
    // eye color on the hue wheel (180 degrees apart).
    double hue_delta = std::fabs(hue_degrees(shade) - hue_degrees(eye));
    if (hue_delta > 180.0) {
        hue_delta = 360.0 - hue_delta;
    }
    const double complement_component = (1.0 - std::fabs(hue_delta - 180.0) / 180.0) * 60.0;

    // Chroma bonus: vivid pigments make stronger statements.
    const double chroma_component = std::clamp(chroma(shade) / 100.0, 0.0, 1.0) * 25.0;

    // Lightness-clash penalty: shade and eye lightness should contrast.
    const double lightness_contrast = std::fabs(shade.l - eye.l) / 100.0;
    const double contrast_component = std::clamp(lightness_contrast, 0.0, 1.0) * 15.0;

    return std::clamp(complement_component + chroma_component + contrast_component, 0.0, 100.0);
}

}  // namespace redsticks
