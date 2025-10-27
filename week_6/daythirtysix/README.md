# Day 36: Networking & Socket Programming

## Overview

This project demonstrates the fundamentals of network programming using Python sockets.  
It covers how to create both simple TCP echo programs and a multi-client chat system.  
The examples in this folder show how clients and servers communicate, handle multiple connections, and exchange data over a network.

---

## Folder Structure

```

daythirtysix/
│
├── day_thirtysix.py      # Main menu and example runner
├── README.md             # Documentation file
├── echo_server.py        # Basic TCP echo server
├── echo_client.py        # Basic TCP echo client
├── chat_server.py        # Multi-client chat server
├── chat_client.py        # Chat client for multi-user messaging
└── chat_log.txt          # Chat history log file (auto-generated)

```

---

## Quick Start

### Option 1: Use the Main Menu

Run the interactive menu to access all examples:

```bash
python day_thirtysix.py
```

### Option 2: Run Individual Components

**Start the Echo Server**

```bash
python echo_server.py
```

**Run the Echo Client (in a new terminal)**

```bash
python echo_client.py
```

**Start the Chat Server**

```bash
python chat_server.py
```

**Run a Chat Client (in one or more terminals)**

```bash
python chat_client.py
```

---

## Features

### Echo Server and Client

- Demonstrates the basics of socket connections.
- Uses TCP for reliable communication.
- Handles one client connection at a time.
- Echoes received messages back to the sender.

### Multi-Client Chat Server

- Handles multiple clients using threading.
- Broadcasts messages to all connected users.
- Supports simple text commands such as:

  - `/users` — show online users
  - `/quit` — exit chat

- Logs messages to `chat_log.txt`.
- Demonstrates JSON message formatting.

---

## Learning Objectives

- Understand the concept of **TCP/IP communication**.
- Learn the **client-server model** in networking.
- Use the Python `socket` module for network programming.
- Manage **multiple connections** using threads.
- Handle user input and data serialization.
- Implement basic **error handling** in networked applications.

---

## Networking Concepts Covered

- IP addresses and port numbers.
- TCP vs UDP transport protocols.
- Socket functions:

  - `socket()`, `bind()`, `listen()`, `accept()`, `connect()`, `send()`, `recv()`

- Threading for concurrent connections.
- JSON-based message exchange.

---

## Chat Message Protocol

Messages exchanged between server and clients follow this structure:

```json
{
  "type": "message | notification | error",
  "content": "Message text",
  "sender": "User nickname",
  "timestamp": "2025-10-27T12:00:00"
}
```

---

## Example Workflow

1. Start the chat server:

   ```bash
   python chat_server.py
   ```

2. Launch multiple chat clients:

   ```bash
   python chat_client.py
   ```

3. Clients can send messages to each other in real-time.
4. Use `/users` to list connected users.
5. Type `/quit` to disconnect.

---

## Key Takeaways

- A **socket** is the endpoint of communication between two programs.
- **TCP** ensures reliable, ordered, and error-checked delivery of data.
- **Threading** allows handling multiple clients simultaneously.
- **Serialization** (e.g., JSON) helps structure and interpret transmitted data.
- Proper **exception handling** ensures smooth client disconnection and server stability.

---
