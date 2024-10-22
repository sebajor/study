cmake_minimum_required(VERSION 3.25)
project(fft_tcp)

include_directories(../includes
                    ../../tcp_server_multi_client/includes
                    ../../TcpUtils/includes
)

add_executable(${PROJECT_NAME} 
    test.cpp
    ../../tcp_server_multi_client/source/TcpServer.cpp
    ../../TcpUtils/source/TcpSocket.cpp
)

find_library(fft_lib fftw3)
if(${fft_lib})
    message("No library fftw3 found")
else()
    message("fftw3 lib found as ${fft_lib}$")
endif()


target_link_libraries($(PROJECT_NAME) ${fft_lib})
