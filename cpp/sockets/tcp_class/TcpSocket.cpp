#include <iostream>
#include <stdlib.h>
#include <netdb.h>
#include <sys/types.h>
#include <unistd.h>
#include <string>
#include <cstring>
#include <time.h>
#include <arpa/inet.h>
#include <errno.h>
#include <sys/socket.h>
//#include <"TcpSocket.hpp">

class TcpSocket{
    public:
        TcpSocket(int sndsize, int rcvsize,int timeout){
            createSocket(timeout);
        };
        ~TcpSocket(){
            disconnectSocket();
        };
        void SetSocketBuffers(int recvbuf, int sendbuf){
            if(setsockopt(sock, SOL_SOCKET, SO_RCVBUF, &recvbuf, sizeof(int)))
                throw std::logic_error("socket send buffer not set");
            if(setsockopt(sock, SOL_SOCKET, SO_SNDBUF, &sendbuf, sizeof(int)))
                throw std::logic_error("socket send buffer not set");
        };

        void ConnectSocket(std::string host, int port){
            if(sock<0)
                throw std::logic_error("socket destroyed");
            server = gethostbyname(host.c_str());
            if(server==NULL)
                throw std::logic_error("gethostbyname returns NULL");
            memcpy(&address.sin_addr.s_addr, server->h_addr, server->h_length);
            address.sin_family = AF_INET;
            address.sin_port = htons(port);
            //try to connect the socket
            if(connect(sock, (struct sockaddr *)&address, sizeof(address))<0)
                throw std::logic_error("socket connect error");
        };

        void ListenSocket(int port, int queueSize){
            if(sock<0){
                throw std::logic_error("socket destroyed");
            }
            address.sin_family = AF_INET;
            address.sin_addr.s_addr = INADDR_ANY;
            address.sin_port = htons(port);
            if(bind(sock, (struct sockaddr *)&address, sizeof(address))<0)
                throw std::logic_error("cannot bind to port");
            if(listen(sock, queueSize)<0)
                throw std::logic_error("Error listening");
        };


        void ReadData(void* recv_buffer, int size){
            int asd = recv(sock, recv_buffer, size, 0);
            std::cout << asd<< std::endl;
                //throw std::logic_error("Error recv");
        }


        void disconnectSocket(){
            std::cout << "destructor"<<std::endl;
            if(sock<0)
                throw std::logic_error("socket already disconnected");
            int fd = sock;
            shutdown(fd, SHUT_RD);
            int out = close(fd);
            if(out<0)
                throw std::logic_error("socket not closed");
            sock = -1;
        };

    private:
        //variables
        int sock;   //socket filedescriptor
        struct sockaddr_in address = {0};
        struct hostent *server;
        //functions
        
        void createSocket(int timeout){
            struct timeval sock_timeout;
            struct linger sock_linger;  //behaviour when closing the socket
            //create socket and set the timeout 
            sock = socket(AF_INET, SOCK_STREAM,0);
            if(sock<0)
                throw std::logic_error("socket not created :(");
            if(timeout<0)
                timeout=0;
            sock_timeout.tv_sec = timeout;
            //set the send timeout
            if(setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, &sock_timeout, sizeof(struct timeval)))
                throw std::logic_error("socket send timeout not set");
            //set the recv timeout
           if(setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &sock_timeout, sizeof(struct timeval)))
                throw std::logic_error("socket recv timeout not set");
           //set the linger
           sock_linger.l_onoff = timeout>0;
           sock_linger.l_linger = (timeout>0) ? timeout:0;
           if(setsockopt(sock, SOL_SOCKET, SO_LINGER, &sock_linger, sizeof(struct linger)))
                throw std::logic_error("socket linger timeout not set");
        };
};


int main(){
    int port = 1234;
    int queue_size = 10;
    char buffer[1024] = {65, 65};
    
    TcpSocket socket_test(1024, 1024, 30);
    socket_test.ListenSocket(port, queue_size);
    sleep(10);

    //Here i still need to accept the incomming socket with accept...

    socket_test.ReadData(buffer, 10);
    std::cout << buffer << std::endl;
    return 1;
}
