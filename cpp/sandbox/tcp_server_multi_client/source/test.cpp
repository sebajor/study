#include "../includes/TcpServer.h"
#include <iostream>
#include <string>
#include <vector>


int port = 1234;
std::string_view ip {"localhost"};
int recv_len = 128;
std::vector<char> test_msg = {'a','b','c','\n'};

int main(){
    TcpServer server(ip, port);
    std::vector<int> sock_index = {};
    std::vector<char> recv_buffer {0};
    recv_buffer.reserve(recv_len);
    int recv_size {0};
    std::cout << "starting eternal loop\n";
    while(1){
        std::cout << server.fds.size() << "\n";
        server.checkClientAvailable(sock_index);
        for(auto element: sock_index){
            std::cout << element<< " " ;
        }
        std::cout <<"=indices \n";
        std::cout << "sock index size: " << sock_index.size()-1<<"\n" ;
        for(int i=sock_index.size()-1; i>-1; --i){
            //like we can delete sockets its better to move from higher to
            //lower indices
            recv_size = server.recvSocketData<char>(recv_buffer, recv_len, 
                    sock_index[i]);
            std::cout << "recv size " << recv_size << "\n";
            if(recv_size==0){
                //there was a deleted socket
                std::cout << "delete socket at "<<i << std::endl;
                continue;
            }
            std::cout << "buff size: "<< recv_buffer.size() << "\n";
            for(auto element: recv_buffer){
                std::cout << element;
            }
            server.sendSocketData<char>(recv_buffer, sock_index[i]);
            //server.sendSocketData<char>(test_msg, sock_index[i]);
            std::cout << "\n";
        }
    }


}
