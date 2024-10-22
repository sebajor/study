#include "../includes/TcpSocket.h"
#include <iostream>
#include <string>
#include <arpa/inet.h>
#include <vector>


TcpSocket::TcpSocket(int sock, int sendsize, int recvsize, int timeout, int reuse_addr){
    if(sock==-1){
        if(TcpSocket::socket_creation(timeout, reuse_addr))
            std::cout << "Error creating the socket\n";
    }
    else{
        std::cout << "creating socket "<< sock  << std::endl;
        sock_fd = sock;     //this assignation is valid in other scopes??
    }
    if(TcpSocket::setBuffers(sendsize, recvsize))
        std::cout << "Error setting socket buffer\n";
}


TcpSocket::~TcpSocket(){
    CloseSocket();
}

int TcpSocket::socket_creation(int timeout, int reuse_addr){
    /*  
     *  Create a simple socket 
     */
    struct timeval sock_timeout {};
    struct linger sock_linger {};   //behavior when closing tehe socket
    const int enable = 1;

    sock_fd = socket(AF_INET, SOCK_STREAM, 0);
    if(sock_fd<0)
        return 1;
    if(timeout<0)
        timeout =0;
    sock_timeout.tv_sec = timeout;
    if(setsockopt(sock_fd, SOL_SOCKET, SO_SNDTIMEO, &sock_timeout, sizeof(struct timeval)))
        return 1;
    if(setsockopt(sock_fd, SOL_SOCKET, SO_RCVTIMEO, &sock_timeout, sizeof(struct timeval)))
        return 1;
    if(setsockopt(sock_fd, SOL_SOCKET, SO_KEEPALIVE, & enable, sizeof(int)))
        std::cout << "socket keep-alive not set!\n";
    //set linger
    sock_linger.l_onoff = timeout>0;
    sock_linger.l_linger = (timeout>0) ? timeout:0;
    if(setsockopt(sock_fd, SOL_SOCKET, SO_LINGER, &sock_linger, sizeof(struct linger)))
        return 1;
    
    if(reuse_addr){
        if(setsockopt(sock_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &enable, sizeof(int))){
            std::cout << "error setting reuse addr";
        }
    }
    return 0;
}


int TcpSocket::setBuffers(int sendsize, int recvsize){
    int send = setsockopt(sock_fd, SOL_SOCKET, SO_SNDBUF, &sendsize, sizeof(int));
    int recv = setsockopt(sock_fd, SOL_SOCKET, SO_RCVBUF, &recvsize, sizeof(int));
    return (send | recv);
}


int TcpSocket::connectSocket(std::string_view host, int port){
    if(inet_pton(AF_INET, host.data(), &(address.sin_addr))){
        std::cout << "Error getting address\n";
        return 1;
    }
    address.sin_family = AF_INET;
    address.sin_port = htons(port);
    //try to connect 
    if(connect(sock_fd, (struct sockaddr *)&address, sizeof(address))){
        std::cout << "Error connecting to the address\n";
        return 1;
    }
    return 0;
}


int TcpSocket::bindListenSocket(std::string_view ip, int port, int backlog){
    if(inet_pton(AF_INET, ip.data(), &(address.sin_addr))){
        std::cout << "Error getting address\n";
        return 1;
    }
    address.sin_family = AF_INET;
    address.sin_port = htons(port);
    //try to get the port
    if(bind(sock_fd, (struct sockaddr *)&address, sizeof(address))){
        std::cout << "Error binding socket\n";
        return 1;
    }
    //listen for incomming connections
    if(listen(sock_fd, backlog)){
        std::cout << "Error listening\n";
        return 1;
    }
    return 0;
}

int TcpSocket::AcceptConnection(int client_sock, sockaddr &client_addr){
    socklen_t addr_size = sizeof(client_addr);
    client_sock = accept(sock_fd, (struct sockaddr *) client_sock, &addr_size);
    return client_sock;
}



int TcpSocket::CloseSocket(){
    std::cout << "destroying the socket "<< sock_fd <<std::endl;
    if(~(sock_fd))
        shutdown(sock_fd, SHUT_RD);
    return 0;
}







