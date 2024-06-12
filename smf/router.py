import typing as t
from .context import AppContext
from .types import RouteHandler


PARAM_ID = ':'


class Route:
    """example of usage:
    ```python
    Route('/users/:id', User.profile_detail, methods=['GET', 'POST'])
    ```
    """

    def __init__(self,
                 path: str,
                 handler: RouteHandler,
                 methods=['GET']) -> None:
        self._path = path.strip('/')
        self._handler = handler
        self._methods = [method.upper() for method in methods]
        self._params = {}
        self._parts = self._path.split('/')

        self._parse_params()

    def match(self, path: str) -> t.Tuple[bool, t.Dict[str, str]]:
        parts = path.strip('/').split('/')
        named_param_idx = list(self._params.keys())
        param_values = {}

        for i in range(len(self._parts)):
            if i in named_param_idx:
                param_name = self._params[i]

                # strip param identifier before storing them
                param_values[param_name[1:]] = parts[i]
                continue

            if parts[i] != self._parts[i]:
                return (False, {})

        return (True, param_values)

    def is_allowed(self, method: str) -> bool:
        for supported_method in self._methods:
            if supported_method == method.upper():
                return True
                break

        return False

    def get_handler(self) -> RouteHandler:
        return self._handler

    def _parse_params(self):
        for i in range(len(self._parts)):
            if self._parts[i].startswith(PARAM_ID):
                self._params[i] = self._parts[i]
