#include "../includes/SCPI_server.h"
#include <iostream>
#include <string>
#include <limits>
#include <cmath>

SCPI_server::SCPI_server(std::string_view ip, int port): TcpServer(ip, port) {
    //std::cout << this->TcpServer::server_sock;  //this is the way how I access to parents memebers
}

SCPI_server::~SCPI_server(){

}

int SCPI_server::parse_recv_msg(std::string_view input_data, float &arg, std::vector<std::string_view> &scpi_cmds){
    //TODO: this has a bug!! when putting args usign chars it also transform the data to float!
    //first we are going to check the what command is it
    int loc = -1;
    int out_index = -1;
    for(int i=0; i< scpi_cmds.size(); ++i){
        loc = input_data.find(scpi_cmds[i]);
        if((loc!=-1) && (loc<input_data.size())){
            std::cout << "cmd found! \n";
            out_index = i;
            break;
        }
    }
    std::string substr {input_data.substr(cmds[out_index].size())};
    try{
        arg = std::stof(substr);
    }
    catch(std::invalid_argument){
        arg = std::numeric_limits<float>::quiet_NaN();
    }
    std::cout << "out_index "<< out_index<<"\t args "<<arg<< std::endl;
    return out_index;
}

int SCPI_server::SCPI_help(float &args, std::string &msg){
    msg = "SCPI_SEVER:INFO You ask for help, here it is\n";
    return 0;
}

int SCPI_server::SCPI_set_integer(float &args, std::string &msg){
    //first check that the argument is valid
    std::cout << "arg "<< args << "\t nan:"<<  std::numeric_limits<float>::quiet_NaN() << std::endl;
    if(std::isnan(args)){
        msg = "Error in argument!\n";
        return -1;
    }
    std::cout << "set integer value:"<< args << "\n";
    internal_value = static_cast<int>(args);
    msg = "SCPI_SERVER:SET_INTEGER "+std::to_string(internal_value)+"\n";
    return 0;
};

int SCPI_server::SCPI_get_integer(float &args, std::string &msg){
    msg = "SCPI_SERVER:GET_INTEGER "+std::to_string(internal_value)+"\n";
    return 0;
}
