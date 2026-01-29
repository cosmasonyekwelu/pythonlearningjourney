# Day 36: Networking & Socket Programming

**Date:** October 27, 2025

## Learning Objective
To understand the fundamentals of network communication in Python using the `socket` module and to build basic server-client architectures.

## Concepts Covered
- **Socket Programming**: Understanding TCP/IP sockets, binding, listening, and accepting connections.
- **Echo Servers**: Building a basic server that returns any data sent by a client.
- **Multi-threading**: Using threads to handle multiple simultaneous client connections.
- **Protocol Design**: Creating a simple chat protocol for message exchange.
- **Client Implementation**: Building robust clients that can connect, send data, and handle server responses.

## Code Explanation
The `day_thirtysix.py` script acts as a launcher for several networking examples:
- **`echo_server.py` & `echo_client.py`**: A foundational "Hello World" of networking.
- **`chat_server.py`**: A more advanced implementation that maintains a list of connected clients and broadcasts messages to all of them.
- **`chat_client.py`**: Uses a separate thread for receiving messages so the user can type and receive simultaneously.
- **`run_single_chat_test()`**: Orchestrates a server and client in a single process using threads for easy demonstration.

## How to Run
1. Open two terminal windows.
2. In the first, run the server:
```bash
python week_06/daythirtysix/echo_server.py
```
3. In the second, run the client:
```bash
python week_06/daythirtysix/echo_client.py
```

## Reflection
Sockets are the lowest level of network programming. Understanding how they work is crucial for building anything from web servers to real-time multiplayer games. The transition from a single-threaded echo server to a multi-threaded chat server highlights the importance of concurrency in networking.
