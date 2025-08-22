#include <string>
#include <vector>
#include <thread>
#include <mutex>
#include <fftw3.h>
#include "../../../tcp_server_multi_client/includes/TcpServer.h"

struct hyperparameters {
    std::string_view ip {"localhost"};
    int port {12334};
    int max_workers {3};
    int accumulation {4};
    int fft_points {4096};
    //parameters for the pluto+
    double LO {1.5};   //GHz
    double BW {30};   //MHz
};


class Correlator{
    private:
        const hyperparameters localparams;
        int recv_len {0};
        std::vector<std::thread> workers;
        std::vector<int> busy;
    public:
        TcpServer data_server;
        std::vector<double> power0, power1, corr_re, corr_im;   //will be initialized with the constructor
        std::vector<double> recv_buffer;
        std::vector<int> sock_index{};
        int recv_size {0};

        std::mutex data_in_mutex;
        std::mutex data_out_mutex;
        int accumulation_counter {0};
        //temporary values for the fftw
        fftw_complex* in0;
        fftw_complex* in1;
        fftw_complex* out0;
        fftw_complex* out1;
        //methods
        Correlator(hyperparameters &params);
        ~Correlator();
        void spectrometer_iteration(int &busy_flag, std::vector<double> &input_data,
                std::vector<double> &power0, std::vector<double> &power1,
                std::vector<double> &corr_re, std::vector<double> &corr_im);
        int run();
        void sendData();
};

