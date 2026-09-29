cmake_minimum_required(VERSION 3.18)

project(libirislab LANGUAGES CXX VERSION 1.0.0)

include(GNUInstallDirs)

set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_VISIBILITY_INLINES_HIDDEN ON)

# ---------------------------------------------------------------------------
# Build mode selection.
#
# Library mode (default):
#   Build the standalone shared library libirislab and install its public
#   header. Used by the `libirislab` Conda output.
#
# Bindings mode (-DIRISLAB_BUILD_BINDINGS=ON):
#   Build only the pybind11 extension `_native` and link it against a
#   pre-installed libirislab, for example from the `libirislab` Conda
#   package.
#
#   If no installed library is available, the native source is compiled
#   directly into the extension. This is useful for local development.
# ---------------------------------------------------------------------------

option(
    IRISLAB_BUILD_BINDINGS
    "Build the pybind11 extension instead of the shared library"
    OFF
)

if(NOT IRISLAB_BUILD_BINDINGS)

    # -----------------------------------------------------------------------
    # Standalone native library
    # -----------------------------------------------------------------------

    add_library(
        irislab
        SHARED
        irislab.cpp
    )

    add_library(
        irislab::irislab
        ALIAS
        irislab
    )

    target_include_directories(
        irislab
        PUBLIC
            $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
            $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
    )

    target_compile_features(
        irislab
        PUBLIC
        cxx_std_17
    )

    target_compile_definitions(
        irislab
        PRIVATE
        IRISLAB_BUILD_SHARED
    )

    set_target_properties(
        irislab
        PROPERTIES
            OUTPUT_NAME irislab
            VERSION ${PROJECT_VERSION}
            SOVERSION ${PROJECT_VERSION_MAJOR}
    )

    if(MSVC)
        target_compile_options(
            irislab
            PRIVATE
            /W4
            /permissive-
        )
    else()
        target_compile_options(
            irislab
            PRIVATE
            -Wall
            -Wextra
            -Wpedantic
        )
    endif()

    install(
        TARGETS irislab
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    )

    install(
        FILES irislab.hpp
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

    # Prefer an already installed libirislab, typically supplied by the
    # Conda host environment.
    find_library(
        IRISLAB_LIB
        NAMES irislab
    )

    find_path(
        IRISLAB_INCLUDE_DIR
        NAMES irislab.hpp
    )

    if(IRISLAB_LIB AND IRISLAB_INCLUDE_DIR)

        message(
            STATUS
            "Using installed libirislab: ${IRISLAB_LIB}"
        )

        pybind11_add_module(
            _native
            MODULE
            bindings.cpp
        )

        target_include_directories(
            _native
            PRIVATE
            ${IRISLAB_INCLUDE_DIR}
        )

        target_link_libraries(
            _native
            PRIVATE
            ${IRISLAB_LIB}
        )

    else()

        message(
            STATUS
            "libirislab not found; embedding irislab.cpp into _native"
        )

        pybind11_add_module(
            _native
            MODULE
            bindings.cpp
            irislab.cpp
        )

        target_include_directories(
            _native
            PRIVATE
            ${CMAKE_CURRENT_SOURCE_DIR}
        )

        target_compile_definitions(
            _native
            PRIVATE
            IRISLAB_BUILD_SHARED
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