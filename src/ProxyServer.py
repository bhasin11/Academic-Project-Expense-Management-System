import socket
import threading
import signal
import sys
import redis
from circuitbreaker import CircuitBreaker

r_server = redis.Redis("127.0.0.1")

MY_EXCEPTION = 'Threw Dependency Exception'
config =  {
            "HOST_NAME" : "0.0.0.0",
            "BIND_PORT" : 12301,
            "MAX_REQUEST_LEN" : 8192, #
            "CONNECTION_TIMEOUT" : 5
          }


class Server:
    """ The server class """

    def __init__(self, config):
        signal.signal(signal.SIGINT, self.shutdown)     # Shutdown on Ctrl+C
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)             # Create a TCP socket
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    # Re-use the socket
        self.serverSocket.bind((config['HOST_NAME'], config['BIND_PORT'])) # bind the socket to a public host, and a port
        self.serverSocket.listen(10)    # become a server socket
        self.__clients = {}
        self.i = 0


    def listenForClient(self):
        """ Wait for clients to connect """
        while True:
            (clientSocket, client_address) = self.serverSocket.accept()   # Establish the connection
            d = threading.Thread(name=self._getClientName(client_address), target=self.proxy_thread, args=(clientSocket, client_address))
            d.setDaemon(True)
            d.start()
        self.shutdown(0,0)


    def proxy_thread(self, conn, client_addr):
        request = conn.recv(config['MAX_REQUEST_LEN'])        # get the request from browser
        first_line = request.split('\n')[0]                   # parse the first line
        url = first_line.split(' ')[1]                        # get url

        http_pos = url.find("://")          # find pos of ://
        if (http_pos==-1):
            temp = url
        else:
            temp = url[(http_pos+3):]       # get the rest of url

        port_pos = temp.find(":")           # find the port pos (if any)

        webserver_pos = temp.find("/")
        if webserver_pos == -1:
            webserver_pos = len(temp)

        if (port_pos==-1 or webserver_pos < port_pos):      # default port
            port = 80
            webserver = temp[:webserver_pos]

        else:                                               # specific port

            port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
            webserver = temp[:port_pos]

        inst = Instanes()
        port = int(inst.getInstance(0))
        self.Connection(conn,request,port)



    @CircuitBreaker(max_failure_to_open=3)
    def Connection(self,conn,request,port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(config['CONNECTION_TIMEOUT'])
            host = '127.0.0.1'
            port = int (port)
            s.connect((host, port))
            s.sendall(request)

            while 1:
                data = s.recv(config['MAX_REQUEST_LEN'])  # receive data from web server
                if (len(data) > 0):
                    conn.send(data)  # send to browser
                else:
                    break

            s.close()
            conn.close()
            return 'SUCCESS'

        except Exception as ex:
            print MY_EXCEPTION


    def _getClientName(self, cli_addr):
        return "Client"


    def shutdown(self, signum, frame):
        self.serverSocket.close()
        sys.exit(0)


class Instanes:

    def __init__(self):
        self.instances = r_server.lrange("FINAL", 0, r_server.llen("FINAL"))

    def getInstance(self,i):
        return self.instances[i]

    def getLength(self):
        return len(self.instances)

if __name__ == "__main__":
    server = Server(config)
    server.listenForClient()
