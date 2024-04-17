import asyncio
import uvicorn
import json
from .app import App, AppContext
from typing import Awaitable, Optional


app = App()


@app.route("/id/:user_id", methods=["GET"])
async def index(ctx: AppContext) -> Optional[Awaitable]:
    print(ctx.get_param('user_id'))

    # you could return the response
    return ctx.create_response(b'Hello world')


@app.route("/test", methods=["GET"])
async def test(ctx: AppContext) -> Optional[Awaitable]:
    data = {}
    data['message'] = 'hello world'
    headers = {b'content-type': b'application/json'}

    # invoke an error to test the default handler
    print(1/0)

    # or directly await the response
    await ctx \
        .set_headers(headers) \
        .set_status(200) \
        .create_response(json.dumps(data).encode('utf-8'))


async def main():
    config = uvicorn.Config('smf.main:app',
                            port=8899,
                            log_level='info',
                            reload=True)
    server = uvicorn.Server(config)
    print(app.list_endpoints())
    await server.serve()


if __name__ == '__main__':
    asyncio.run(main())
