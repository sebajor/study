#include "../includes/TcpFFT.h"
#include <vector>


TcpFFT::TcpFFT(std::string_view recv_ip, int recv_port, std::string_view send_ip, int send_port): TcpServer(send_ip, send_port){
    //here we should start listening into the recv_ip,port
}
