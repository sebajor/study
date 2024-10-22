#include <iostream>
#include "../includes/TcpSocket.h"
#include <sys/socket.h>


std::string_view host {"localhost"};
//std::string_view host {"127.0.0.1"};
//std::string_view host {"192.168.1.13"};
int port = 1234;
int send_message = 4;
int trials = 10;

int test_sending(){
    int sock_fd = TcpSocket::socket_config();
    std::cout << "sock_fd "<< sock_fd << std::endl;
    if(TcpSocket::connectSocket(sock_fd, host, port)){
        std::cout << "error connecting\n";
    }
    std::cout << "trying to send data\n";
    std::vector<char> msg {'h','o', 'l', 'a', '\n'};
     for(int i=0; i<send_message; ++i){
        TcpSocket::sendData(sock_fd, msg);
    }
    TcpSocket::closeSocket(sock_fd);
    return 0;
}

int test_simple_server(){
    int client_sock {0};
    sockaddr client_addr;
    std::vector<char> msg;
    msg.reserve(64);

    int sock_fd = TcpSocket::socket_config();
    TcpSocket::bindListenSocket(sock_fd, host, port);
    client_sock = TcpSocket::acceptConnection(sock_fd, client_addr);

    int msg_size = TcpSocket::recvData(client_sock, msg, 32);
    for(int i=0; i<msg_size; ++i){
        std::cout << msg[i];
    }
    /*
    char* raw_pointer =&(msg[0]);
    int recv_size = recv(client_sock, raw_pointer, 32*sizeof(char), 0);
    for(int i=0; i<recv_size; ++i){
        std::cout << msg[i];
    }
    shutdown(client_sock,SHUT_RD);
    */
    TcpSocket::closeSocket(sock_fd);
    return 1;
}


int main(){
    //test_sending();
    test_simple_server();
}
