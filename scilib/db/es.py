# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import os
import json
import requests

ES_API = os.environ.get('ES_API', 'http://localhost:9205')
ES_BULK_API = f'{ES_API}/_bulk'


def index_or_update_rows(rows, *, index="wos", action="index"):
    """ index_or_update_rows

    https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html
    """
    if not rows:
        return
    lines = []
    for row in rows:
        lines.append({
            action: {
                "_index": index,
                "_id": row["UT"],
            }
        })
        if action == "update":
            lines.append(dict(doc=row))
        elif action == "index":
            lines.append(row)
        else:
            raise ValueError(action)

    contents = [json.dumps(line) for line in lines]
    content = '\n'.join(contents) + '\n'
    response = requests.post(ES_BULK_API, data=content, headers={
        "Content-Type": "application/x-ndjson",
    })
    response_json = response.json()

    if 'errors' not in response_json:
        print(response_json)
        raise ValueError()
    elif response_json['errors']:
        print(response_json)
        raise ValueError()
    else:
        print('took', response_json['took'])
