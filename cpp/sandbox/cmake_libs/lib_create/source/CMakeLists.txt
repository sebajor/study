cmake_minimum_required(VERSION 3.10.0)
project(cmake_libs)

##this tells cmake that we want a library
add_library(${PROJECT_NAME} adder.cpp)

##tells what are the headers that the scripts uses
set_target_properties(${PROJECT_NAME} PROPERTIES PUBLIC_HEADER adder.h)

##where to install the library and the headers
install(TARGETS ${PROJECT_NAME} LIBRARY DESTINATION lib
        PUBLIC_HEADER DESTINATION include/${PROJECT_NAME}
        )
