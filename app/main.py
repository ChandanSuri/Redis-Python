import socket
import threading

def handle_connection(connection, addr):
    pong = "+PONG\r\n"

    # We are sending 2 commands with the same connection.
    while True:
        request = connection.recv(1024)
        if not request:
            break

        data = request.decode()
        # PING should be received and then we send our encoded packet with data.
        if "ping" in data.lower():
            connection.send(pong.encode())

    connection.close()

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)

    while True:
        # Wait for client
        client_socket, client_address = server_socket.accept() 
        print("Received a connection from client: {client_address}")
        
        threading.Thread(
            target=handle_connection, 
            args=[client_socket, client_address]
        ).start()

if __name__ == "__main__":
    main()
