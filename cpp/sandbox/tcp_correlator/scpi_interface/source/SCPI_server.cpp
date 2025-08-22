#include "../includes/SCPI_server.h"
#include <iostream>
#include <string>
#include <cstring>
#include <thread>
#include <chrono>

//here I initialize the TcpServer and the internal fpga object to point to the referenced one
SCPI_server::SCPI_server(std::string_view ip, int cmd_port, int data_port,
        apexHoloBackend &apex_fpga)
    : cmd_server(ip, cmd_port), data_server(ip, data_port), fpga(apex_fpga) {
        this->worker = std::thread(&SCPI_server::data_thread, this);
}

SCPI_server::~SCPI_server(){
    this->alive = 0;
    if(this->worker.joinable())
        this->worker.join();

}

void SCPI_server::data_thread(){
    std::vector<int> sock_index {};
    std::vector<char> recv_buffer {0};
    recv_buffer.reserve(128);
    int recv_size {0};
    int64_t stamp {0};
    std::array<uint64_t, 4> read_data;
    
    int send_msg_size = 4;  //we gather this amount to send it
    int msg_words = 0;      //counter to see when send the packet

    while(alive){
        this->data_server.checkClientAvailable(sock_index, 10);
        for(int i=sock_index.size()-1; i>-1; --i){
            //if the recv_size is zero the function internally drop the socket
            recv_size = this->data_server.recvSocketData<char>(recv_buffer, 128,
                                                        sock_index[i]);
        }
        if(this->data_flag){
            try{
                {
                    std::lock_guard<std::mutex> lock(this->mut);
                    if(this->fpga.check_data_available()){
                        this->fpga.get_register_data(read_data);
                        this->fpga.acknowledge_data();
                        stamp = std::chrono::duration_cast<std::chrono::microseconds>(
                                std::chrono::system_clock::now().time_since_epoch()).count();
                        for(int i=0; i<4; ++i){
                            send_msg[i+msg_words*5] = read_data[i];
                        }
                        std::memcpy(&send_msg[4+msg_words*5], &stamp, sizeof(uint64_t));
                        //send_msg[4+msg_words*5] = static_cast<float>(stamp);
                        msg_words+=1;
                        if(msg_words==(send_msg_size)){
                            for(int j=1; j< this->data_server.fds.size(); ++j){
                                this->data_server.sendSocketData<int64_t>(send_msg, j);
                            }
                            msg_words = 0;
                        }
                    }
                }
            }
            catch(const std::exception &e){
                std::cout << "Data thread exception: "<< e.what() << "\n";
            }
        }
    }
}

int SCPI_server::parse_recv_msg(std::string_view input_data, std::string &out_msg){
    /*
     *  See if it found a match with the SCPI commands and execute the function associated
     */
    for(auto& pair: this->cmds){
        if(input_data.find(pair.first) != std::string::npos){
            std::cout << "match! "<< pair.first << "\n";
            int cmd_out = (this->*pair.second)(input_data, out_msg); 
            
            return 1;
        }
    }
    std::cout << "no match\n";
    out_msg.assign("undefined command!\n");
    return -1;
}



int SCPI_server::zuboard_set_acc(std::string_view msg, std::string &out_msg){
    //first we will try to get the argument
    size_t space = msg.find(" ");
    if(space!= std::string_view::npos){
        std::string_view s_arg = msg.substr(space+1);
        try{
            float arg = std::stof(std::string(s_arg));
            std::cout << "setting acc to "<< s_arg << "\n";
            std::lock_guard<std::mutex> lock(this->mut);
            this->fpga.set_accumulation(arg);
            out_msg.assign(std::string(msg.substr(0,space)).append(" OK\n"));
            this->integ_time = this->fpga.accumulation*this->fpga.dft_len/this->adc_clock;
            return 0;
        }
        catch(...){
            std::cout << "ERROR in set accumualtion!\n";
            std::cout << msg << "\n";
            out_msg.assign(std::string(msg.substr(0,space)).append(" ERROR!\n"));
            return 1;
        }
    }
    out_msg.assign(" ERROR!\n");
    return 1;
};

