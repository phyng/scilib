# coding: utf-8

""" dataset transform
"""

from __future__ import unicode_literals, absolute_import, print_function, division

from optparse import OptionParser
from scilib.db.trans import pgcsv_to_items, pgcsv_to_es, ndjsongz_to_es


def run():
    parser = OptionParser()
    parser.add_option("--from", action="store", type="str", dest="from_path", default="")
    parser.add_option("--from-type", action="store", type="str", dest="from_type", default="")
    parser.add_option("--to", action="store", type="str", dest="to_path", default="")
    parser.add_option("--to-type", action="store", type="str", dest="to_type", default="")

    parser.add_option("--es-index", action="store", type="str", dest="es_index", default="")
    parser.add_option("--es-pk", action="store", type="str", dest="es_pk", default="")
    parser.add_option("--json-fields", action="store", type="str", dest="json_fields", default="")

    options, args = parser.parse_args()
    print('options', options)
    trans_type = f'{options.from_type}_to_{options.to_type}'
    json_fields = [i for i in options.json_fields.split(',') if i]
    trans_funcs = {
        'pgcsv_to_items': lambda options: pgcsv_to_items(options.from_path, json_fields),
        'pgcsv_to_es': lambda options: pgcsv_to_es(options.from_path, options.es_index, options.es_pk, json_fields),
        'ndjsongz_to_es': lambda options: ndjsongz_to_es(options.from_path, options.es_index, options.es_pk)
    }
    print('trans_type:', trans_type)
    if trans_type not in trans_funcs:
        print(f'type {trans_type} not support')
        return
    trans_func = trans_funcs[trans_type]
    trans_func(options)


if __name__ == '__main__':
    run()
