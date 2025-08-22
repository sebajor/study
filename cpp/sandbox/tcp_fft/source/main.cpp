#include "../../tcp_server_multi_client/includes/TcpServer.h"
#include <iostream>
#include <vector>
#include <array>
#include <thread>
#include <atomic>
#include <mutex>
#include <fftw3.h>

/*
 *  This sample code just receive data in one port, computes an FFT and sent the result back
 */

int port {12334};
std::string_view ip {"localhost"};
int recv_len {128*8};   //this is the maximum allowed fft.. everything beneath is ok
std::mutex mut;


void FFT_computation(std::vector<double> &input_data, std::vector<double> &out_data){
    int N = input_data.size();
    std::cout << "fft size: "<<N <<"\n";
    fftw_plan p;
    fftw_complex in[N], out[N];

    std::lock_guard<std::mutex> lock(mut);
    for(int i=0; i<N; ++i){
        in[i][0] = input_data[i];
        in[i][1] = 0;
    }
    p = fftw_plan_dft_1d(N, in, out, FFTW_FORWARD, FFTW_ESTIMATE);
    fftw_execute(p);
    //now we put the data in the output data
    for(int i=0; i<N; ++i){
        out_data[2*i] = out[i][0];
        out_data[2*i+1] = out[i][1];
    }
    fftw_destroy_plan(p);
    fftw_cleanup();
}


int main(){
    std::cout << "creating server\n";
    TcpServer server(ip, port);
    std::vector<int> sock_index {};
    std::vector<double> recv_buffer(recv_len, 0);
    std::vector<double> out_buffer(recv_len, 0);
    int recv_size {0};
    
    std::cout << "starting while true\n";
    while(1){
        server.checkClientAvailable(sock_index);
        for(int i=sock_index.size()-1; i>-1; --i){
            recv_size = server.recvSocketData<double>(recv_buffer, recv_len, sock_index[i]);
            std::cout << "recv size " << recv_size <<"\n";
            if(recv_size==0){
                std::cout << "delete socket at "<<i<<"\n";
                continue;
            }
            recv_buffer.resize(recv_size/sizeof(double));
            out_buffer.resize(recv_size/sizeof(double)*2);
            for(auto element: recv_buffer){
                std::cout << element << "\n";
            }
            FFT_computation(recv_buffer, out_buffer);
            for(auto element: out_buffer){
                std::cout << element << "\n";
            }
            server.sendSocketData<double>(out_buffer, sock_index[i]);
        }
    }
}