int SCPI_server::zuboard_get_acc(std::string_view msg, std::string &out_msg){
    try{
        std::lock_guard<std::mutex> lock(this->mut);
        out_msg.assign(std::string(msg.substr(0, msg.size()-1))+" "+
            std::to_string(this->fpga.accumulation)+
            " \n");
        return 0;
        }
    catch(...){
            std::cout << "ERROR in getting accumualtion!\n";
            std::cout << msg << "\n";
            out_msg.assign(std::string(msg.substr(0, msg.size()-1)).append(" ERROR!\n"));
            return 1;
    }
};

int SCPI_server::zuboard_set_dft_size(std::string_view msg, std::string &out_msg){
    //try to get the arg
    size_t space = msg.find(" ");
    if(space!= std::string_view::npos){
        std::string_view s_arg = msg.substr(space+1);
        try{
            float arg = std::stof(std::string(s_arg));
            std::cout << "setting dft size to "<< s_arg << "\n";
            std::lock_guard<std::mutex> lock(this->mut);
            this->fpga.set_dft_len(arg);
            out_msg.assign(std::string(msg.substr(0,space)).append(" OK\n"));
            this->integ_time = this->fpga.accumulation*this->fpga.dft_len/this->adc_clock;
            return 0;
        }
        catch(...){
            std::cout << "ERROR in set dft size!\n";
            std::cout << msg << "\n";
            out_msg.assign(std::string(msg.substr(0,space)).append(" ERROR!\n"));
            return 1;
        }
    }
    out_msg.assign(" ERROR!\n");
    return 1;
};


int SCPI_server::zuboard_get_dft_size(std::string_view msg, std::string &out_msg){
    try{
        std::lock_guard<std::mutex> lock(this->mut);
        out_msg.assign(std::string(msg.substr(0, msg.size()-1))+" "+
            std::to_string(this->fpga.dft_len)+
            " \n");
        return 0;
        }
    catch(...){
            std::cout << "ERROR in getting DFT size!\n";
            std::cout << msg << "\n";
            out_msg.assign(std::string(msg.substr(0, msg.size()-1)).append(" ERROR!\n"));
            return 1;
    }
};


int SCPI_server::zuboard_set_twiddle(std::string_view msg, std::string &out_msg){
    //try to get the arg
    size_t space = msg.find(" ");
    if(space!= std::string_view::npos){
        std::string_view s_arg = msg.substr(space+1);
        try{
            float arg = std::stof(std::string(s_arg));
            std::cout << "setting twiddle to "<< s_arg << "\n";
            std::lock_guard<std::mutex> lock(this->mut);
            this->fpga.upload_twiddle_factors(arg, this->fpga.twiddle_point);
            out_msg.assign(std::string(msg.substr(0,space)).append(" OK\n"));
            return 0;
        }
        catch(...){
            std::cout << "ERROR in set the twiddle factor!\n";
            std::cout << msg << "\n";
            out_msg.assign(std::string(msg.substr(0,space)).append(" ERROR!\n"));
            return 1;
        }
    }
    out_msg.assign(" ERROR!\n");
    return 1;
};

int SCPI_server::zuboard_get_twiddle(std::string_view msg, std::string &out_msg){
    try{
        std::lock_guard<std::mutex> lock(this->mut);
        out_msg.assign(std::string(msg.substr(0, msg.size()-1))+" "+
            std::to_string(this->fpga.twiddle_number)+
            " \n");
        return 0;
        }
    catch(...){
            std::cout << "ERROR in getting twiddle factor!\n";
            std::cout << msg << "\n";
            out_msg.assign(std::string(msg.substr(0, msg.size()-1)).append(" ERROR!\n"));
            return 1;
    }
    return 0;
};


