#include "../includes/TcpServer.h"
#include <string>
#include <vector>
#include <poll.h>
#include <sys/socket.h>

TcpServer::TcpServer(std::string_view ip, int port){
    server_sock = TcpSocket::socket_config();
    TcpSocket::bindListenSocket(server_sock, ip, port);
    pollfd server_pollfd {};
    server_pollfd.fd = server_sock;
    server_pollfd.events = POLLIN;
    fds.push_back(server_pollfd);
}

TcpServer::~TcpServer(){
    for(auto item: fds){
        TcpSocket::closeSocket(item.fd);
    }
}

int TcpServer::checkClientAvailable(std::vector<int> &indices, int timeout){
    int poll_count = poll(fds.data(), fds.size(),timeout);
    if(poll_count>0)
        std::cout << "poll count " <<poll_count << std::endl;
    if(poll_count<0)
        return -1;
    indices.clear();
    int new_sock = -1;
    sockaddr client_addr{0};
    for(int i=0; i<fds.size(); ++i){
        if(fds[i].revents & POLLIN){
            if(fds[i].fd == server_sock){
                //if the file descirptor is the server one then there is a new client
                //waiting to be accepted
                new_sock = TcpSocket::acceptConnection(server_sock, client_addr);
                if(new_sock<0)
                    continue;
                pollfd client_pollfd {0};
                client_pollfd.fd = new_sock;
                client_pollfd.events = POLLIN;
                fds.push_back(client_pollfd);
            }
            else{
                std::cout << "Data available at [" << i << "],"<< fds[i].fd << "\n";
                indices.push_back(i);
            }
        }
    }
    return 0;
}


