#include "../includes/multi_client_server.h"
#include <string>
#include <vector>
#include <poll.h>
#include <sys/socket.h>

multi_client_server::multi_client_server(std::string_view ip, int port){
    sock.bindListenSocket(ip, port);
    //add the server socket to the poll list
    pollfd server_pollfd{};
    server_pollfd.fd = sock.sock_fd;
    server_pollfd.events = POLLIN;      //check for the incomming connections
    fds.push_back(server_pollfd);
}

multi_client_server::~multi_client_server(){
}

//This functions puts the address of the clients that are ready to be read
int multi_client_server::check_client_available(std::vector<int> &addrs){
    int poll_count = poll(fds.data(), fds.size(),-1);
    if(poll_count>0)
        std::cout << "poll count " <<poll_count << std::endl;
    if(poll_count<0)
        return -1;
    addrs.clear();
    int new_sock = 0;
    sockaddr client_addr {};
    std::cout << fds.size() << std::endl;
    for(size_t i=0; i<fds.size(); ++i){
        if(fds[i].revents & POLLIN){
            if(fds[i].fd == sock.sock_fd){
                //if the file descirptor is the server one then there is a new client
                //waiting to be accepted
                new_sock = sock.AcceptConnection(new_sock, client_addr);
                if(new_sock<0){
                    continue;
                }
                pollfd client_pollfd {};
                client_pollfd.fd = new_sock;
                client_pollfd.events = POLLIN;
                fds.push_back(client_pollfd);
                //this client is getting out scope.. 
                //but when pushing it into vector generates a copy
                //I think since by default it sets the reuse addr there is no problem
                TcpSocket client(new_sock);
                //client_sockets.push_back(client);
                client_sockets.emplace_back(client);
                std::cout << "client added\n";
            }
            else{
                std::cout << "data available at "<< i << " " << fds[i].fd << "\n" ;
                addrs.push_back(i);
            }
        }
    }
    return 0;
}


