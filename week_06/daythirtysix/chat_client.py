"""
Chat Client for Multi-Client Chat Server
"""

import socket
import threading
import json


class ChatClient:
    def __init__(self, host='127.0.0.1', port=12346):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.nickname = ""

    def receive_messages(self):
        while self.running:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    break
                message = json.loads(data)
                print(
                    f"{message.get('sender', 'Server')}: {message.get('content', '')}")
            except:
                break
        self.stop()

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host, self.port))
            self.running = True
            nickname_request = self.socket.recv(1024).decode('utf-8')
            if nickname_request == "NICK":
                self.nickname = input(
                    "Enter your nickname: ").strip() or "Guest"
                self.socket.send(self.nickname.encode('utf-8'))
            threading.Thread(target=self.receive_messages, daemon=True).start()
            print("Connected to chat. Type messages below.")
            while self.running:
                msg = input()
                if msg.lower() == "/quit":
                    break
                self.socket.send(msg.encode('utf-8'))
        except:
            print("Connection failed.")
        finally:
            self.stop()

    def stop(self):
        self.running = False
        if self.socket:
            self.socket.close()
        print("Disconnected.")


def main():
    client = ChatClient()
    client.start()


if __name__ == "__main__":
    main()
