
#include <stdio.h>
#include <stdlib.h>
#include <netdb.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <time.h>
#include <arpa/inet.h>
#include <errno.h>
#include <sys/socket.h>

class TcpSocket{
    public:
        TcpSocket(int sndsize, int rcvsize,int timeout);
        ~TcpSocket();
        ConnectSocket(string host, int port);
        ListenSocket(int queueSize);
        disconnectSocket();
    private:
        int sock;
}
