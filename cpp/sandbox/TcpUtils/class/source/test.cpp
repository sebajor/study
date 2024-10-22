#include <iostream>
#include "../includes/TcpSocket.h"
#include <sys/socket.h>

std::string_view host {"localhost"};
//std::string_view host {"127.0.0.1"};
int port = 1234;
int send_message = 4;
int trials = 10;

int test_sending(){
    TcpSocket sock = TcpSocket();
    if(sock.connectSocket(host, port)){
        std::cout << "error connecting\n";
        //return 0;
    }
    //std::cout << "asdsad";
    std::vector<char> msg {'h','o', 'l', 'a', '\n'};
    for(int i=0; i<send_message; ++i){
        sock.sendData(msg);
    }
    return 1;
}

int test_simple_server(){
    int client_sock {0};
    sockaddr client_addr;
    std::vector<char> msg;
    msg.reserve(64);

    TcpSocket sock = TcpSocket();
    sock.bindListenSocket(host, port);
    client_sock = sock.AcceptConnection(client_sock, client_addr);

    TcpSocket sock_client = TcpSocket(client_sock);
    int msg_size = sock_client.recvData(msg, 32);
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

    return 1;
}

const std::vector<std::string_view> cmds {
    "APEX:HOLO:SET_ACC",
    "APEX:HOLO:INFO"
};

const std::string response = "NO CMD FOUND\n";
std::vector<char> response_v(response.begin(), response.end());

int test_scpi_server(){
    int client_sock {0};
    sockaddr client_addr;
    std::vector<char> msg;
    msg.reserve(64);
    
    std::string s {};

    TcpSocket sock = TcpSocket();
    sock.bindListenSocket(host, port);
    client_sock = sock.AcceptConnection(client_sock, client_addr);

    TcpSocket sock_client = TcpSocket(client_sock);
    for(int i=0; i< trials; ++i){
        std::cout << "waiting message\n";
        int msg_size = sock_client.recvData(msg, 64);
        if(msg_size == -1)
            continue;
        std::cout << msg_size << std::endl;
        s = std::string(msg.data());
        std::cout << s << std::endl;
        int found = 0;
        for(auto& element : cmds){
            std::cout << element << std::endl;
            int loc = s.find(element);
            std::cout << "loc "<< loc << std::endl;
            if((loc!=-1) && (loc < msg_size)){
                try{
                    float parameter= std::stof(s.substr(element.size()));
                    std::cout << "paramter sent " << parameter << std::endl;
                    found = 1;
                }
                catch(std::invalid_argument){
                    std::cout << "error! \n";
                }
            }
        }
        std::cout << "found "<<found << std::endl;
        if(!found){
            std::cout << "no match\n";
            sock_client.sendData(response_v);
        }

    }
    return 1;
}



int main(){
    //test_sending();
    //test_simple_server();
    test_scpi_server();
    return 1;
}
