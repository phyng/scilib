# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division
from collections import Counter
import json
import os
import pandas as pd

from scilib.corrs.corrs_utils import (
    corrs_to_pnetview_json,
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


def report_wos_wc(wos_items, *, outpur_dir):
    wcs_list = []
    for item in wos_items:
        wcs = [i.strip() for i in item.get('WC', '').split(';') if i.strip()]
        wcs_list.append(wcs)

    counter = Counter([i for li in wcs_list for i in li])
    wcs_items = []
    for i, (k, v) in enumerate(counter.most_common()):
        wcs_items.append(dict(i=i + 1, name=k, count=v))

    pd.DataFrame.from_records(wcs_items).to_csv(os.path.join(outpur_dir, "wcs.items.csv"), index=False)

    _, corrs = get_corrs(wcs_list)
    corrs_csv_string = corrs_to_csv_string(corrs)
    with open(os.path.join(outpur_dir, "wc.corrs.csv"), "w") as f:
        f.write(corrs_csv_string)

    # pnetview txt format
    pnetview_text = '\n'.join([','.join([t.replace(',', '-') for t in wcs]) for wcs in wcs_list if wcs])
    with open(os.path.join(outpur_dir, "wc.pnetview.txt"), "w") as f:
        f.write(pnetview_text)


def report_wos_keywords(
    wos_items,
    *,
    outpur_dir,
    keyword_field="DE",
    keyword_replace_map=None,
    top_size=50
):
    keyword_tokens_list = [
        parse_keyword_tokens(item, keyword_field=keyword_field, replace_map=keyword_replace_map)
        for item in wos_items
    ]
    counter = Counter([token for tokens in keyword_tokens_list for token in tokens])
    counter_items = [dict(keyword=k, count=v) for k, v in counter.most_common()]
    pd.DataFrame(counter_items).to_csv(os.path.join(outpur_dir, "keywords.counter.csv"), index=False)
    top_n = [token for token, _ in counter.most_common(top_size)]

    # corrs
    _, corrs = get_corrs(keyword_tokens_list, top_size=top_size)
    corrs_csv_string = corrs_to_csv_string(corrs)
    with open(os.path.join(outpur_dir, "keywords.corrs.csv"), "w") as f:
        f.write(corrs_csv_string)

    # cortext network
    cortext_network = corrs_to_cortext_network(corrs)
    with open(os.path.join(outpur_dir, "keywords.cortext.csv"), "w") as f:
        f.write(cortext_network_to_csv_string(cortext_network))

    # keywords_year_extend
    top_keywords_year_extend = []

    # cortext network with year
    networks = {}
    for year in sorted(set([item["PY"] for item in wos_items if item.get("PY") and str(item["PY"]) != "nan"])):
        year_items = [item for item in wos_items if item.get("PY") == year]
        year_counter, year_corrs = get_corrs([
            parse_keyword_tokens(item, keyword_field=keyword_field, replace_map=keyword_replace_map)
            for item in year_items
        ])
        networks[int(year)] = corrs_to_cortext_network(year_corrs)
        for k, v in year_counter.most_common():
            if k in top_n:
                top_keywords_year_extend.extend(dict(year=year, keyword=k) for i in range(v))

    year_cortext_networks = merge_year_cortext_networks(networks)
    with open(os.path.join(outpur_dir, "keywords.cortext_with_year.csv"), "w") as f:
        f.write(cortext_network_to_csv_string(year_cortext_networks))

    pd.DataFrame.from_records(top_keywords_year_extend).to_csv(
        os.path.join(outpur_dir, "keywords.top.year_extend.csv"), index=False
    )

    # pnetview txt format
    pnetview_text = '\n'.join([','.join([t.replace(',', '-') for t in tokens]) for tokens in keyword_tokens_list])
    with open(os.path.join(outpur_dir, "keywords.pnetview.txt"), "w") as f:
        f.write(pnetview_text)


def report_country(wos_items, *, outpur_dir, country_map):
    prefix = 'country.with_country_map' if country_map else 'country'
    for field in ['countrys_c1_rp', 'countrys_rp', 'first_country']:
        countrys_list = []
        year_countrys_list = {}
        total_count = 0
        for item in wos_items:
            if field == 'first_country':
                countrys = [item['first_country']] if item['first_country'] else []
            else:
                countrys = list(set(item[field]))

            # map and filter by country_map
            if country_map:
                countrys = [country_map.get(i, i) for i in countrys]
            countrys = [i for i in countrys if i]
            if not countrys:
                continue

            total_count += 1
            countrys_list.append(countrys)
            if item.get('PY'):
                year_countrys_list.setdefault(item['PY'], []).append(countrys)

        with open(os.path.join(outpur_dir, f'{prefix}.{field}.count.csv'), 'w') as f:
            f.write(str(total_count))

        for size in [50, 100]:
            _, corrs = get_corrs(countrys_list, top_size=size)
            csv = corrs_to_csv_string(corrs)
            with open(os.path.join(outpur_dir, f'{prefix}.{field}.corr.{size}.csv'), 'w') as f:
                f.write(csv)
            pnetview_json = corrs_to_pnetview_json(corrs)
            with open(os.path.join(outpur_dir, f'{prefix}.{field}.pnetview.{size}.json'), 'w') as f:
                json.dump(pnetview_json, f)


def report_wos_all(
    wos_items,
    *,
    outpur_dir,
    keyword_field="DE",
    keyword_replace_map=None,
    keywords_top_size=50,
    country_map=None
):
    pd.DataFrame.from_records(wos_items).to_csv(os.path.join(outpur_dir, "items.csv"), index=False)
    report_wos_keywords(
        wos_items,
        outpur_dir=outpur_dir,
        keyword_field=keyword_field,
        keyword_replace_map=keyword_replace_map,
        top_size=keywords_top_size
    )
    report_wos_org(wos_items, outpur_dir=outpur_dir)
    report_wos_wc(wos_items, outpur_dir=outpur_dir)
    report_country(wos_items, outpur_dir=outpur_dir, country_map=None)
    if country_map:
        report_country(wos_items, outpur_dir=outpur_dir, country_map=country_map)
