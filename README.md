# Simplecoin readme - brief overview
Simplecoin is a prototype of cryptocurrency, based on Bitcoin. Currently, it is working on the basis of HTTP. Its blockchain network is under development.

server.py is a script allowing user to launch new nodes. It takes 2 or 4 arguments, depending on whether it is first node or not:
-a <ip> -p <port> -r <remote_ip> -o <remote_port>
passed ip and port as arguments will be node address.

Launching example network:

1. $ python3 server.py -a "127.0.0.1" -p "5001"
2. $ python3 server.py -a "127.0.0.1" -p "5002" -r "127.0.0.1" -o "5001"
3. $ python3 server.py -a "127.0.0.1" -p "5003" -r "127.0.0.1" -o "5002"

With 3 servers launched, test client (client_test.py) can be launched to test, how the network is working. It is designed to test features like signature verification and informing other nodes about new node.
