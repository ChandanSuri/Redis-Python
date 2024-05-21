import socket


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    pong = "+PONG\r\n"

    server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    connection, addr = server_socket.accept() # wait for client

    with connection:
        connection.recv(1024)
        connection.send(pong.encode())

if __name__ == "__main__":
    main()
