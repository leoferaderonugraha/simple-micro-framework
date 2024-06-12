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
        self._scope = scope
        self._receive = receive
        self._send = send

        self._status_code = HTTP_STATUS_OK
        self._headers = {}
        self._stacktrace: Exception = None

    def set_status(self, status_code: int) -> 'AppContext':
        self._status_code = status_code
        return self

    def set_headers(self, headers: dict[bytes, bytes]) -> 'AppContext':
        self._headers = headers
        return self

    async def send(self,
                   message: str,
                   content_type: str = 'text/html') -> None:

        self._headers[b'content-type'] = content_type.encode('utf-8')

        headers = [[k, v] for k, v in self._headers.items()]

        await self._send({
            'type': 'http.response.start',
            'status': self._status_code,
            'headers': headers,
        })
        await self._send({
            'type': 'http.response.body',
            'body': message.encode('utf-8')
        })

    async def json(self, message: object) -> None:
        await self.send(json.dumps(message),
                        content_type='application/json')

    def get_param(self, name: str) -> t.Any:
        params = self._scope.get('params', {})

        return params.get(name, None)

    def _set_last_exception(self, err: Exception) -> None:
        self._stacktrace = err

    def get_last_exception(self) -> Exception:
        return self._stacktrace

    def get_stacktrace(self) -> str:
        exc_type, exc_value, exc_tb = sys.exc_info()

        tb = traceback.extract_tb(exc_tb)

        stacktrace = []
        stacktrace.append(f"{exc_type}: \"{exc_value}\"")
        for trace in tb:
            path, line, fn, code = trace
            stacktrace.append(
                f"File \"{path}\", line {line}, in {fn}: \"{code}\""
            )

        return stacktrace
