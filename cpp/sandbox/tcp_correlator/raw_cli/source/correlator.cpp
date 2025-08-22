#include "../includes/correlator.h"
#include <vector>
#include <string>
#include <iostream>
#include <fftw3.h>
#include <mutex>



Correlator::Correlator(hyperparameters &params)
    : localparams(params), data_server(params.ip, params.port)
{
    //this->localparams = params;
    this->recv_len = 2*params.fft_points*sizeof(double);    //I receive two streams of data
    this->power0.resize(params.fft_points);
    this->power1.resize(params.fft_points);
    this->corr_re.resize(params.fft_points);
    this->corr_im.resize(params.fft_points);
    this->recv_buffer.resize(2*params.fft_points);

    this->in0 = (fftw_complex*) fftw_malloc(sizeof(fftw_complex)*params.fft_points);
    this->in1 = (fftw_complex*) fftw_malloc(sizeof(fftw_complex)*params.fft_points);
    this->out0 = (fftw_complex*) fftw_malloc(sizeof(fftw_complex)*params.fft_points);
    this->out1 = (fftw_complex*) fftw_malloc(sizeof(fftw_complex)*params.fft_points);
    //initialize the vectors with zeros
    for(int i=0; i<params.fft_points; ++i){
        power0[i] = 0;
        power1[i] = 0;
        corr_re[i] = 0;
        corr_im[i] = 0;
    }
}

Correlator::~Correlator(){
    //here I should join all the launched threads
    std::unique_lock<std::mutex> din_lock(this->data_in_mutex, std::defer_lock);
    din_lock.lock();
    free(in0);
    free(in1);
    free(out0);
    free(out1);
    din_lock.unlock();
}

void Correlator::spectrometer_iteration(int &busy_flag, std::vector<double> &input_data,
        std::vector<double> &power0, std::vector<double> &power1,
        std::vector<double> &corr_re, std::vector<double> &corr_im){
    std::unique_lock<std::mutex> din_lock(this->data_in_mutex, std::defer_lock);
    std::unique_lock<std::mutex> dout_lock(this->data_out_mutex, std::defer_lock);
    //copy the data
    din_lock.lock();
    fftw_plan p0;
    fftw_plan p1;
    //Change this part accordingly!!
    for(int i=0; i<this->localparams.fft_points; ++i){
        this->in0[i][0] = input_data[2*i];
        this->in0[i][1] = 0;
        this->in1[i][0] = input_data[2*i+1];
        this->in1[i][1] = 0;
    }
    din_lock.unlock();
    p0 = fftw_plan_dft_1d(this->localparams.fft_points, in0, out0, FFTW_FORWARD, FFTW_ESTIMATE);
    p1 = fftw_plan_dft_1d(this->localparams.fft_points, in1, out1, FFTW_FORWARD, FFTW_ESTIMATE);
    fftw_execute(p0);
    fftw_execute(p1);
    dout_lock.lock();
    for(int i=0; i<this->localparams.fft_points; ++i){
        power0[i] += out0[i][0]*out0[i][0]+out0[i][1]*out0[i][1];
        power1[i] += out1[i][0]*out1[i][0]+out1[i][1]*out1[i][1];
        //(a+ib)*(c-id) = ((ac+bd)+i(bc-ad))
        corr_re[i] += out0[i][0]*out1[i][0]+out0[i][1]*out1[i][1];
        corr_im[i] += out0[i][1]*out1[i][0]-out0[i][0]*out1[i][1];
    }
    this->accumulation_counter +=1;
    busy_flag = 0;
    dout_lock.unlock();
    fftw_destroy_plan(p0);
    fftw_destroy_plan(p1);
    fftw_cleanup();
}

void Correlator::sendData(){
    //std::cout << "acc value:" << this->accumulation_counter<<"\n";
    if((this->accumulation_counter)== (this->localparams.accumulation)){
        //dirty trick to send data to all sockets
        for(int j=0; j<(this->data_server.fds.size()); ++j){
            if(this->data_server.fds[j].fd != this->data_server.server_sock){
                std::cout << "sending data..\n";
                this->data_server.sendSocketData<double>(this->power0, j);
                this->data_server.sendSocketData<double>(this->power1, j);
                this->data_server.sendSocketData<double>(this->corr_re,j);
                this->data_server.sendSocketData<double>(this->corr_im,j);
            }
        }
        std::cout << "cleaning containers.. ";
        for(int j=0; j<this->power0.size(); ++j){
            this->power0[j] =0;
            this->power1[j] =0;
            this->corr_re[j] =0;
            this->corr_im[j] =0;
        }
        std::cout << "done\n";
        this->accumulation_counter =0;
    }
}


int Correlator::run(){
    std::unique_lock<std::mutex> din_lock(this->data_in_mutex, std::defer_lock);
    std::unique_lock<std::mutex> dout_lock(this->data_out_mutex, std::defer_lock);
    while(1){
        this->data_server.checkClientAvailable(sock_index, 10); //if -1 its blocking
        for(int i=this->sock_index.size()-1; i>-1; --i){
            din_lock.lock();
            //here I got a problem... if the recv data is to big then the socket just got 
            //some portion of the data (we need to iterate to get the full input data)
            //when using the IIO this should not be a problem, I guess....
            this->recv_size = this->data_server.recvSocketData<double>(this->recv_buffer,
                    this->recv_len, this->sock_index[i]);
            din_lock.unlock();
            std::cout << "recv size"<<this->recv_size << "\trecv_len:"<< this->recv_len <<"\n";
            if(this->recv_size ==0){
                std::cout << "deleted socket at "<<i<< "\n";
                continue;
            }
            //first we check if we have data ready to be sent
            dout_lock.lock();
            this->sendData();
            dout_lock.unlock();
            //now we chekc if there are some workers
            if(this->workers.size()<this->localparams.max_workers){
                this->busy.emplace_back(1);
                //by default the damn threads make copies even if I defined with a pass ref >:(
                workers.push_back(std::thread(
                            &Correlator::spectrometer_iteration,
                            this,
                            std::ref(this->busy[workers.size()]),
                            std::ref(this->recv_buffer),
                            std::ref(this->power0),
                            std::ref(this->power1),
                            std::ref(this->corr_re),
                            std::ref(this->corr_im)
                            )
                        );
            }
            else{
                std::cout << "Max thread number exceded\n";
            }
        }
        dout_lock.lock();
        this->sendData();
        dout_lock.unlock();

        //here I must check if there are threads dead
        for(int j=this->workers.size()-1; j>-1; --j){
            std::cout << "cleaing threads:"<<j<<"\n";
            if(~this->busy[j] & this->workers[j].joinable()){
                std::cout << "joining thread" << j <<"\n";
                this->workers[j].join();
                this->workers.erase(this->workers.begin()+j);
                this->busy.erase(this->busy.begin()+j);
            }
        }
    }
    return 1;
}




