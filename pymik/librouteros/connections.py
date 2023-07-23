# -*- coding: UTF-8 -*-
from socket import socket
from .exceptions import ConnectionClosed


class SocketTransport:

    def __init__(self, sock: socket):
        self.sock = sock

    def write(self, data: bytes) -> None:
        """
        Write given bytes to socket. Loop as long as every byte in
        string is written unless exception is raised.
        """
        self.sock.sendall(data)

    def read(self, length: int) -> bytes:
        """
        Read as many bytes from socket as specified in length.
        Loop as long as every byte is read unless exception is raised.
        """
        data = bytearray()
        while len(data) != length:
            data += self.sock.recv((length - len(data)))
            if not data:
                raise ConnectionClosed('Connection unexpectedly closed.')
        return data

    def close(self) -> None:
        self.sock.close()