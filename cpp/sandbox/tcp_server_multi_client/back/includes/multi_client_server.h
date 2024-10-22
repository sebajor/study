#include <string>
#include "../../TcpUtils/includes/TcpSocket.h"
#include <vector>
#include <poll.h>

class multi_client_server{
    private:
        std::vector<TcpSocket> client_sockets {};
    public:
        TcpSocket sock{};
        std::vector<pollfd> fds {};
        multi_client_server(std::string_view ip, int port);
        ~multi_client_server();
        int check_client_available(std::vector<int> &addrs);
        
        template <typename T>
        int ReadSocketData(std::vector<T> &buff, int len, int sock_index){
            //the sock_addr should come from the check_client_available
            //note that if the returned value is zero then you remove one of the 
            //clients, then the next sock_index should be diminish by one
            std::cout << "triying to read "<< sock_index << std::endl;
            int recv_len = client_sockets[sock_index-1].recvData<T>(buff,len);
            if(recv_len==0){
                //then the client is disconnected
                std::cout << "client "<< sock_index << " disconnected\n";
                client_sockets[sock_index-1].CloseSocket();
                client_sockets.erase(client_sockets.begin()+sock_index-1);
                fds.erase(fds.begin()+sock_index);
            }
            return recv_len;
        };

        template <typename T>
        int SendSocketData(std::vector<T> &data, int sock_index){
            int sent_data = client_sockets[sock_index-1].sendData<T>(data);
            return sent_data;
        }
};
