import socket
from threading import Thread
import os
class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.server_socket.bind((host, port))

    def start(self):
        self.server_socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}")
        while True:
            client_socket, address = self.server_socket.accept()
            print("New connection from", address)
            client_thread = Thread(target=self.handle_client, args=(client_socket, address))
            client_thread.start()

    def handle_client(self, client_socket, address):
        self.clients.append(client_socket)
        while True:
            try:
                header = client_socket.recv(1).decode('utf-8')
                if not header:
                    break

                if header == 'T':
                    message_length = int(client_socket.recv(4).decode('utf-8'))
                    message = client_socket.recv(message_length).decode('utf-8')
                    print(f"Received message from {address}: {message}")
                    self.broadcast(message, client_socket)
                elif header == 'F':
                    file_name_length = int(client_socket.recv(4).decode('utf-8'))
                    file_name = client_socket.recv(file_name_length).decode('utf-8')
                    file_size = int(client_socket.recv(10).decode('utf-8'))
                    name_group_size = int(client_socket.recv(4).decode('utf-8'))
                    name_group = client_socket.recv(name_group_size).decode('utf-8')
                    file_data = b""
                    while len(file_data) < file_size:
                        chunk = client_socket.recv(1024)
                        if not chunk:
                            break
                        file_data += chunk
                    self.save_file(file_name, file_data, client_socket,name_group)
                elif header == 'L':
                    message_length = int(client_socket.recv(4).decode('utf-8'))
                    message = client_socket.recv(message_length).decode('utf-8')
                    if "." not in message:
                        directory = os.path.join("received_files",message)
                        files_list = ""
                        if os.path.exists(directory):
                            files_list = os.listdir(directory)
                        delimiter = '\0'
                        files_str = delimiter.join(files_list)
                        print(files_str)
                        try:
                            message_length = len(files_str.encode('utf-8'))
                            header = f"L{message_length:04d}".encode('utf-8')
                            client_socket.sendall(header + files_str.encode('utf-8'))
                            print("Message sent successfully")
                        except Exception as e:
                            print("Error sending message to client:", e)

                    else:
                        file_name = message[:-5]
                        id = message[-5:]
                        file_path = os.path.join("received_files",id ,file_name)
                        try:
                            file_size = os.path.getsize(file_path)
                            file_name_bytes = file_name.encode('utf-8')
                            file_name_length = len(file_name_bytes)
                            group_name = f"[Server][Server][{id}]".encode("utf-8")
                            header = f"F{file_name_length:04d}".encode(
                                'utf-8') + file_name_bytes + f"{file_size:010d}".encode('utf-8') +f"{len(group_name):04d}".encode("utf-8")+group_name

                            with open(file_path, 'rb') as file:
                                file_data = file.read()
                            client_socket.sendall(header + file_data)

                            print("Success", "File sent successfully!")
                        except Exception as e:
                            print("Error", f"Failed to send file: {e}")


            except Exception as e:
                print(f"Error handling client {address}: {e}")
                break
        self.clients.remove(client_socket)
        client_socket.close()
        print("Connection closed by", address)

    def save_file(self, file_name, file_data, sender_socket,name_group):
        values = name_group.split("]")
        id = values[2].replace("[", "")
        directory = os.path.join("received_files", id)
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)

            file_path = os.path.join(directory,file_name)
            with open(file_path, "wb") as file:
                file.write(file_data)

            print(f"File '{file_name}' received and saved successfully!")

            # Broadcast the file to all connected clients
            self.broadcast_file(file_name, file_data, sender_socket,name_group)
        except Exception as e:
            print("Error saving or broadcasting file:", e)

    def broadcast_file(self, file_name, file_data, sender_socket,name_group):
        for client_socket in self.clients:
            if client_socket != sender_socket:
                try:
                    name_group_bytes = name_group.encode('utf-8')
                    file_name_encoded = file_name.encode('utf-8')
                    header = f"F{len(file_name_encoded):04d}".encode('utf-8') + file_name_encoded + f"{len(file_data):010d}".encode('utf-8') + f"{len(name_group_bytes):04d}".encode('utf-8') + name_group_bytes
                    client_socket.sendall(header + file_data)
                except Exception as e:
                    print("Error broadcasting file to client:", e)

    def broadcast(self, message, sender_socket):
        for client_socket in self.clients:
            if client_socket != sender_socket:
                try:
                    message_length = len(message.encode("utf-8"))
                    header = f"T{message_length:04d}".encode('utf-8')
                    client_socket.sendall(header + message.encode('utf-8'))
                except Exception as e:
                    print("Error sending message to client:", e)

if __name__ == "__main__":
    host = os.getenv("CHAT_HOST", "localhost")
    port = int(os.getenv("CHAT_PORT", 8080))
    server = ChatServer(host, port)
    server.start()
