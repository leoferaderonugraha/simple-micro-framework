"""Builtin http handlers"""

from .context import AppContext
from .status_codes import (
    HTTP_STATUS_NOT_FOUND,
    HTTP_STATUS_INTERNAL_SERVER_ERROR,
)


async def page_404_handler(ctx: AppContext):
    data = {}
    data['message'] = 'Route Not Found.'

    return ctx \
        .set_status(HTTP_STATUS_NOT_FOUND) \
        .json(data)


async def page_505_handler(ctx: AppContext):
    data = {}
    data['message'] = 'Internal Server Error'
    data['error'] = ctx.get_stacktrace()

    return ctx \
        .set_status(HTTP_STATUS_INTERNAL_SERVER_ERROR) \
        .json(data)
