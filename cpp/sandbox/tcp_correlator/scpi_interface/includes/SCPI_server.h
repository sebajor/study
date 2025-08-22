#include "TcpServer.h"
#include "apexHoloBackend.h"
#include <vector>
#include <array>
#include <string>
#include <utility>
#include <mutex>
#include <atomic>
#include <thread>


class SCPI_server {
    private:
        std::thread worker;
        std::vector<bool> mask(1<<15, 1);//this should gave 2**15 True mask
        int acc_len {5};
        int dft_size {128};
    public:
        TcpServer cmd_server;
        TcpServer data_server;
        float integ_time = -1;
        //this are the flags used to handle the threads safetly
        std::mutex mut;
        std::atomic<int> data_flag = 0;
        std::atomic<int> alive = 1;
        //
        SCPI_server(std::string_view ip, int cmd_port, int data_port, apexHoloBackend &apex_fpga);
        ~SCPI_server();
        int parse_recv_msg(std::string_view input_data, std::string &out_msg);
        void data_thread();
        
        //methods.. always returns a int that shows if the action was successfull
        //the msg is the received one, the out_msg is the string that will be send to
        
        int set_accumulation(std::string_view msg, std::string &out_msg);
        int get_accumulation(std::string_view msg, std::string &out_msg);
        int set_mask(std::string_view msg, std::string &out_msg);
        int get_mask(std::string_view msg, std::string &out_msg);
        int set_fft_size(std::string_view msg, std::string &out_msg);
        int get_fft_size(std::string_view msg, std::string &out_msg);
        int enable_data_pipeline(std::string_view, std::string &out_msg);
        int disable_data_pipeline(std::string_view, std::string &out_msg);


        //commands and the corresponding methods
        std::vector<std::pair<std::string_view, int(SCPI_server::*)(std::string_view, std::string&)>> cmds {
            {"ATLAST:INTERF:SET_ACC", &SCPI_server::set_accumulation},
            {"ATLAST:INTERF:GET_ACC", &SCPI_server::get_accumulation},
            {"ATLAST:INTERF:SET_MASK", &SCPI_server::set_mask},
            {"ATLAST:INTERF:GET_MASK", &SCPI_server::get_mask},
            {"ATLAST:INTERF:SET_DFT_SIZE", &SCPI_server::set_dft_size},
            {"ATLAST:INTERF:GET_DFT_SIZE", &SCPI_server::get_dft_size},
            {"ATLAST:INTERF:ENABLE_PIPE", &SCPI_server::zuboard_enable_corr},
            {"ATLAST:INTERF:DISABLE_PIPE", &SCPI_server::zuboard_enable_corr},
        };
};
