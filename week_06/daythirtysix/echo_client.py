"""
Basic TCP Echo Client
Connects to the echo server and sends messages
"""

import socket


def start_echo_client(host='127.0.0.1', port=12345):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print(f"Connecting to {host}:{port}...")
        client_socket.connect((host, port))
        print("Connected to echo server.")
        welcome = client_socket.recv(1024).decode('utf-8')
        print(welcome.strip())
        while True:
            message = input("You: ").strip()
            client_socket.send(message.encode('utf-8'))
            if message.lower() == 'quit':
                break
            response = client_socket.recv(1024).decode('utf-8')
            print("Server:", response.strip())
    finally:
        client_socket.close()
        print("Disconnected from server.")


if __name__ == "__main__":
    start_echo_client()
