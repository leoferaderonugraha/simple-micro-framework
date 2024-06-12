import inspect
import typing as t
from .signal_handlers import (
    page_404_handler,
    page_505_handler,
)
from .context import AppContext
from .status_codes import (
    HTTP_STATUS_NOT_FOUND,
    HTTP_STATUS_INTERNAL_SERVER_ERROR,
)
from .router import Route
from .types import (
    Scope,
    Receive,
    Send,
    RouteHandler,
)


class App:
    def __init__(self) -> None:
        self._routes: t.List[Route] = []

        self._signal_handlers: dict[int, RouteHandler] = {
            HTTP_STATUS_NOT_FOUND: page_404_handler,
            HTTP_STATUS_INTERNAL_SERVER_ERROR: page_505_handler,
        }

    async def __call__(self,
                       scope: Scope,
                       receive: Receive,
                       send: Send) -> None:
        assert scope['type'] == 'http'

        path = scope['path']
        method = scope['method']
        matched_route = None

        for route in self._routes:
            matched, params = route.match(path)
            if matched:
                matched_route = route
                scope['params'] = params
                break

        ctx = AppContext(scope, receive, send)

        if matched_route is None:
            await self._handle(
                self._signal_handlers[HTTP_STATUS_NOT_FOUND],
                ctx
            )
            return None

        if not matched_route.is_allowed(method):
            await ctx.create_response(b'Method not allowed!')
            return None

        try:
            await self._handle(route.get_handler(), ctx)
        except Exception as e:
            print('exception occured:', e)
            await self._handle(
                self._signal_handlers[HTTP_STATUS_INTERNAL_SERVER_ERROR],
                ctx
            )

    def route(self, path: str, **kwargs: dict) -> RouteHandler:
        # TODO:
        #   - handle same path different method(s), e.g:
        #     - Route('/:id' get_handler, methods=['GET'])
        #     - Route('/:id' put_handler, methods=['PUT'])
        def decorate(func: RouteHandler) -> RouteHandler:
            methods = kwargs.get('methods', ['GET'])
            new_route = Route(path, func, methods=methods)

            print(new_route)

            self._routes.append(new_route)
            return func
        return decorate

    # def list_endpoints(self) -> dict:
    #     endpoints = {}

    #     for k, v in self._routes.items():
    #         endpoints[k] = v.__name__

    #     return endpoints

    def set_signal_handler(self, signal: int, fn: RouteHandler):
        self._signal_handlers[signal] = fn

    async def _handle(self, fn: RouteHandler, ctx: AppContext):
        result = await fn(ctx)
        # await another returned coroutine by the handler
        # possibly like this:
        #     return ctx.create_response(...)
        if inspect.iscoroutine(result):
            await result
