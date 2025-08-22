#include "../includes/SCPI_server.h"
#include <string>
#include <vector>

std::string_view ip {"localhost"};
int port {1234};
std::vector<int> sock_index {0};
int recv_len = 128;
std::string cmds_out(100,' ');



int main(){
    int recv_size {0};
    std::vector<char> recv_buffer {0};
    recv_buffer.reserve(recv_len);
    //to parse the message
    std::string recv_msg {}; 
    std::string out_msg {"No cmd found\n"};
    float arg=-1;
    int func_index = -1;
    //
    SCPI_server serv(ip, port);
    std::cout << "entering to while 1\n";
    while(1){
        serv.TcpServer::checkClientAvailable(sock_index);
        for(int i=sock_index.size()-1; i>-1; --i){
            recv_size = serv.TcpServer::recvSocketData<char>(recv_buffer, recv_len,
                    sock_index[i]);
            std::cout << "recv size " << recv_size << "\n";
            if(recv_size==0){
                //there was a deleted socket
                std::cout << "delete socket at "<<i << std::endl;
                continue;
            }
            recv_msg = recv_buffer.data();
            serv.parse_recv_msg(recv_msg, cmds_out);
            //send the response
            recv_buffer.resize(cmds_out.size());
            recv_buffer.assign(cmds_out.data(), cmds_out.data()+cmds_out.size());
            serv.TcpServer::sendSocketData<char>(recv_buffer, sock_index[i]);
            recv_buffer.clear();
        }


    }
}
