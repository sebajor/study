#include "../includes/SCPI_server.h"
#include <string>
#include <sys/socket.h>
#include <poll.h>


SCPI_server::SCPI_server(std::string_view ip, int port){
    sock.bindListenSocket(ip, port);
}

SCPI_server::~SCPI_server(){
    for(int i=0; i<client_sockets.size(); ++i){
        client_sockets[i].CloseSocket();
    }
}

int SCPI_server::AddClient(){
    int client_sock=-1;
    sockaddr client_addr;
    client_sock = sock.AcceptConnection(client_sock,client_addr);   //this one is blocking?
    TcpSocket client(client_sock);
    client_sockets.push_back(client);
    return 0;
}

//check if there is message in some of the sockets.. the idea is to use epoll or somethign
//like that to just check when there is data availble...
//
int SCPI_server::CheckAvailableMessage(){
    return 0;
}


