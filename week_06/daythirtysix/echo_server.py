"""
Basic TCP Echo Server
Demonstrates fundamental socket programming concepts
"""

import socket
import threading


def handle_client(client_socket, address):
    print(f"New connection from {address}")
    try:
        client_socket.send(
            "Welcome to the Echo Server! Type 'quit' to exit.\n".encode('utf-8'))
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            message = data.strip()
            print(f"Received from {address}: {message}")
            if message.lower() == 'quit':
                client_socket.send("Goodbye.\n".encode('utf-8'))
                break
            client_socket.send(f"ECHO: {message}\n".encode('utf-8'))
    finally:
        client_socket.close()
        print(f"Connection with {address} closed.")


def start_echo_server(host='127.0.0.1', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Echo Server started on {host}:{port}")
    try:
        while True:
            client_socket, address = server_socket.accept()
            threading.Thread(target=handle_client, args=(
                client_socket, address), daemon=True).start()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_echo_server()
