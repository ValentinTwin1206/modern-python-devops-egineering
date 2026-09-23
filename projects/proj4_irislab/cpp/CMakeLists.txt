cmake_minimum_required(VERSION 3.18)

project(libiriscolor LANGUAGES CXX VERSION 1.0.0)

include(GNUInstallDirs)

set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_VISIBILITY_INLINES_HIDDEN ON)

# ---------------------------------------------------------------------------
# Build mode selection.
#
# Library mode (default):
#   Build the standalone shared library libiriscolor and install its public
#   header. Used by the `libiriscolor` Conda output.
#
# Bindings mode (-DIRISCOLOR_BUILD_BINDINGS=ON):
#   Build only the pybind11 extension `_native` and link it against a
#   pre-installed libiriscolor, for example from the `libiriscolor` Conda
#   package.
#
#   If no installed library is available, the native source is compiled
#   directly into the extension. This is useful for local development.
# ---------------------------------------------------------------------------

option(
    IRISCOLOR_BUILD_BINDINGS
    "Build the pybind11 extension instead of the shared library"
    OFF
)

if(NOT IRISCOLOR_BUILD_BINDINGS)

    # -----------------------------------------------------------------------
    # Standalone native library
    # -----------------------------------------------------------------------

    add_library(
        iriscolor
        SHARED
        iriscolor.cpp
    )

    add_library(
        iriscolor::iriscolor
        ALIAS
        iriscolor
    )

    target_include_directories(
        iriscolor
        PUBLIC
            $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
            $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
    )

    target_compile_features(
        iriscolor
        PUBLIC
        cxx_std_17
    )

    target_compile_definitions(
        iriscolor
        PRIVATE
        IRISCOLOR_BUILD_SHARED
    )

    set_target_properties(
        iriscolor
        PROPERTIES
            OUTPUT_NAME iriscolor
            VERSION ${PROJECT_VERSION}
            SOVERSION ${PROJECT_VERSION_MAJOR}
    )

    if(MSVC)
        target_compile_options(
            iriscolor
            PRIVATE
            /W4
            /permissive-
        )
    else()
        target_compile_options(
            iriscolor
            PRIVATE
            -Wall
            -Wextra
            -Wpedantic
        )
    endif()

    install(
        TARGETS iriscolor
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    )

    install(
        FILES iriscolor.hpp
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    )

else()

    # -----------------------------------------------------------------------
    # Python bindings
    # -----------------------------------------------------------------------

    find_package(
        Python
        REQUIRED
        COMPONENTS Interpreter Development.Module
    )

    find_package(
        pybind11
        CONFIG
        REQUIRED
    )

    # Prefer an already installed libiriscolor, typically supplied by the
    # Conda host environment.
    find_library(
        IRISCOLOR_LIB
        NAMES iriscolor
    )

    find_path(
        IRISCOLOR_INCLUDE_DIR
        NAMES iriscolor.hpp
    )

    if(IRISCOLOR_LIB AND IRISCOLOR_INCLUDE_DIR)

        message(
            STATUS
            "Using installed libiriscolor: ${IRISCOLOR_LIB}"
        )

        pybind11_add_module(
            _native
            MODULE
            bindings.cpp
        )

        target_include_directories(
            _native
            PRIVATE
            ${IRISCOLOR_INCLUDE_DIR}
        )

        target_link_libraries(
            _native
            PRIVATE
            ${IRISCOLOR_LIB}
        )

    else()

        message(
            STATUS
            "libiriscolor not found; embedding iriscolor.cpp into _native"
        )

        pybind11_add_module(
            _native
            MODULE
            bindings.cpp
            iriscolor.cpp
        )

        target_include_directories(
            _native
            PRIVATE
            ${CMAKE_CURRENT_SOURCE_DIR}
        )

        target_compile_definitions(
            _native
            PRIVATE
            IRISCOLOR_BUILD_SHARED
        )

    endif()

    target_compile_features(
        _native
        PRIVATE
        cxx_std_17
    )

    if(MSVC)
        target_compile_options(
            _native
            PRIVATE
            /W4
            /permissive-
        )
    else()
        target_compile_options(
            _native
            PRIVATE
            -Wall
            -Wextra
            -Wpedantic
        )
    endif()

    install(
        TARGETS _native
        LIBRARY DESTINATION irislab
        RUNTIME DESTINATION irislab
    )

endif()