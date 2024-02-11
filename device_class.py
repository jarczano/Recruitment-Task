import socket
import threading
import time
import random
from utils import write_frame


class Device:
    # The class functions as a server capable of both receiving and sending messages to clients
    def __init__(self, name, port, id_can, receive=False):
        self.name = name  # Auxiliary attribute for the task
        self.receive = receive  # This attribute determines whether the device can send messages or only receive
        self.host = '127.0.0.1'
        self.port = port  # Port number to run the server
        self.id_can = id_can  # Id_can of device

    def receive_message(self, client_socket):
        # Function responsible for receiving messages from clients
        try:
            while True:
                data = client_socket.recv(1024)
                received_message = data.decode()
                print(f"Device {self.name} with id_can: {self.id_can} received message: {received_message}")
        except Exception as e:
            print(e)
        finally:
            client_socket.close()

    def send_data(self, client_socket):
        #  Function responsible for sending messages to clients
        try:
            while True:
                #  for the task we send a random number
                random_number = random.randint(1, 10)

                frame = write_frame(1, 0, self.id_can, [random_number])

                client_socket.send(str(frame).encode())
                print(f"Send frame to app: {frame}")
                time.sleep(1)  # Here it should normally be about 1/10

        except Exception as e:
            print(f"Error while sending: {e}")
        finally:
            client_socket.close()

    def start_server(self):
        # Function to run the server
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind a socket to a specific address and port
        server.bind((self.host, self.port))

        # Listening for connection
        server.listen(5)
        print(f"The server is listening on {self.host}:{self.port}")
        try:
            while True:

                # Accepting a connection from a client
                client_socket, addr = server.accept()
                print(f"A call was accepted from {addr}")

                # Customer service in a separate thread
                client_handler = threading.Thread(target=self.send_data, args=(client_socket,))
                client_handler.start()

                # If the device can also receive messages
                if self.receive:
                    receiver = threading.Thread(target=self.receive_message, args=(client_socket,))
                    receiver.start()
        except Exception as e:
            print(f"Error while accepting connection: {e}")

        server.close()

