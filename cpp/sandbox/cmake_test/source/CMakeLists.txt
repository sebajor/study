cmake_minimum_required(VERSION 3.10.0)


#project name
project(CMAKE_test)

## this will generate the executable
add_executable(${PROJECT_NAME} main.cpp)

##after creating the makefile if you run make install it will put the excutable at /bin :O
install(TARGETS ${PROJECT_NAME} DESTINATION bin)

