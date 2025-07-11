import pickle
import queue
import socket
import socketserver
import threading
from collections.abc import Callable, Hashable, Iterable
from types import CodeType
from typing import Any

def unpickle_code(ms: bytes) -> CodeType: ...
def pickle_code(
    co: CodeType,
) -> tuple[Callable[[bytes], CodeType], tuple[bytes]]: ...
def dumps(obj: str, protocol: int | None = ...) -> str: ...

class CodePickler(pickle.Pickler):
    dispatch_table: dict[  # type: ignore[mutable-override]
        type,
        Callable[[type], tuple[Callable[[bytes], type], tuple[bytes]]],
    ]

BUFSIZE: int
LOCALHOST: str

class RPCServer(socketserver.TCPServer):
    def __init__(
        self,
        addr: tuple[str, int],
        handlerclass: socketserver.BaseRequestHandler | None = ...,
    ) -> None: ...
    def server_bind(self) -> None: ...
    def server_activate(self) -> None: ...
    def get_request(self) -> tuple[socket.socket, tuple[str, int]]: ...
    def handle_error(
        self,
        request: socket.socket | tuple[bytes, socket.socket],
        client_address: tuple[str, int] | str,
    ) -> None: ...

objecttable: dict[int, object]
request_queue: queue.Queue[
    tuple[str, tuple[str, tuple[object, list[Any], dict[str, Any]]]]
]
response_queue: queue.Queue[tuple[int, object]]

class SocketIO:
    nextseq: int
    sockthread: threading.Thread
    debugging: bool
    sock: socket.socket
    objtable: dict[int, object]
    responses: dict[int, Any]
    cvars: dict[int, threading.Condition]
    def __init__(
        self,
        sock: socket.socket,
        objtable: dict[int, object] | None = ...,
        debugging: bool | None = ...,
    ) -> None: ...
    def close(self) -> None: ...
    def exithook(self) -> None: ...
    def debug(self, *args: Iterable[object]) -> None: ...
    def register(self, oid: Hashable, object: object) -> None: ...
    def unregister(self, oid: Hashable) -> None: ...
    def localcall(
        self,
        seq: str,
        request: tuple[str, tuple[int, str, list[Any], dict[str, Any]]],
    ) -> tuple[str, str | dict[str, Any] | object, None, Exception]: ...
    def remotecall(
        self,
        oid: int,
        methodname: str,
        args: list[Any],
        kwargs: dict[str, Any],
    ) -> object | None: ...
    def remotequeue(
        self,
        oid: int,
        methodname: str,
        args: list[Any],
        kwargs: dict[str, Any],
    ) -> object | None: ...
    def asynccall(
        self,
        oid: int,
        methodname: str,
        args: list[Any],
        kwargs: dict[str, Any],
    ) -> int: ...
    def asyncqueue(
        self,
        oid: int,
        methodname: str,
        args: list[Any],
        kwargs: dict[str, Any],
    ) -> int: ...
    def asyncreturn(self, seq: int) -> Any | None: ...
    def decoderesponse(self, response: tuple[str, Any]) -> Any | None: ...
    def decode_interrupthook(self) -> None: ...
    def mainloop(self) -> None: ...
    def getresponse(
        self,
        myseq: int,
        wait: float,
    ) -> tuple[str, RPCProxy] | None: ...
    def newseq(self) -> int: ...
    def putmessage(self, message: tuple[int, tuple[str, object]]) -> None: ...
    buff: bytes
    bufneed: int
    bufstate: int
    def pollpacket(self, wait: float) -> bytes | None: ...
    def pollmessage(self, wait: float) -> tuple[int, Any] | None: ...
    def pollresponse(self, myseq: int, wait: float) -> Any: ...
    def handle_EOF(self) -> None: ...
    def EOFhook(self) -> None: ...

class RemoteObject: ...

def remoteref(obj: object) -> RemoteProxy: ...

class RemoteProxy:
    oid: int
    def __init__(self, oid: int) -> None: ...

class RPCHandler(socketserver.BaseRequestHandler, SocketIO):
    debugging: bool
    location: str
    def __init__(
        self,
        sock: socket.socket,
        addr: tuple[str, int] | str,
        svr: socketserver.BaseServer,
    ) -> None: ...
    def handle(self) -> None: ...
    def get_remote_proxy(self, oid: int) -> RPCProxy: ...

class RPCClient(SocketIO):
    debugging: bool
    location: str
    nextseq: int
    listening_sock: socket.socket
    def __init__(
        self,
        address: tuple[Any, ...] | str | bytes,
        family: socket.AddressFamily = ...,
        type: socket.SocketKind = ...,
    ) -> None: ...
    def accept(self) -> None: ...
    def get_remote_proxy(self, oid: int) -> RPCProxy: ...

class RPCProxy:
    sockio: SocketIO
    oid: int
    def __init__(self, sockio: SocketIO, oid: int) -> None: ...
    def __getattr__(self, name: str) -> Any: ...

class MethodProxy:
    sockio: SocketIO
    oid: int
    name: str
    def __init__(self, sockio: SocketIO, oid: int, name: str) -> None: ...
    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...

def displayhook(value: Any | None) -> None: ...
