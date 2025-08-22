#include "../includes/SCPI_server.h"
#include <iostream>
#include <string>


SCPI_server::SCPI_server(std::string_view ip, int port): TcpServer(ip, port){

}

SCPI_server::~SCPI_server(){
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



int SCPI_server::SCPI_help(std::string_view msg, std::string &out_msg){
    std::string_view out = "SCPI_SEVER:INFO You ask for help, here it is\n";
    out_msg = out;
    std::cout << out;
    return 0;
}

int SCPI_server::SCPI_get_integer(std::string_view msg, std::string &out_msg){
    std::string cmd_name = std::string(msg.substr(0, msg.size()-1)).append(" ");
    out_msg = cmd_name+std::to_string(this->internal_value)+"\n";


   // out_msg = std::string(msg.substr(0, msg.size()-1)).append(" ")+std::to_string(this->internal_value);
    return 0;
}

int SCPI_server::SCPI_set_integer(std::string_view msg, std::string &out_msg){
    //first we try to get the argument
    size_t space = msg.find(" ");
    if(space != std::string_view::npos){
        std::string_view s_arg = msg.substr(space+1);
        std::cout << "arg found " << s_arg << "\n";
        //here I set the internal value
        float arg = std::stof(std::string(s_arg)); //HERE I SHOULD HANDLE THE EXCEPTIONS!!!
        this->internal_value = arg;
        std::cout << "internal value=" << this->internal_value << "\n";
        //out_msg = std::string(msg.substr(0, space)).append(" OK\n");
        out_msg.assign(std::string(msg.substr(0,space)).append(" OK\n"));
        return 0;
    }
    out_msg = std::string(msg.substr(0,space)).append(" ERROR\n");
    return -1;
    
}
