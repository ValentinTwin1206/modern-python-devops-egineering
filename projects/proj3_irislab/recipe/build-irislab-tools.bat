@echo off
setlocal EnableDelayedExpansion

cmake -S "%SRC_DIR%\cpp" ^
    -B build-tools ^
    -G Ninja ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DIRISLAB_BUILD_BINDINGS=ON ^
    -DCMAKE_PREFIX_PATH="%LIBRARY_PREFIX%"
if errorlevel 1 exit 1

cmake --build build-tools
if errorlevel 1 exit 1

if not exist "%SP_DIR%\irislab" mkdir "%SP_DIR%\irislab"
copy "%SRC_DIR%\src\irislab\*.py" "%SP_DIR%\irislab\"
if errorlevel 1 exit 1
copy "build-tools\_native*.pyd" "%SP_DIR%\irislab\"
if errorlevel 1 exit 1