int SCPI_server::zuboard_get_snapshot(std::string_view msg, std::string &out_msg){
    try{
        std::lock_guard<std::mutex> lock(this->mut);
        this->fpga.get_snapshot(this->adc0_snapshot, this->adc1_snapshot);
        //now we convert ythe data to strings...
        //this is not ideal bcs 
        std::memcpy((this->adc0_str).data(), (this->adc0_snapshot).data(), (this->adc0_str).size());
        std::memcpy((this->adc1_str).data(), (this->adc1_snapshot).data(), (this->adc1_str).size());
        //now I have to see how to send this over the connection..
        out_msg.assign(std::string(msg)+"ADC0:"+this->adc0_str+" ADC1:"+this->adc1_str+"\n");
        return 0;
    }
    catch(...){
        std::cout << "ERROR in getting snapshot!\n";
        std::cout << msg << "\n";
        out_msg.assign(std::string(msg.substr(0, msg.size()-1)).append(" ERROR!\n"));
        return 1;
    }
};

int SCPI_server::zuboard_enable_corr(std::string_view msg, std::string &out_msg){
    try{
        std::lock_guard<std::mutex> lock(this->mut);
        this->fpga.enable_correlator();
        out_msg.assign(std::string(msg.substr(0, msg.size()-1))+" OK\n");
        return 0;
    }
    catch(...){
            std::cout << "ERROR enabling correaltor factor!\n";
            std::cout << msg << "\n";
            out_msg.assign(std::string(msg.substr(0, msg.size()-1)).append(" ERROR!\n"));
            return 1;
    }
    return 0;
};

int SCPI_server::zuboard_continous_stream(std::string_view msg, std::string &out_msg){
    try{
        std::lock_guard<std::mutex> lock(this->mut);
        if(this->data_flag==0){
            this->fpga.enable_correlator();
            this->data_flag = 1;
        }
        out_msg.assign(std::string(msg.substr(0, msg.size()-1))+" OK\n");
        return 0;
    }
    catch(...){
        std::cout << "Error initializing the continous data stream!\n";
        out_msg.assign(std::string(msg.substr(0, msg.size()-1)).append(" ERROR!\n"));
        return 1;
    }
};

int SCPI_server::zuboard_disable_continous_stream(std::string_view msg, std::string &out_msg){
    try{
        if(this->data_flag==1)
            this->data_flag = 0;
        out_msg.assign(std::string(msg.substr(0, msg.size()-1))+" OK\n");
        return 0;
    }
    catch(...){
        std::cout << "Error ending the continous data stream!\n";
        out_msg.assign(std::string(msg.substr(0, msg.size()-1)).append(" ERROR!\n"));
        return 1;
    }
}


int SCPI_server::zuboard_set_integration_time(std::string_view msg, std::string &out_msg){
    //try to get the arg
    size_t space = msg.find(" ");
    if(space!= std::string_view::npos){
        std::string_view s_arg = msg.substr(space+1);
        try{
            float arg = std::stof(std::string(s_arg));
            std::cout << "setting integration time to "<< s_arg << "\n";
            int acc = static_cast<int>(arg*this->adc_clock/this->fpga.dft_len);
            std::cout << "Using acc len: "<< acc <<"\n";
            std::lock_guard<std::mutex> lock(this->mut);
            this->fpga.set_accumulation(acc);
            out_msg.assign(std::string(msg.substr(0,space)).append(" OK\n"));
            this->integ_time = this->fpga.accumulation*this->fpga.dft_len/this->adc_clock;
            return 0;
        }
        catch(...){
            std::cout << "ERROR in set the integration time!\n";
            std::cout << msg << "\n";
            out_msg.assign(std::string(msg.substr(0,space)).append(" ERROR!\n"));
            return 1;
        }
    }
    out_msg.assign(" ERROR!\n");
    return 1;
};

int SCPI_server::zuboard_get_integration_time(std::string_view msg, std::string &out_msg){
    try{
        std::lock_guard<std::mutex> lock(this->mut);
        out_msg.assign(std::string(msg.substr(0, msg.size()-1))+" "+
            std::to_string(this->integ_time)+
            " \n");
        return 0;
        }
    catch(...){
            std::cout << "ERROR in getting integration time!\n";
            std::cout << msg << "\n";
            out_msg.assign(std::string(msg.substr(0, msg.size()-1)).append(" ERROR!\n"));
            return 1;
    }
    return 1;
};



int SCPI_server::zuboard_get_reg(std::string_view msg, std::string &out_msg){
    return 0;
};




