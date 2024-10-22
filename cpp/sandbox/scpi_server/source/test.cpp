#include "../includes/SCPI_server.h"
#include <string>
#include <vector>

std::string_view ip {"localhost"};
int port {1234};
std::vector<int> sock_index {0};
int recv_len = 128;

std::vector<std::string_view> scpi_cmds {
    "SCPI_SERVER:INFO",
    "SCPI_SERVER:SET_INTEGER",
    "SCPI_SERVER:INTEGER?"
};

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
            //like we can delete sockets its better to move from higher to
            //lower indices
            recv_size = serv.TcpServer::recvSocketData<char>(recv_buffer, recv_len, 
                    sock_index[i]);
            std::cout << "recv size " << recv_size << "\n";
            if(recv_size==0){
                //there was a deleted socket
                std::cout << "delete socket at "<<i << std::endl;
                continue;
            }
            /*
            std::cout << "buff size: "<< recv_buffer.size() << "\n";
            for(auto element: recv_buffer){
                std::cout << element;
            }
            */
            recv_msg = recv_buffer.data();
            func_index = serv.parse_recv_msg(recv_msg, arg, scpi_cmds);
            std::cout << "arg recv "<<arg<<"\n";
            switch(func_index){
                case 0:{
                    serv.SCPI_help(arg, out_msg);
                    break;
                    }
                case 1:{
                    serv.SCPI_set_integer(arg, out_msg);
                    break;
                    }
                case 2:{
                    serv.SCPI_get_integer(arg, out_msg);
                    break;
                    }
                default:{
                    out_msg = "No cmd found\n";
                    break;
                    }
            }
            recv_buffer.resize(out_msg.size());
            recv_buffer.assign(out_msg.data(), out_msg.data()+out_msg.size());
            serv.TcpServer::sendSocketData<char>(recv_buffer, sock_index[i]);
            //serv.TcpServer::sendSocketData<char>(recv_buffer, sock_index[i]);
            //server.sendSocketData<char>(test_msg, sock_index[i]);
            //std::cout << "\n";
        }
    }
}
