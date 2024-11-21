import socket
import threading
import json

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None
        self.message_queue = []  # Stores messages received
        self.running = False

    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        self.running = True
        print(f"Connected to server at {self.host}:{self.port}")

        # Start a thread to listen for multicast messages
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def receive_messages(self):
        while self.running:
            try:
                data = self.client_socket.recv(1024).decode()
                if not data:
                    print("Disconnected from server.")
                    break

                message = json.loads(data)
                self.handle_message(message)
            except Exception as e:
                print(f"Error receiving message: {e}")
                break
        self.disconnect()

    def handle_message(self, message):
        self.message_queue.append(message)
        self.message_queue.sort(key=lambda x: x['timestamp'])  # Ensure messages are ordered
        print(f"Received message: {message['content']} with timestamp {message['timestamp']}")

    def send_message(self, content):
        message = {
            'content': content,
            'timestamp': 0  # Timestamp will be added by the leader
        }
        self.client_socket.sendall(json.dumps(message).encode())

    def disconnect(self):
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        print("Disconnected from server.")

# Client logic
if __name__ == "__main__":
    client = Client("127.0.0.1", 8080)
    try:
        client.connect()
        while True:
            message = input("Enter message (type 'exit' to disconnect): ")
            if message.lower() == "exit":
                client.disconnect()
                break
            client.send_message(message)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.disconnect()