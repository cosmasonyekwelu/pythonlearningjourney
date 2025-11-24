"""
Multi-Client Chat Server
Handles multiple concurrent clients with message broadcasting
"""

import socket
import threading
import json
import datetime


class ChatServer:
    def __init__(self, host='127.0.0.1', port=12346):
        self.host = host
        self.port = port
        self.clients = []
        self.nicknames = {}
        self.server_socket = None
        self.running = False
        self.log_file = "chat_log.txt"

    def broadcast(self, message, sender_socket=None):
        message_json = json.dumps(message)
        disconnected_clients = []
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.send(message_json.encode('utf-8'))
                except:
                    disconnected_clients.append(client)
        for client in disconnected_clients:
            self.remove_client(client)
        self.log_message(message)

    def log_message(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(
                f"[{timestamp}] {message['sender']}: {message.get('content', '')}\n")

    def handle_client(self, client_socket, address):
        print(f"New connection from {address}")
        try:
            client_socket.send("NICK".encode('utf-8'))
            nickname = client_socket.recv(1024).decode(
                'utf-8').strip() or f"User{address[1]}"
            self.nicknames[client_socket] = nickname
            self.clients.append(client_socket)
            join_msg = {"type": "notification",
                        "content": f"{nickname} joined the chat.", "sender": "System"}
            self.broadcast(join_msg)
            while self.running:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                if data.strip().startswith("/"):
                    self.handle_command(client_socket, data.strip())
                else:
                    msg = {"type": "message", "content": data.strip(),
                           "sender": nickname}
                    self.broadcast(msg, client_socket)
        except:
            pass
        finally:
            self.remove_client(client_socket)

    def handle_command(self, client_socket, command):
        nickname = self.nicknames.get(client_socket, "Unknown")
        if command == "/users":
            user_list = ", ".join(self.nicknames.values())
            client_socket.send(json.dumps(
                {"type": "notification", "content": f"Online users: {user_list}"}).encode('utf-8'))
        elif command == "/quit":
            raise ConnectionResetError
        else:
            client_socket.send(json.dumps(
                {"type": "error", "content": "Unknown command."}).encode('utf-8'))

    def remove_client(self, client_socket):
        if client_socket in self.clients:
            self.clients.remove(client_socket)
        nickname = self.nicknames.pop(client_socket, "Unknown")
        try:
            client_socket.close()
        except:
            pass
        leave_msg = {"type": "notification",
                     "content": f"{nickname} left the chat.", "sender": "System"}
        self.broadcast(leave_msg)
        print(f"{nickname} disconnected.")

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        print(f"Chat Server started on {self.host}:{self.port}")
        try:
            while True:
                client_socket, address = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(
                    client_socket, address), daemon=True).start()
        except KeyboardInterrupt:
            print("\nServer shutting down.")
        finally:
            self.stop()

    def stop(self):
        self.running = False
        for client in self.clients[:]:
            self.remove_client(client)
        if self.server_socket:
            self.server_socket.close()
        print("Server stopped.")


def main():
    server = ChatServer()
    server.start()


if __name__ == "__main__":
    main()
