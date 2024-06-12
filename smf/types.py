import typing as t

if t.TYPE_CHECKING:
    from .context import AppContext

T = t.TypeVar('T')

Route = str
RouteHandler = t.Callable[['AppContext'], t.Optional[t.Awaitable[None]]]

Scope = t.Dict
Receive = t.Callable
Send = t.Callable
