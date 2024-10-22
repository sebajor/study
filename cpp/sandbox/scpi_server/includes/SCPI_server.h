#include "../../tcp_server_multi_client/includes/TcpServer.h"
#include <vector>
#include <string>
#include <map>
#include <functional>


class SCPI_server: public TcpServer {
    public:
        //The best should be to have a mapping<string, func> but I couldnt manage
        //to make it..
        int internal_value = -1;
        SCPI_server(std::string_view ip, int port);
        ~SCPI_server();
        int parse_recv_msg(std::string_view input_data, float &arg, std::vector<std::string_view> &scpi_cmd);
        //methods
        int SCPI_help(float &args, std::string &msg);
        int SCPI_set_integer(float &args, std::string &msg);
        int SCPI_get_integer(float &args, std::string &msg);
};
