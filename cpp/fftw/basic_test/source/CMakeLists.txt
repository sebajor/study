cmake_minimum_required(VERSION 3.13)
project(fftw_test)

add_executable(${PROJECT_NAME} main.cpp)

find_library(fft_lib fftw3) 
if(${fft_lib})
    message("No library ffftw3 found!")
else()
    message("fftw3 lib found as ${fft_lib}")
endif()

target_link_libraries(${PROJECT_NAME} ${fft_lib})


