import psutil
import time
import threading
import socket

network_data = {'top_applications': [], 'top_receivers': []}

def get_network_usage():
    connections = psutil.net_connections(kind='inet')
    network_io = psutil.net_io_counters(pernic=True)
    
    usage_data = []
    for conn in connections:
        if conn.laddr and conn.raddr and conn.status == 'ESTABLISHED':
            try:
                remote_host = socket.gethostbyaddr(conn.raddr.ip)
                if remote_host[0]:
                    usage_data.append({
                        'laddr': conn.laddr.ip,
                        'raddr': remote_host[0],
                        'pid': conn.pid,
                        'status': conn.status,
                        'bytes_sent': network_io[conn.laddr.ip].bytes_sent if conn.laddr.ip in network_io else 0,
                        'bytes_recv': network_io[conn.laddr.ip].bytes_recv if conn.laddr.ip in network_io else 0,
                    })
            except (socket.herror, socket.timeout):
                pass

    top_applications = []
    top_receivers = []
    total_bytes_sent = sum(stats.bytes_sent for stats in network_io.values())
    total_bytes_recv = sum(stats.bytes_recv for stats in network_io.values())

    for usage in usage_data:
        app_data = {
            'name': usage['laddr'],
            'bytes': usage['bytes_sent'],
            'packets': usage['bytes_recv'],
            'percent': (usage['bytes_sent'] / total_bytes_sent) * 100 if total_bytes_sent > 0 else 0
        }
        recv_data = {
            'hostname': usage['raddr'],
            'bytes': usage['bytes_recv'],
            'packets': usage['bytes_sent'],
            'percent': (usage['bytes_recv'] / total_bytes_recv) * 100 if total_bytes_recv > 0 else 0
        }
        top_applications.append(app_data)
        top_receivers.append(recv_data)

    global network_data
    network_data = {'top_applications': top_applications, 'top_receivers': top_receivers}

def update_network_data():
    def run():
        while True:
            get_network_usage()
            time.sleep(5)
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
