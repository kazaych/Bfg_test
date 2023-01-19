from aiohttp import web


async def app():
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('stackoversearch/templates'))
    app.router.add_static('/static', path=str('stackoversearch/static'), name='static')

    app.router.add_route('*', '/', main)
    app.router.add_route('GET', '/show_all', show_all)
    return app