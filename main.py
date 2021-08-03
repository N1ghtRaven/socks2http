import asyncio
import logging
import os
import re
from asyncio import StreamReader, StreamWriter
from collections import namedtuple

from python_socks import ProxyType
from python_socks.async_.asyncio import Proxy

HttpHeader = namedtuple('HttpHeader', ['method', 'url', 'version', 'connect_to', 'is_connect'])
Socks5Credentials = namedtuple('Socks5Credentials', ['host', 'port', 'username', 'password'])


async def dial(client_conn, server_conn):
    async def io_copy(reader: StreamReader, writer: StreamWriter):
        while True:
            data = await reader.read(8192)
            if not data:
                break
            writer.write(data)
        writer.close()

    asyncio.ensure_future(io_copy(client_conn[0], server_conn[1]))
    asyncio.ensure_future(io_copy(server_conn[0], client_conn[1]))


async def open_socks5_connection(host: str, port: int, proxy):
    sock = await proxy.connect(host, port)
    return await asyncio.open_connection(sock=sock)


async def read_until_end_of_http_header(reader: StreamReader) -> bytes:
    lines = []
    while True:
        line = await reader.readline()
        lines.append(line)
        if line == b'\r\n':
            return b''.join(lines)


def parse_http_header(header: bytes) -> HttpHeader:
    lines = header.split(b'\r\n')
    fl = lines[0].decode()
    method, url, version = fl.split(' ', 2)

    if method.upper() == 'CONNECT':
        host, port = url.split(':', 1)
        port = int(port)
    else:
        # find Host header line
        host_text = None
        for header_line in lines:
            hl = header_line.decode()
            if re.match(r'^host:', hl, re.IGNORECASE):
                host_text = re.sub(r'^host:\s*', '', hl, count=1, flags=re.IGNORECASE)
                break

        if not host_text:
            raise ValueError("No http host line")

        if ':' not in host_text:
            host = host_text
            port = 80
        else:
            host, port = host_text.split(':', 1)
            port = int(port)

    is_connect = method.upper() == 'CONNECT'
    return HttpHeader(method=method, url=url, version=version, connect_to=(host, port), is_connect=is_connect)


async def handle_connection(reader: StreamReader, writer: StreamWriter):
    try:
        http_header_bytes = await read_until_end_of_http_header(reader)
        http_header = parse_http_header(http_header_bytes)
    except (IOError, ValueError) as e:
        logging.error(e)
        writer.close()
        return

    socks_cred = parse_socks_proxy()
    server_conn = await open_socks5_connection(
        host=http_header.connect_to[0],
        port=http_header.connect_to[1],
        proxy=Proxy.create(ProxyType.SOCKS5, socks_cred.host, socks_cred.port, socks_cred.username, socks_cred.password)
    )

    if http_header.is_connect:
        writer.write(b'HTTP/1.0 200 Connection Established\r\n\r\n')
    else:
        server_writer = server_conn[1]
        server_writer.write(http_header_bytes)

    asyncio.ensure_future(dial((reader, writer), server_conn))


def parse_socks_proxy() -> Socks5Credentials:
    try:
        return Socks5Credentials(
            host=os.environ['SOCKS_HOST'],
            port=int(os.environ['SOCKS_PORT']),
            username=os.environ['SOCKS_USERNAME'],
            password=os.environ['SOCKS_PASSWORD']
        )

    except KeyError as key:
        logging.error('Environment variable ' + key.args[0] + ' not found', )
        exit(1)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s]: %(name)s - %(message)s',
        level=logging.getLevelName(logging.INFO)
    )

    server = asyncio.start_server(handle_connection, host="0.0.0.0", port="8080")
    try:
        loop = asyncio.get_event_loop()
        server = loop.run_until_complete(server)
        loop.run_forever()
    except KeyboardInterrupt:
        server.close()
