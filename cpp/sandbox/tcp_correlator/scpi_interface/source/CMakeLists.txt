cmake_minimum_required(VERSION 3.13)
project(holo_server)

##include dir
include_directories(${CMAKE_SOURCE_DIR}i/../includes/)

add_executable(${PROJECT_NAME} 
    main.cpp
    TcpSocket.cpp
    SCPI_server.cpp
    TcpServer.cpp
    apexHoloBackend.cpp
)



