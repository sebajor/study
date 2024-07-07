cmake_minimum_required(VERSION 3.13)
project(cmake_lib_usage)

add_executable(${PROJECT_NAME} main.cpp)
#As this is a user created lib, I need to tell it where to find it
target_link_directories(${PROJECT_NAME} PRIVATE ${CMAKE_SOURCE_DIR}/../../lib_create/build/)

##this tells cmake what are the libraries we want to use (in our case we create cmake_libs
target_link_libraries(${PROJECT_NAME} cmake_libs)


