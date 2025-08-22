#include <string>
#include "TcpSocket.h"
#include <vector>
#include <poll.h>


class TcpServer{
    private:
    public:
        int server_sock {-1};
        std::vector<pollfd> fds {};
        TcpServer(std::string_view ip, int port);
        ~TcpServer();
        int checkClientAvailable(std::vector<int> &index, int timeout=-1);

        template <typename T>
        int recvSocketData(std::vector<T> &buff, int len, int sock_index){
            //the sock_index should come from the check_client_available
            //note that if the returned value is zero then you remove one of the 
            //clients, then the next sock_index should be diminish by one
            std::cout << "triying to read "<< sock_index << std::endl;
            int recv_len = TcpSocket::recvData<T>(fds[sock_index].fd, buff, len);
            if(recv_len==0){
                std::cout << "client ["<< sock_index <<"],"<< fds[sock_index].fd 
                    << " disconnected\n" ;
                TcpSocket::closeSocket(fds[sock_index].fd);
                fds.erase(fds.begin()+sock_index);
            }
            return recv_len;
        }
        template <typename T>
        int sendSocketData(std::vector<T> &buff, int sock_index){
            int sent_data = TcpSocket::sendData<T>(fds[sock_index].fd, buff);
            return sent_data;
        }
};
