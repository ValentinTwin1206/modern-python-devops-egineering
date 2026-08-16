cmake_minimum_required(VERSION 3.18)

project(libheisenblue LANGUAGES CXX)

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(_native MODULE heisenblue.cpp)

target_include_directories(_native PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
target_compile_features(_native PRIVATE cxx_std_17)

if(MSVC)
    target_compile_options(_native PRIVATE /W4 /permissive-)
else()
    target_compile_options(_native PRIVATE -Wall -Wextra -Wpedantic)
endif()

install(TARGETS _native
    LIBRARY DESTINATION heisenblue
    RUNTIME DESTINATION heisenblue
    ARCHIVE DESTINATION heisenblue
)