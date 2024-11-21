import socket
import threading

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []  # List of connected client sockets

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server is running on {self.host}:{self.port}...")

        # Start a thread to handle multicast messages from the server
        threading.Thread(target=self.server_multicast, daemon=True).start()

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"New connection from {client_address}")
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        try:
            while True:
                message = client_socket.recv(1024).decode()
                if not message:
                    break
                print(f"Received message: {message}")
                self.broadcast_message(message, client_socket)
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            self.clients.remove(client_socket)
            client_socket.close()
            print("Client disconnected.")

    def broadcast_message(self, message, sender_socket=None):
        for client in self.clients:
            if client != sender_socket:  # Don't send the message back to the sender (if applicable)
                try:
                    client.sendall(message.encode())
                except Exception as e:
                    print(f"Error sending message to client: {e}")

    def server_multicast(self):
        """Allows the server to manually send multicast messages to all clients."""
        while True:
            message = input("Enter a multicast message to send to all clients: ")
            self.broadcast_message(f"[Server]: {message}")

    def stop(self):
        if self.server_socket:
            self.server_socket.close()
        print("Server stopped.")

# Start the server
if __name__ == "__main__":
    server = Server("127.0.0.1", 8080)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()