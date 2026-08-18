cmake_minimum_required(VERSION 3.18)

project(libheisenblue LANGUAGES CXX VERSION 1.0.0)

include(GNUInstallDirs)

set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_VISIBILITY_INLINES_HIDDEN ON)

# ---------------------------------------------------------------------------
# Build mode selection.
#
# When driven by scikit-build-core (SKBUILD is defined), we ONLY build the
# pybind11 extension `_native` and link it against a pre-installed
# libheisenblue provided by the `libheisenblue` Conda package.
#
# Otherwise (plain CMake build), we build the standalone shared library
# libheisenblue and install its headers. This is the mode used by the
# `libheisenblue` Conda output.
# ---------------------------------------------------------------------------

if(NOT DEFINED SKBUILD)
    add_library(heisenblue SHARED heisenblue.cpp)
    add_library(heisenblue::heisenblue ALIAS heisenblue)

    target_include_directories(heisenblue
        PUBLIC
            $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
            $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
    )
    target_compile_features(heisenblue PUBLIC cxx_std_17)
    target_compile_definitions(heisenblue PRIVATE HEISENBLUE_BUILD_SHARED)

    set_target_properties(heisenblue PROPERTIES
        OUTPUT_NAME heisenblue
        VERSION ${PROJECT_VERSION}
        SOVERSION ${PROJECT_VERSION_MAJOR}
    )

    if(MSVC)
        target_compile_options(heisenblue PRIVATE /W4 /permissive-)
    else()
        target_compile_options(heisenblue PRIVATE -Wall -Wextra -Wpedantic)
    endif()

    install(TARGETS heisenblue
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    )
    install(FILES heisenblue.hpp DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
else()
    find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
    find_package(pybind11 CONFIG REQUIRED)

    # Locate the pre-installed libheisenblue shared library and headers
    # from the Conda host prefix.
    find_library(HEISENBLUE_LIB
        NAMES heisenblue
        REQUIRED
    )
    find_path(HEISENBLUE_INCLUDE_DIR
        NAMES heisenblue.hpp
        REQUIRED
    )

    pybind11_add_module(_native MODULE bindings.cpp)
    target_include_directories(_native PRIVATE ${HEISENBLUE_INCLUDE_DIR})
    target_link_libraries(_native PRIVATE ${HEISENBLUE_LIB})
    target_compile_features(_native PRIVATE cxx_std_17)

    if(MSVC)
        target_compile_options(_native PRIVATE /W4 /permissive-)
    else()
        target_compile_options(_native PRIVATE -Wall -Wextra -Wpedantic)
    endif()

    install(TARGETS _native
        LIBRARY DESTINATION heisenblue
        RUNTIME DESTINATION heisenblue
    )
endif()
