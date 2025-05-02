# ( module, resposnsible ffor handling communication between max/msp and python)
import argparse
from pythonosc import dispatcher, osc_server
from pythonosc import udp_client
import json
import threading

class OSCHandler:
    def __init__(self, recieve_ip="127.0.0.1", recieve_port=5005, send_ip="127.0.0.1", send_port=5006):
        #setting up the client for sendin messages
        self.client=udp_client.SimpleUDPClient(send_ip, send_port)

        #osc server for receiving messages
        self.dispatcher=dispatcher.Dispatcher()
        self.server=osc_server.ThreadingOSCUDPServer((recieve_ip, recieve_port), self.dispatcher)

    def adding_handler(self, address, handler):
        #for a specific address we will be addin up a handler here
        self.dispatcher.map(address, handler)
        print(f"handler succesfully added for address: {address}")

    def send_message(self, address, data):
        #yhn se jo cmd hogi, ye vo msp/max ko bhejega
        self.client.send_message(address, data)
        print(f"message sent to {address} with data: {data}")

    def start_server(self):
        #start the server in a new thread
        print("Starting OSC server...")
        server_thread=threading.Thread(target=self.server.serve_forever)
        server_thread.daemon=True
        server_thread.start()
        print(f"server succesfully started on {self.server.server_address}")
        return server_thread
    
    def stop_server(self):
        #stop the server
        print("Stopping OSC server...")
        self.server.shutdown()
        print("Server stopped.")
        
