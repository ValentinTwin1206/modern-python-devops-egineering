cmake_minimum_required(VERSION 3.18)

project(libredsticks LANGUAGES CXX VERSION 1.0.0)

include(GNUInstallDirs)

set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_VISIBILITY_INLINES_HIDDEN ON)

# ---------------------------------------------------------------------------
# Build mode selection.
#
# Library mode (default): build the standalone shared library libredsticks
# and install its headers. Used by the `libredsticks` Conda output.
#
# Bindings mode (-DREDSTICKS_BUILD_BINDINGS=ON): ONLY build the pybind11
# extension `_native` and link it against a pre-installed libredsticks
# (e.g. from the `libredsticks` Conda package). Used by the
# `redsticks-tools` Conda output and for local development builds.
# ---------------------------------------------------------------------------

option(REDSTICKS_BUILD_BINDINGS "Build the pybind11 extension instead of the shared library" OFF)

if(NOT REDSTICKS_BUILD_BINDINGS)
    add_library(redsticks SHARED redsticks.cpp)
    add_library(redsticks::redsticks ALIAS redsticks)

    target_include_directories(redsticks
        PUBLIC
            $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
            $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
    )
    target_compile_features(redsticks PUBLIC cxx_std_17)
    target_compile_definitions(redsticks PRIVATE REDSTICKS_BUILD_SHARED)

    set_target_properties(redsticks PROPERTIES
        OUTPUT_NAME redsticks
        VERSION ${PROJECT_VERSION}
        SOVERSION ${PROJECT_VERSION_MAJOR}
    )

    if(MSVC)
        target_compile_options(redsticks PRIVATE /W4 /permissive-)
    else()
        target_compile_options(redsticks PRIVATE -Wall -Wextra -Wpedantic)
    endif()

    install(TARGETS redsticks
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    )
    install(FILES redsticks.hpp DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
else()
    find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
    find_package(pybind11 CONFIG REQUIRED)

    # Prefer a pre-installed libredsticks (Conda host prefix). Fall back to
    # compiling the library sources directly into the extension for local
    # development builds outside Conda.
    find_library(REDSTICKS_LIB NAMES redsticks)
    find_path(REDSTICKS_INCLUDE_DIR NAMES redsticks.hpp)

    if(REDSTICKS_LIB AND REDSTICKS_INCLUDE_DIR)
        pybind11_add_module(_native MODULE bindings.cpp)
        target_include_directories(_native PRIVATE ${REDSTICKS_INCLUDE_DIR})
        target_link_libraries(_native PRIVATE ${REDSTICKS_LIB})
    else()
        message(STATUS "libredsticks not found; embedding redsticks.cpp into _native")
        pybind11_add_module(_native MODULE bindings.cpp redsticks.cpp)
        target_include_directories(_native PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
        target_compile_definitions(_native PRIVATE REDSTICKS_BUILD_SHARED)
    endif()
    target_compile_features(_native PRIVATE cxx_std_17)

    if(MSVC)
        target_compile_options(_native PRIVATE /W4 /permissive-)
    else()
        target_compile_options(_native PRIVATE -Wall -Wextra -Wpedantic)
    endif()

    install(TARGETS _native
        LIBRARY DESTINATION redsticks
        RUNTIME DESTINATION redsticks
    )
endif()
