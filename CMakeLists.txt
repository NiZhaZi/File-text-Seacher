cmake_minimum_required(VERSION 3.15)
project(TextSearcher NONE)

# Find Python interpreter
find_package(Python3 REQUIRED COMPONENTS Interpreter)

# Source dir
set(SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR}/src)

# Install deps into the active environment used by Python3_EXECUTABLE
add_custom_target(install_deps
  COMMAND ${Python3_EXECUTABLE} -m pip install --upgrade pip
  COMMAND ${Python3_EXECUTABLE} -m pip install -r ${CMAKE_CURRENT_SOURCE_DIR}/requirements.txt
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  COMMENT "Installing Python dependencies (PyInstaller)"
  VERBATIM
)

# Build CLI executable
add_custom_target(build_cli ALL
  COMMAND ${Python3_EXECUTABLE} -m PyInstaller --clean --noconfirm --onefile --console --name TextSearcherCLI ${SRC_DIR}/main.py
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  DEPENDS install_deps
  COMMENT "Building CLI executable with PyInstaller"
  VERBATIM
)

# Build GUI executable
add_custom_target(build_gui ALL
  COMMAND ${Python3_EXECUTABLE} -m PyInstaller --clean --noconfirm --onefile --windowed --name TextSearcherGUI ${SRC_DIR}/gui_app.py
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  DEPENDS install_deps
  COMMENT "Building GUI executable with PyInstaller"
  VERBATIM
)

# Convenience clean target for PyInstaller artifacts
add_custom_target(pyclean
  COMMAND ${CMAKE_COMMAND} -E rm -rf ${CMAKE_CURRENT_BINARY_DIR}/build ${CMAKE_CURRENT_BINARY_DIR}/dist ${CMAKE_CURRENT_BINARY_DIR}/*.spec
  COMMENT "Removing PyInstaller artifacts"
  VERBATIM
)
