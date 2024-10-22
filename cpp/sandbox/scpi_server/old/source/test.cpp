#include "SCPI_server.cpp"
#include <string>
#include <iostream>


std::string_view ip {"localhost"};
int port = 1234;


int main(){
    std::vector<char> recv_buffer {};
    int recv_len = 0;

    SCPI_server server(ip, port);
    std::cout << "waiting client \n";
    int client = server.AddClient();
    std::cout << "client joined\n";
    while(1){


    }
    return 1;
}

