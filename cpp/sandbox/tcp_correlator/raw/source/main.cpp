#include "../../../tcp_server_multi_client/includes/TcpServer.h"
#include <iostream>
#include <vector>
#include <array>
#include <thread>
#include <atomic>
#include <mutex>
#include <fftw3.h>


int port {12334};
std::string_view ip {"localhost"};
int recv_len {128*sizeof(double)};   //this is the maximum allowed fft (its in double size).. everything beneath is ok
                                     //well in this case since I assume interleaved data then is half of it..
int max_samples = recv_len/sizeof(double)/2;    //this its only bcs I take


constexpr int max_workers {2};
std::vector<std::thread> workers;

std::mutex mut;
std::vector<int> busy;

int accumulation = 4;
int acc_counter {0};

void spectrometer_iteration(int &busy_flag, std::vector<double> &input_data,
        std::vector<double> &buffer_power0, std::vector<double> &buffer_power1, 
        std::vector<double> &corr_re, std::vector<double> &corr_im){
    
    //busy_flag =1;
    std::unique_lock<std::mutex> lock(mut, std::defer_lock);  
    lock.lock();
    int N = input_data.size()/2;
    std::cout << "fft size " << N <<"\n";
    fftw_plan p0;
    fftw_plan p1;
    fftw_complex in0[N],in1[N], out0[N], out1[N];
    //here I just take the input data interleaved..
    for(int i=0; i<N; ++i){
        in0[i][0] = input_data[2*i];
        in0[i][1] = 0;
        in1[i][0] = input_data[2*i+1];
        in1[i][1] = 0;
    }
    lock.unlock();
    p0 = fftw_plan_dft_1d(N, in0, out0, FFTW_FORWARD, FFTW_ESTIMATE);
    p1 = fftw_plan_dft_1d(N, in1, out1, FFTW_FORWARD, FFTW_ESTIMATE);
    fftw_execute(p0);
    fftw_execute(p1);
    lock.lock();
    for(int i=0; i<N; ++i){
        buffer_power0[i] += out0[i][0]*out0[i][0]+out0[i][1]*out0[i][1];
        buffer_power1[i] += out1[i][0]*out1[i][0]+out1[i][1]*out1[i][1];
        //(a+ib)*(c-id) = ((ac+bd)+i(bc-ad))
        corr_re[i] += out0[i][0]*out1[i][0]+out0[i][1]*out1[i][1];
        corr_im[i] += out0[i][1]*out1[i][0]-out0[i][0]*out1[i][1];
    }
    acc_counter+=1;
    busy_flag = 0;
    lock.unlock();
    fftw_destroy_plan(p0);
    fftw_destroy_plan(p1);
    fftw_cleanup();
}


int main(){
    std::cout << "creating server\n";
    TcpServer server(ip, port);
    std::vector<int> sock_index {};
    std::vector<double> recv_buffer(recv_len/sizeof(double), 0);
    std::vector<double> out_buffer(recv_len/sizeof(double),0);
    int recv_size {0};
    //the necessary data
    std::vector<double> power0(max_samples);
    std::vector<double> power1(max_samples);
    std::vector<double> corr_re(max_samples);
    std::vector<double> corr_im(max_samples);
    //our lock
    std::unique_lock<std::mutex> lock(mut, std::defer_lock);  

    std::cout << "starting while true loop\n";
    while(1){
        ///THIS SHOULD BE BLOCKING!!
        server.checkClientAvailable(sock_index, 10);
         for(int i=sock_index.size()-1; i>-1; --i){
             lock.lock();
            recv_size = server.recvSocketData<double>(recv_buffer, recv_len, sock_index[i]);
            lock.unlock();
            std::cout << "recv size " << recv_size <<"at "<<i << "\n";
            if(recv_size==0){
                std::cout << "delete socket at "<<i<<"\n";
                continue;
            }
            recv_buffer.resize(recv_size/sizeof(double));
            out_buffer.resize(recv_size/sizeof(double)*2);
            /*
            for(auto element: recv_buffer){
                std::cout << element << "\n";
            }
            */
            //first we check if we reach the accumulation 
            lock.lock();
            if(acc_counter == accumulation){
                //TODO: send to all the connected sockets.. I dont think is necesary..
                server.sendSocketData<double>(power0, sock_index[i]);
                server.sendSocketData<double>(power1, sock_index[i]);
                server.sendSocketData<double>(corr_re, sock_index[i]);
                server.sendSocketData<double>(corr_im, sock_index[i]);
                //now we put all the values at zero once again
                for(int i=0; i<power0.size(); ++i){
                    power0[i] = 0;
                    power1[i] = 0;
                    corr_re[i] = 0;
                    corr_im[i] = 0;
                    acc_counter = 0;
                }
            }
            lock.unlock();

            //now we check if there are workers
            if(workers.size()<max_workers){
                busy.emplace_back(1);
                //by default the threads make copies of hte objects
                workers.push_back(std::thread(
                            spectrometer_iteration,
                            std::ref(busy[workers.size()]),
                            std::ref(recv_buffer),
                            std::ref(power0),
                            std::ref(power1),
                            std::ref(corr_re),
                            std::ref(corr_im)
                            )
                        );
            }
            else
                std::cout << "Max thread numbers created.. lost packet\n";
            //FFT_computation(recv_buffer, out_buffer);
        }

        //just in case...
        lock.lock();
        if(acc_counter == accumulation){
            //TODO: send to all the connected sockets.. I dont think is necesary..
            server.sendSocketData<double>(power0, sock_index[0]);
            server.sendSocketData<double>(power1, sock_index[0]);
            server.sendSocketData<double>(corr_re, sock_index[0]);
            server.sendSocketData<double>(corr_im, sock_index[0]);
            //now we put all the values at zero once again
            for(int i=0; i<power0.size(); ++i){
                power0[i] = 0;
                power1[i] = 0;
                corr_re[i] = 0;
                corr_im[i] = 0;
                acc_counter = 0;
            }
        }
        lock.unlock();
        //here we check to join the threads that are ready
        //std::cout << "check if there is a thread to join\n";
        lock.lock();
        for(int i=workers.size()-1; i>-1; --i){
            if(~busy[i] & workers[i].joinable()){
                std::cout << "joining thread:" << i<< "\n";
                workers[i].join();
                workers.erase(workers.begin()+i);
                busy.erase(busy.begin()+i);
            }
        }
        lock.unlock();
    }

}

