import socket


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    pong = "+PONG\r\n"

    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    connection, _ = server_socket.accept() # wait for client

    # We are sending 2 commands with the same connection.
    while True:
        with connection:
            request = connection.recv(1024)
            data = request.decode()

            # PING should be received and then we send our encoded packet with data.
            if "ping" in data.lower():
                connection.send(pong.encode())

if __name__ == "__main__":
    main()
