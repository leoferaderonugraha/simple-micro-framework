import typing as tp

if tp.TYPE_CHECKING:
    from .context import AppContext

T = tp.TypeVar('T')

Route = str
RouteHandler = tp.Callable[['AppContext'], tp.Optional[tp.Awaitable[None]]]

Scope = tp.Dict
Receive = tp.Callable
Send = tp.Callable
