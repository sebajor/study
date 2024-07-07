
cmake_minimum_required(VERSION 3.13)
project(cmake_test)

##include dir
include_directories(${CMAKE_SOURCE_DIR}/../includes/)

add_executable(${PROJECT_NAME} 
    main.cpp
    lib_test.cpp    
)


