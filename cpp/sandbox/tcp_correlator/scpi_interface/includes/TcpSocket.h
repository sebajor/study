#include <string>
#include <arpa/inet.h>
#include <vector>
#include <iostream>


namespace TcpSocket{
int socket_config(int sock=-1, int sndsize=128, int recvsize=128, 
        int timeout=10, int reuse_addr=1);

int socket_creation(int timeout, int reuse_addr);

int setBuffer(int sock_fd, int sendsize, int recvsize);

int connectSocket(int sock_fd, std::string_view host, int port);

int bindListenSocket(int sock_fd, std::string_view ip, int port, int backlog=32);

int acceptConnection(int sock_fd, sockaddr &client_addr);

int closeSocket(int sock_fd);


template <typename T>
int sendData(int sock_fd, std::vector<T> &data){
    T* raw_pointer = &(data[0]);
    int bytes_sent = send(sock_fd, raw_pointer, data.size()*sizeof(T), 0);
    return bytes_sent/sizeof(T);
}

template <typename T>
int recvData(int sock_fd, std::vector<T> &buff, int len){
    /*
     * Here len is in terms of T!! so the actual number of bytes that you got are
     * len*sizeof(T)
     */
    //first we check if the buffer has enough space
    if(buff.size()<len)
        buff.resize(len);
    T* raw_pointer = &(buff[0]);
    int out = recv(sock_fd, raw_pointer, len*sizeof(T), 0);
    if(out==0){
        std::cout << "socket disconnected!\n";
        return out;
    }
    if(out==-1){
        std::cout << "error receiving data\n";
        return out;
    }
    buff.resize(out);
    return out;
}

}
