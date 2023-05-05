# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division
from collections import Counter
import os
import pandas as pd

from scilib.corrs.corrs_utils import (
    get_corrs,
    corrs_to_csv_string,
    corrs_to_cortext_network,
    cortext_network_to_csv_string,
    merge_year_cortext_networks,
)
from scilib.wos.parse_common import parse_keyword_tokens


def report_wos_org(wos_items, *, outpur_dir):
    orgs_list = []
    for item in wos_items:
        orgs = []
        for info in (item['c1_address_info'] + item['rp_address_info']):
            if info['org'] not in orgs:
                orgs.append(info['org'])
        orgs_list.append(orgs)

    counter = Counter([i for li in orgs_list for i in li])
    org_items = []
    for i, (k, v) in enumerate(counter.most_common()):
        org_items.append(dict(i=i + 1, name=k, count=v))

    pd.DataFrame.from_records(org_items).to_csv(os.path.join(outpur_dir, "org.items.csv"), index=False)

    _, corrs = get_corrs(orgs_list)
    corrs_csv_string = corrs_to_csv_string(corrs)
    with open(os.path.join(outpur_dir, "org.corrs.csv"), "w") as f:
        f.write(corrs_csv_string)

    # pnetview txt format
    pnetview_text = '\n'.join([','.join([t.replace(',', '-') for t in orgs]) for orgs in orgs_list if orgs])
    with open(os.path.join(outpur_dir, "org.pnetview.txt"), "w") as f:
        f.write(pnetview_text)


def report_wos_keywords(
    wos_items,
    *,
    outpur_dir,
    keyword_field="DE",
    keyword_replace_map=None,
):
    keyword_tokens_list = [
        parse_keyword_tokens(item, keyword_field=keyword_field, replace_map=keyword_replace_map)
        for item in wos_items
    ]
    counter = Counter([token for tokens in keyword_tokens_list for token in tokens])
    counter_items = [dict(keyword=k, count=v) for k, v in counter.most_common()]
    pd.DataFrame(counter_items).to_csv(os.path.join(outpur_dir, "keywords.counter.csv"), index=False)

    # corrs
    _, corrs = get_corrs(keyword_tokens_list)
    corrs_csv_string = corrs_to_csv_string(corrs)
    with open(os.path.join(outpur_dir, "keywords.corrs.csv"), "w") as f:
        f.write(corrs_csv_string)

    # cortext network
    cortext_network = corrs_to_cortext_network(corrs)
    with open(os.path.join(outpur_dir, "keywords.cortext.csv"), "w") as f:
        f.write(cortext_network_to_csv_string(cortext_network))

    # cortext network with year
    networks = {}
    for year in sorted(set([item["PY"] for item in wos_items if item.get("PY") and str(item["PY"]) != "nan"])):
        year_items = [item for item in wos_items if item.get("PY") == year]
        _, year_corrs = get_corrs([
            parse_keyword_tokens(item, keyword_field=keyword_field, replace_map=keyword_replace_map)
            for item in year_items
        ])
        networks[int(year)] = corrs_to_cortext_network(year_corrs)
    year_cortext_networks = merge_year_cortext_networks(networks)
    with open(os.path.join(outpur_dir, "keywords.cortext_with_year.csv"), "w") as f:
        f.write(cortext_network_to_csv_string(year_cortext_networks))

    # pnetview txt format
    pnetview_text = '\n'.join([','.join([t.replace(',', '-') for t in tokens]) for tokens in keyword_tokens_list])
    with open(os.path.join(outpur_dir, "keywords.pnetview.txt"), "w") as f:
        f.write(pnetview_text)


def report_wos_all(
    wos_items,
    *,
    outpur_dir,
    keyword_field="DE",
    keyword_replace_map=None,
):
    report_wos_keywords(
        wos_items,
        outpur_dir=outpur_dir,
        keyword_field=keyword_field,
        keyword_replace_map=keyword_replace_map,
    )
    report_wos_org(wos_items, outpur_dir=outpur_dir)
