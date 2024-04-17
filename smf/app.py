import inspect
from .signal_handlers import (
    page_404_handler,
    page_505_handler,
)
from .context import AppContext
from .status_codes import (
    HTTP_STATUS_NOT_FOUND,
    HTTP_STATUS_INTERNAL_SERVER_ERROR,
)
from .types import (
    Scope,
    Receive,
    Send,
    Route,
    RouteHandler,
)


class App:
    def __init__(self) -> None:
        self.__routes: dict[Route, RouteHandler] = {}
        self.__route_methods: dict[str, list[str]] = {}

        self.__signal_handlers: dict[int, RouteHandler] = {
            HTTP_STATUS_NOT_FOUND: page_404_handler,
            HTTP_STATUS_INTERNAL_SERVER_ERROR: page_505_handler,
        }

    async def __call__(self,
                       scope: Scope,
                       receive: Receive,
                       send: Send) -> None:
        assert scope['type'] == 'http'

        ctx = AppContext(scope, receive, send)

        print(scope)
        path = scope['path']

        handler = self.__routes.get(path, None)
        methods = self.__route_methods.get(path, ['GET'])

        is_method_match = False
        for method in methods:
            if method == scope['method']:
                is_method_match = True
                break

        if not is_method_match:
            await ctx.create_response(b'Method not allowed!')
            return None

        if handler is None:
            await self.__handle(
                self.__signal_handlers[HTTP_STATUS_NOT_FOUND],
                ctx
            )
            return None

        try:
            await self.__handle(handler, ctx)
        except Exception as e:
            print(e)
            await self.__handle(
                self.__signal_handlers[HTTP_STATUS_INTERNAL_SERVER_ERROR],
                ctx
            )

    def route(self, route: str, **kwargs: dict) -> RouteHandler:
        def decorate(func: RouteHandler) -> RouteHandler:
            self.__routes[route] = func
            print(route.split('/'))
            self.__route_methods[route] = kwargs.get('methods', [])
            return func
        return decorate

    def list_endpoints(self) -> dict:
        endpoints = {}

        for k, v in self.__routes.items():
            endpoints[k] = v.__name__

        return endpoints

    def set_signal_handler(self, signal: int, fn: RouteHandler):
        self.__signal_handlers[signal] = fn

    async def __handle(self, fn: RouteHandler, ctx: AppContext):
        result = await fn(ctx)
        # await another returned coroutine by the handler
        # possibly like this:
        #     return ctx.create_response(...)
        if inspect.iscoroutine(result):
            await result
