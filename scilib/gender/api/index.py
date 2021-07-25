
# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

from aiohttp import web
from scilib.gender.benchmark.benchmark import CONFIGS_MAP
import redis

KEY_PREFIX = 'scilib-gender'
POOL = redis.ConnectionPool()


async def gender(request):
    tool = request.query.get('tool', 'gender_guesser')
    names = request.query.get('name', None)
    if tool not in CONFIGS_MAP:
        return web.json_response(dict(status='error', message_type='invalid_tool'))
    if not names:
        return web.json_response(dict(status='error', message_type='invalid_name'))

    func = CONFIGS_MAP[tool][1]
    names = [i.strip() for i in names.split(';') if i.strip()]

    conn = redis.Redis(connection_pool=POOL)
    results = conn.hmget(f'{KEY_PREFIX}-{tool}', keys=names)
    results = [i.decode('utf-8') if i else None for i in results]

    results_items = [[i, r] for i, r in enumerate(results)]
    blank_items = [[i, r] for i, r in results_items if not r]
    if blank_items:
        call_results = func([names[i] for i, r in blank_items])
        for i, r in enumerate(call_results):
            results_items[blank_items[i][0]][1] = r

    results = [r for i, r in results_items]
    if not all(results):
        return web.json_response(dict(status='error', message_type='invalid_results', results_items=results_items))

    if blank_items:
        conn.hset(f'{KEY_PREFIX}-{tool}', mapping={names[i]: r for i, r in results_items})

    return web.json_response(dict(
        status='success',
        results=[dict(name=names[i], result=r) for i, r in results_items],
    ))


def main():
    app = web.Application()
    app.add_routes([
        web.get('/gender', gender)
    ])
    web.run_app(app, port=9901)


if __name__ == '__main__':
    main()
