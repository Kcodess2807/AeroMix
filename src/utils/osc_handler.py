import argparse
from pythonosc import dispatcher, osc_server
from pythonosc import udp_client
import json
import threading

class OSCHandler:
    def __init__(self, receive_ip="127.0.0.1", receive_port=5005,
                 send_ip="127.0.0.1", send_port=5006):
        print(f"OSCHandler: Initializing with receive_port={receive_port}, send_port={send_port}")
        self.client = udp_client.SimpleUDPClient(send_ip, send_port)
        self.dispatcher = dispatcher.Dispatcher()
        self.server = osc_server.ThreadingOSCUDPServer(
            (receive_ip, receive_port), self.dispatcher)
        self.server_thread = None

    def add_handler(self, address, handler):
        self.dispatcher.map(address, handler)
        print(f"handler succesfully added for address: {address}")

    def send_message(self, address, data):
        print(f"Sending message to address: {address}")
        print(f"Data: {data}")
        if isinstance(data, (int, float)):
            self.client.send_message(address, [data])
        else:
            self.client.send_message(address, data)

    def start_server(self):
        print("Starting OSC server...")
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        print(f"server succesfully started on {self.server.server_address}")
        return self.server_thread

    def stop_server(self):
        print("Stopping OSC server...")
        if self.server:
            self.server.shutdown()
            print("Server stopped.")
