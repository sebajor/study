cmake_minimum_required(VERSION 3.25)
project(tcp_server)

include_directories(../includes)

add_executable(${PROJECT_NAME} 
    test.cpp
    TcpSocket.cpp
)



#find_library(log_lib spdlog) 
#if(${log_lib})
#    message("No library spdlog found!")
#else()
#    message("log lib found as ${log_lib}")
#endif()

#target_link_libraries(${PROJECT_NAME} ${log_lib})

