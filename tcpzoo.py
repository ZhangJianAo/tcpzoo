import asyncio
import os
import socket
import struct
import sys

# List of ports to listen on and server name and iptables command
port_config = {
    8000: ('Normal Server', None),
    8001: ('Drop SYN', 'iptables -A INPUT -p tcp --dport %d -j DROP'),
    8002: ('Drop ACK', 'iptables -A INPUT -p tcp --tcp-flags ACK ACK --dport %d -j DROP'),
    8003: ('Connection Refused icmp', 'iptables -A INPUT -p tcp --dport %d -j REJECT'),
    8004: ('Connection Refused', 'iptables -A INPUT -p tcp --dport %d -j REJECT --reject-with tcp-reset'),
    8005: ('Refused after ACK icmp', 'iptables -A INPUT -p tcp --tcp-flags ACK ACK --dport %d -j REJECT'),
    8006: ('Reset after ACK', 'iptables -A INPUT -p tcp --tcp-flags ACK ACK --dport %d -j REJECT --reject-with tcp-reset'),
    8007: ('Close after request', None),
    8008: ('Reset after request', None)
}


async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    _, server_port = writer.get_extra_info('sockname')

    print(f"Connected by {addr}")

    while True:
        data = await reader.read(1024)
        if not data:
            break

        print(f"Received {data!r} from {addr!r}")

        body = f'Hello, World! -- from {server_port}\n'.encode()
        response = f'HTTP/1.1 200 OK\nContent-Length: {len(body)}\n\n'.encode() + body
        writer.write(response)
        await writer.drain()

    print("Closing the connection")
    writer.close()


async def start_web_server(port, loop):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen()
    server_socket.setblocking(False)
    print(f"server start at 0.0.0.0:{port}")

    while True:
        client_socket, addr = await loop.sock_accept(server_socket)

        stream_reader = asyncio.StreamReader(loop=loop)
        protocol = asyncio.StreamReaderProtocol(stream_reader, loop=loop)

        transport, _ = await loop.create_connection(
            lambda: protocol, sock=client_socket)

        if port == 8007 or port == 8008:
            await stream_reader.read(1024)

            if port == 8008:
                l_onoff = 1
                l_linger = 0
                client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', l_onoff, l_linger))

            transport.close()
            continue

        stream_writer = asyncio.StreamWriter(transport, protocol, stream_reader, loop)
        loop.create_task(handle_client(stream_reader, stream_writer))


def start_servers():
    # Start a server for each port in a new task
    loop = asyncio.get_event_loop()
    for port in port_config.keys():
        loop.create_task(start_web_server(port, loop))
    loop.run_forever()


def request_servers():
    prefix = ''
    for port, (name, _) in port_config.items():
        print(f"{prefix}curl server {port}: {name}")
        os.system(f"curl --max-time 2 http://localhost:{port}")
        prefix = "\n"


def setup_iptables():
    for port, (_, iptables_cmd) in port_config.items():
        if iptables_cmd is None:
            continue
        cmd = iptables_cmd % port
        os.system(cmd)


def clean_iptables():
    for port, (_, iptables_cmd) in port_config.items():
        if iptables_cmd is None:
            continue
        cmd = iptables_cmd % port
        cmd = cmd.replace('-A', '-D')
        os.system(cmd)


if __name__ == "__main__":
    if sys.argv[1] == 'server':
        start_servers()
    elif sys.argv[1] == 'request':
        request_servers()
    elif sys.argv[1] == 'setup':
        setup_iptables()
    elif sys.argv[1] == 'clean':
        clean_iptables()
