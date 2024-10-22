#include <iostream>
#include <fftw3.h>
#include "../../tcp_server_multi_client/includes/TcpServer.h"



class TcpFFT: public TcpServer  {
    TcpFFT(std::string_view recv_ip, int recv_port, std::string_view send_ip, int send_port);
    ~TcpFFT();
};


