import json
import typing as t
import traceback
import sys
from .status_codes import (
    HTTP_STATUS_OK,
)
from .types import (
    Scope,
    Receive,
    Send,
)


class AppContext:
    def __init__(self, scope: Scope, receive: Receive, send: Send) -> None:
        self.__scope = scope
        self.__receive = receive
        self.__send = send

        # default value so we can use `AppContext.send` immediately
        self.__status_code = HTTP_STATUS_OK
        self.__headers = {
            b'content-type': b'text/plain'
        }
        self.__stacktrace: Exception = None

    def set_status(self, status_code: int) -> 'AppContext':
        self.__status_code = status_code
        return self

    def set_headers(self, headers: dict[bytes, bytes]) -> 'AppContext':
        self.__headers = headers
        return self

    async def send(self,
                   message: str,
                   content_type: str = 'text/html') -> None:

        self.__headers[b'content-type'] = content_type.encode('utf-8')

        headers = [[k, v] for k, v in self.__headers.items()]

        await self.__send({
            'type': 'http.response.start',
            'status': self.__status_code,
            'headers': headers,
        })
        await self.__send({
            'type': 'http.response.body',
            'body': message.encode('utf-8')
        })

    async def json(self, message: object) -> None:
        await self.send(json.dumps(message),
                        content_type='application/json')

    def get_param(self, name: str) -> t.Any:
        params = self.__scope.get('params', {})

        return params.get(name, None)

    def _set_last_exception(self, err: Exception) -> None:
        self.__stacktrace = err

    def get_last_exception(self) -> Exception:
        return self.__stacktrace

    def get_stacktrace(self) -> str:
        exc_type, exc_value, exc_tb = sys.exc_info()

        tb = traceback.extract_tb(exc_tb)

        stacktrace = []
        for trace in tb:
            stacktrace.append(f"File: {trace[0]} | Line: {trace[1]} | Name: {trace[2]} | Message: {trace[3]}")

        return stacktrace
