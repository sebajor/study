#include <sys/socket.h>
#include <string>
#include <netdb.h>      //to have the struct sockaddr_in, etc
#include <vector>
#include <iostream>


class TcpSocket{
    private:
        struct sockaddr_in address {};
        struct hostent *server;
        int socket_creation(int timeout, int reuse_addr=1);
    public:
        int sock_fd {};     //socket file descriptor
        TcpSocket(int sock=-1, int sndsize=128, int recvsize=128, int timeout=10, int reuse_addr=1);
        ~TcpSocket();
        int connectSocket(std::string_view host, int port);
        int setBuffers(int sendsize, int recvsize);

        int listenSocket(int port, int queue_size);
        
        //when using the socket as server
        int bindListenSocket(std::string_view ip, int port, int backlog=32);
        int AcceptConnection(int client_sock, sockaddr &client_addr);
        int CloseSocket();


        //C++ sucks and for templates I need to put the definition in the header
        template <typename T>
        int sendData(std::vector<T> &data){
            T* raw_pointer = &(data[0]);
            int bytes_sent = send(sock_fd, raw_pointer, data.size()*sizeof(T), 0);
            return bytes_sent/sizeof(T);
        }

        template <typename T>
        int recvData(std::vector<T> &buff, int len){
            /*
             * Here len is in terms of T!! so the actual number of bytes that you got are
             * len*sizeof(T)
             */
            //first we check if the buffer has enough space
            if(buff.capacity()<len)
                buff.resize(len);
            T* raw_pointer = &(buff[0]);
            int out = recv(sock_fd, raw_pointer, len*sizeof(T), 0);
            //if(out==0)
            //    std::cout << "socket disconnected!\n";
            //if(out==-1)
            //    std::cout << "error receiving data\n";
            return out;
        }

};
