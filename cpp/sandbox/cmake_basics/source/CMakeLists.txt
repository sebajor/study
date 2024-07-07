cmake_minimum_required(VERSION 3.10.0)


#project name
project(CMAKE_test)

##this is to search if a library exists (we dont use it here, but is good to know
find_library(test_lib glew) ##It will search for libglew.so or .a
if(${test_lib})
    message("No library glew found!")
else()
    message("glew lib found as ${test_lib}")
endif()


## this will generate the executable
add_executable(${PROJECT_NAME} main.cpp)

##after creating the makefile if you run make install it will put the excutable at usr/local/bin :O
install(TARGETS ${PROJECT_NAME} DESTINATION bin)

