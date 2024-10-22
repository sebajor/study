#include "../includes/multi_client_server.h"
#include <iostream>
#include <string>
#include <vector>

int port = 1234;
std::string_view ip {"localhost"};
int recv_len = 128;

std::vector<char> test_msg = {'a','b','c','\n'};


int main(){
    multi_client_server server(ip, port);
    std::vector<int> sock_index = {};
    std::vector<char> recv_buffer {};
    recv_buffer.reserve(recv_len);
    int recv_size {0};
    std::cout << "starting eternal loop\n";
    std::cout << server.sock.sock_fd << std::endl;
    while(1){
        //std::cout << server.fds.size() << std::endl;
        /*
        for(int i=1; i<server.fds.size(); ++i){
            //std::cout << server.fds[i].fd << std::endl;
            server.SendSocketData<char>(test_msg, i);
        }
        */
        server.check_client_available(sock_index);
        int deleted_socks = 0;
        for(size_t i=0; i<sock_index.size(); ++i){
            recv_size = server.ReadSocketData<char>(recv_buffer, recv_len,
                    sock_index[i]-deleted_socks);
            if(recv_size==0){
                deleted_socks++;
                continue;
            }
            for(auto& element: recv_buffer){
                std::cout << element;
            }
            server.SendSocketData<char>(recv_buffer, 
                    i-deleted_socks);
        }
    }
    return 0;
}

