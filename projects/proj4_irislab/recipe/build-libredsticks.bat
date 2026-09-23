setlocal EnableDelayedExpansion

mkdir build-libirislab
cd build-libirislab

cmake "%SRC_DIR%\cpp" ^
    -G Ninja ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DCMAKE_INSTALL_PREFIX="%LIBRARY_PREFIX%"
if errorlevel 1 exit 1

cmake --build . --target irislab --config Release
if errorlevel 1 exit 1

cmake --install .
if errorlevel 1 exit 1
