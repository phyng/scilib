# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import json
import pandas as pd
from optparse import OptionParser
from collections import Counter

A_TO_Z = [chr(i) for i in range(65, 65 + 26)]
A_TO_Z_RANGE = [(a, A_TO_Z[i + 1]) for i, a in enumerate(A_TO_Z[:-1])]


def make_nodes_edges(items):
    nodes = set()
    edges = []
    for item in items:
        for a, b in A_TO_Z_RANGE:
            if item.get(a) and item.get(b):
                nodes.add(item.get(a))
                nodes.add(item.get(b))
                edges.append((item.get(a), item.get(b)))
    nodes = list(nodes)
    return nodes, edges


def make_matrix_csv(nodes, edges):
    lines = []
    for nodea in nodes:
        line = [nodea]
        for nodeb in nodes:
            count = len([True for a, b in edges if a == nodea and b == nodeb])
            line.append(count)
        lines.append(','.join([str(i) for i in line]))
    return '\n'.join(lines)


def make_sankey_data(nodes, edges):
    data_nodes = [dict(name=node) for node in nodes]
    counter = Counter(edges)
    data_links = []
    for (a, b), count in counter.most_common():
        if a == b:
            continue
        data_links.append(dict(
            source=nodes.index(a),
            target=nodes.index(b),
            value=count,
        ))
    return dict(
        nodes=data_nodes,
        links=data_links,
    )


def make_arc_data(nodes, edges):
    data_nodes = []
    edges_unique = [edge for edge in edges if edge[0] != edge[1]]
    for index, node in enumerate(nodes):
        data_nodes.append(dict(
            id=index,
            name=node,
            value=len([True for edge in edges_unique if edge[1] == node]),
        ))
    data_links = []
    for a, b in edges_unique:
        data_links.append(dict(
            source=nodes.index(a),
            target=nodes.index(b),
        ))
    return dict(
        nodes=data_nodes,
        links=data_links,
    )


def make_blance_analytics(nodes, edges):
    edges_unique = [edge for edge in edges if edge[0] != edge[1]]
    values = []
    for node in nodes:
        in_value = len([True for a, b in edges_unique if b == node])
        out_value = len([True for a, b in edges_unique if a == node])
        value = in_value - out_value
        values.append(dict(
            name=node,
            in_value=in_value,
            out_value=out_value,
            value=value,
        ))
    return values


def from_excel(path):
    df = pd.read_excel(path, engine='openpyxl')
    return [dict({k: v for k, v in row.items() if str(v) != 'nan'}) for i, row in df.iterrows()]


def run(from_path, to_path, to_type):
    items = from_excel(from_path)
    nodes, edges = make_nodes_edges(items)
    if to_type == 'sankey_json':
        data = make_sankey_data(nodes, edges)
        with open(to_path, 'w') as f:
            json.dump(data, f, indent=2, sort_keys=True, ensure_ascii=False)
    elif to_type == 'arc_json':
        data = make_arc_data(nodes, edges)
        with open(to_path, 'w') as f:
            json.dump(data, f, indent=2, sort_keys=True, ensure_ascii=False)
    elif to_type == 'edges_xlsx':
        df = pd.DataFrame.from_records([dict(source=a, target=b) for a, b in edges if a != b])
        df.to_excel(to_path)
    elif to_type == 'blance_analytics':
        df = pd.DataFrame.from_records(make_blance_analytics(nodes, edges))
        df.to_excel(to_path)
    elif to_type == 'vosviewer':
        data = make_matrix_csv(nodes, edges)
        with open(to_path, 'w') as f:
            f.write(data)


def main():
    parser = OptionParser()
    parser.add_option("--from", action="store", type="str", dest="from_path")
    parser.add_option("--to", action="store", type="str", dest="to_path")
    parser.add_option("--to_type", action="store", type="str", dest="to_type", default="sankey_json")
    options, args = parser.parse_args()
    if not (options.from_path and options.to_path):
        parser.print_help()
        return
    run(options.from_path, options.to_path, options.to_type)


if __name__ == '__main__':
    main()
