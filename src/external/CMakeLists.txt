cmake_minimum_required(VERSION 2.8)
set(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake)
find_package(SWIG 2.0.7 REQUIRED)
find_package(PythonInterp)
find_package(PythonLibs)
include(${SWIG_USE_FILE})

find_package(Eigen3 REQUIRED)
find_package(Bogus REQUIRED)
find_package(FCLIB REQUIRED)
find_package(MPI REQUIRED)
find_package(SiconosNumerics REQUIRED)
add_library(bogus_interface SHARED bogus_interface.cpp)
include_directories(${EIGEN3_INCLUDE_DIR} ${Bogus_INCLUDE_DIRS} ${FCLIB_INCLUDE_DIRS} ${PYTHON_INCLUDE_DIR} ${CMAKE_SOURCE_DIR} ${SiconosNumerics_INCLUDE_DIRS})

foreach(_D ${MPI_CXX_INCLUDE_PATH})
  include_directories(${_D})
endforeach()

target_link_libraries(bogus_interface ${Bogus_LIBRARY} ${Eigen3_LIBRARIES} ${FCLIB_LIBRARIES} ${SiconosNumerics_LIBRARIES} ${MPI_LIBRARIES})
set_source_files_properties(bogus_interface.i PROPERTIES CPLUSPLUS ON)
set_source_files_properties(FCLib.i PROPERTIES CPLUSPLUS ON)
swig_add_module(BogusInterface python bogus_interface.i)
swig_add_module(FCLib python FCLib.i)

swig_link_libraries(BogusInterface ${PYTHON_LIBRARIES} ${Bogus_LIBRARY} ${Eigen3_LIBRARIES} ${FCLIB_LIBRARIES} bogus_interface) 
swig_link_libraries(FCLib ${PYTHON_LIBRARIES} ${FCLIB_LIBRARIES} ) 

