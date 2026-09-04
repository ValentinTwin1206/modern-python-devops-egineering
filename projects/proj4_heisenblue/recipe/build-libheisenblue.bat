setlocal EnableDelayedExpansion

mkdir build-libheisenblue
cd build-libheisenblue

cmake "%SRC_DIR%\cpp" ^
    -G Ninja ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DCMAKE_INSTALL_PREFIX="%LIBRARY_PREFIX%"
if errorlevel 1 exit 1

cmake --build . --target heisenblue --config Release
if errorlevel 1 exit 1

cmake --install .
if errorlevel 1 exit 1
