cmake_minimum_required(VERSION 3.25)
project(log_test)

include_directories(../include)
link_directories(../libraries)

add_executable(${PROJECT_NAME} main.cpp)



#find_library(log_lib spdlog) 
#if(${log_lib})
#    message("No library spdlog found!")
#else()
#    message("log lib found as ${log_lib}")
#endif()

#target_link_libraries(${PROJECT_NAME} ${log_lib})

target_compile_definitions(${PROJECT_NAME} PUBLIC SPDLOG_COMPILED_LIB)
target_link_libraries(${PROJECT_NAME} LINK_PUBLIC libspdlog.a)
