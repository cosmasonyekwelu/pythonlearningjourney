"""
Day 36: Networking & Socket Programming
Main entry point for the networking examples
"""

import os
import threading
import time


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    """Print banner"""
    banner = """
    ==============================================
           DAY 36: NETWORKING BASICS
        Socket Programming Examples
    ==============================================
    """
    print(banner)


def run_echo_example():
    """Run the echo server and client example"""
    print("\nECHO SERVER EXAMPLE")
    print("=" * 40)

    def start_echo_server():
        import echo_server
        echo_server.start_echo_server()

    server_thread = threading.Thread(target=start_echo_server, daemon=True)
    server_thread.start()

    print("Starting Echo Server...")
    time.sleep(2)

    input("\nPress Enter to start echo client...")

    import echo_client
    echo_client.start_echo_client()


def run_chat_example():
    """Run the chat server example"""
    print("\nCHAT SERVER EXAMPLE")
    print("=" * 40)
    print("This will start a chat server that multiple clients can connect to.")
    print("You can test it by running multiple clients in different terminals.")

    choice = input("\nStart chat server? (y/n): ").lower().strip()
    if choice == 'y':
        import chat_server
        chat_server.main()


def run_single_chat_test():
    """Run a quick test with one server and one client"""
    print("\nQUICK CHAT TEST")
    print("=" * 40)

    def start_chat_server():
        import chat_server
        server = chat_server.ChatServer()
        server.start()

    server_thread = threading.Thread(target=start_chat_server, daemon=True)
    server_thread.start()

    print("Starting Chat Server...")
    time.sleep(3)

    print("\nStarting Chat Client...")
    time.sleep(1)

    import chat_client
    client = chat_client.ChatClient()
    client.start()


def show_readme():
    """Display the README content"""
    clear_screen()
    try:
        with open('README.md', 'r') as f:
            print(f.read())
    except FileNotFoundError:
        print("README.md not found.")


def main():
    """Main menu"""
    clear_screen()
    print_banner()

    while True:
        print("\nAVAILABLE EXAMPLES:")
        print("1. Echo Server & Client (Basic)")
        print("2. Multi-Client Chat Server")
        print("3. Quick Chat Test (Server + Client)")
        print("4. View README")
        print("5. Exit")

        choice = input("\nSelect an option (1-5): ").strip()

        if choice == '1':
            run_echo_example()
        elif choice == '2':
            run_chat_example()
        elif choice == '3':
            run_single_chat_test()
        elif choice == '4':
            show_readme()
        elif choice == '5':
            print("\nGoodbye.")
            break
        else:
            print("Invalid choice. Please try again.")

        input("\nPress Enter to continue...")
        clear_screen()
        print_banner()


if __name__ == "__main__":
    main()
