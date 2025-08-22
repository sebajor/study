#include "../../tcp_server_multi_client/includes/TcpServer.h"
#include <vector>
#include <string>
#include <utility>


class SCPI_server: public TcpServer {
    public:
        int internal_value = -1;
        SCPI_server(std::string_view ip, int port);
        ~SCPI_server();
        int parse_recv_msg(std::string_view input_data, std::string &out_msg);

        //methods
        int SCPI_help(std::string_view msg, std::string &out_msg);
        int SCPI_set_integer(std::string_view msg, std::string &out_msg);
        int SCPI_get_integer(std::string_view msg, std::string &out_msg);

        
        std::vector<std::pair<std::string_view, int(SCPI_server::*)(std::string_view, std::string&)>> cmds {
            {"SCPI_SERVER:INFO", &SCPI_server::SCPI_help},
            {"SCPI_SERVER:SET_INT", &SCPI_server::SCPI_set_integer},
            {"SCPI_SERVER:GET_INT", &SCPI_server::SCPI_get_integer}
        };

};
