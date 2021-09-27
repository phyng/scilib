# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import os
import time
import random
import json
import redis
import requests
import hashlib

ENV_STORAGE_ROOT = os.environ.get('ENV_STORAGE_ROOT') or '/tmp'
ENV_DOI_LIST_KEY = os.environ.get('ENV_DOI_LIST_KEY') or 'scilib-altmetric-doi-list'
ENV_DOI_ERROR_KEY = os.environ.get('ENV_DOI_ERROR_KEY') or 'scilib-altmetric-doi-error'
ALL_PROXY = os.environ.get('all_proxy') or 'socks5://127.0.0.1:5913'
ENV_REDIS_HOST = os.environ.get('ENV_REDIS_HOST') or '127.0.0.1'
ENV_REDIS_PORT = os.environ.get('ENV_REDIS_PORT') or '6379'


def get_random_ua():
    n = lambda: random.choice(range(10))
    return (
        f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_{n()}) AppleWebKit/537.36 (KHTML, like Gecko)'
        f'Chrome/{n()}{n()}.0.{n()}651.0 Safari/537.36'
    )


def request(doi):
    url = f'https://api.altmetric.com/v1/doi/{doi}'
    r = requests.get(
        url,
        headers={
            'User-Agent': get_random_ua()
        },
        proxies={
            'http': ALL_PROXY,
            'https': ALL_PROXY
        },
        timeout=10,
    )
    if r.status_code == 404:
        return None
    elif r.status_code == 200:
        return r.json()
    else:
        r.raise_for_status()


def get_storage_path(doi):
    hexdigest = hashlib.md5(doi.encode()).hexdigest()
    dir_path = os.path.join(ENV_STORAGE_ROOT, hexdigest[0], hexdigest[:2])
    path = os.path.join(dir_path, f'{hexdigest}.json')
    return dir_path, path


def run(doi):
    dir_path, path = get_storage_path(doi)
    if os.path.exists(path):
        return 'EXISTS'
    data = request(doi)
    os.makedirs(dir_path, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f)

    if data is None:
        return 'NONE'
    return data.get('details_url')


def dispatch():
    client = redis.StrictRedis(host=ENV_REDIS_HOST, port=ENV_REDIS_PORT)
    stop = False
    count = 0
    while not stop:
        doi = client.rpop(ENV_DOI_LIST_KEY)
        if not doi:
            stop = True
            print('stop')
            break
        doi = doi.decode('utf-8')
        count += 1
        try:
            print(f'{count} run: {doi}')
            result = run(doi)
            time.sleep(1)
        except Exception as e:
            print(f'{count} error: {doi} {e}')
            client.lpush(ENV_DOI_ERROR_KEY, doi)  # ->|...|->
        else:
            print(f'{count} success: {doi} {result}')


def main():
    dispatch()


if __name__ == '__main__':
    main()
