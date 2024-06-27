import pyshark
from flask_socketio import SocketIO, emit
import time
import asyncio

# Global variable to store packet data
packets_data = []
serial_number = 0

# Initialize SocketIO object (to be passed in from main app)
socketio = None

# Function to handle each packet captured
def packet_handler(packet):
    global serial_number
    serial_number += 1

    # Determine packet type and corresponding color
    color = 'black'
    try:
        if 'TCP' in packet:
            if 'SYN' in packet.tcp.flags or 'FIN' in packet.tcp.flags or 'ACK' in packet.tcp.flags:
                color = 'darkgray'
            else:
                color = 'lightpurple'
        elif 'UDP' in packet:
            color = 'lightblue'
        elif 'HTTP' in packet:
            color = 'lightgreen'
        elif 'SMB' in packet:
            color = 'lightyellow'
    except AttributeError:
        pass

    # Check if packet contains IP layer information
    source_ip = 'N/A'
    destination_ip = 'N/A'
    if 'IP' in packet:
        source_ip = packet.ip.src
        destination_ip = packet.ip.dst
    elif 'IPv6' in packet:
        source_ip = packet.ipv6.src
        destination_ip = packet.ipv6.dst

    # Create packet info dictionary
    packet_info = {
        "serial_number": serial_number,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(packet.sniff_timestamp))),
        "source": source_ip,
        "destination": destination_ip,
        "protocol": packet.transport_layer if hasattr(packet, 'transport_layer') else 'N/A',
        "length": packet.length,
        "info": packet.info if hasattr(packet, 'info') else packet.highest_layer,
        "color": color
    }

    packets_data.append(packet_info)
    # Emit packet info to WebSocket if socketio is initialized
    if socketio:
        try:
            socketio.emit('new_packet', packet_info)
        except Exception as e:
            print(f"Error emitting packet info: {e}")

# Function to start sniffing
def start_sniffing():
    # Create a new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    capture = pyshark.LiveCapture(interface='Wi-Fi')
    capture.apply_on_packets(packet_handler)
