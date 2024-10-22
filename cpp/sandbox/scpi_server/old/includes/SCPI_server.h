#include "../../TcpUtils/includes/TcpSocket.h"
#include <vector>
#include <string>

class SCPI_server{
    private:
        TcpSocket sock{};
        std::vector<TcpSocket> client_sockets {};
        std::vector<std::string_view> commands {
            "APEX:HOLO:INFO",
            "APEX:HOLO:GET_DATA"
        };
    public:
        SCPI_server(std::string_view ip, int port);
        ~SCPI_server();
        int AddClient();
        int CheckAvailableMessage();
};
