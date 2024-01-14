# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division
from collections import Counter
import os
from pathlib import Path
import pandas as pd

from scilib.corrs.corrs_utils import (
    get_corrs,
    corrs_to_csv_string,
    corrs_to_cortext_network,
    cortext_network_to_csv_string,
    merge_year_cortext_networks,
)
from scilib.iterlib import uniqify

ORG_TABLE_PATH = Path(__file__).parent / 'config/org_table.xlsx'
ORG_MATCH_RULE_PATH = Path(__file__).parent / 'config/org_match_rule.xlsx'


def report_cnki_org(cnki_items, *, outpur_dir):
    df_org_table = pd.read_excel(ORG_TABLE_PATH)
    df_org_match_rule = pd.read_excel(ORG_MATCH_RULE_PATH)

    org_table_names = [i.strip() for i in df_org_table['机构'].to_list() if i.strip()]
    org_table_names = sorted(org_table_names, key=lambda x: (-len(x), x))
    org_match_rules = {row['规则'].strip(): row['目标'].strip() for i, row in df_org_match_rule.iterrows()}

    authors_list = [
        [i.strip() for i in token.split(';') if i and i.strip()]
        for token in [i.get('Author', '') for i in cnki_items if i]
        if token
    ]
    counter = Counter([i for li in authors_list for i in li])
    author_items = []
    for i, (k, v) in enumerate(counter.most_common()):
        author_items.append(dict(i=i + 1, name=k, count=v))

    orgs_list = [
        [i.strip() for i in token.split(';') if i.strip()]
        for token in [i.get('Organ', '') for i in cnki_items]
    ]
    counter = Counter([i for li in orgs_list for i in li])
    org_items = []
    for i, (k, v) in enumerate(counter.most_common()):
        org_items.append(dict(i=i + 1, name=k, count=v))

    org_map = {}
    for item in org_items:
        match_name = None
        match_type = None
        for n in org_table_names:
            if item['name'].startswith(n):
                match_name = n
                match_type = 'startswith'
                break

        for k, v in org_match_rules.items():
            if Path(item['name']).match(k):
                match_name = v
                match_type = 'rule'
                break

        if not match_name:
            for n in org_table_names:
                if n in item['name']:
                    match_name = n
                    match_type = 'contains'
                    break
        item['match_name'] = match_name
        item['match_type'] = match_type
        if match_name:
            org_map[item['name']] = match_name

    org_items_matched = [i for i in org_items if i['name'] in org_map]
    pd.DataFrame.from_records(org_items).to_csv(os.path.join(outpur_dir, "org.items.csv"), index=False)
    pd.DataFrame.from_records(org_items_matched).to_csv(
        os.path.join(outpur_dir, "org.items_matched.csv"), index=False
    )

    pd.DataFrame.from_records(author_items).to_csv(
        os.path.join(outpur_dir, "author.items.csv"), index=False
    )

    matched_orgs_list = []
    for orgs in orgs_list:
        matched_orgs = []
        for org in orgs:
            if org in org_map and org_map[org] not in matched_orgs:
                matched_orgs.append(org_map[org])
        matched_orgs_list.append(matched_orgs)
    _, corrs = get_corrs(matched_orgs_list)
    corrs_csv_string = corrs_to_csv_string(corrs)
    with open(os.path.join(outpur_dir, "org.corrs.csv"), "w") as f:
        f.write(corrs_csv_string)

    # pnetview txt format
    pnetview_text = '\n'.join(
        [','.join(uniqify([t.replace(',', '-') for t in orgs])) for orgs in matched_orgs_list if orgs]
    )
    with open(os.path.join(outpur_dir, "org.pnetview.txt"), "w") as f:
        f.write(pnetview_text)


def report_cnki_keywords(
    cnki_items,
    *,
    outpur_dir,
    top_size=50,
):
    counter, corrs = get_corrs([item["keyword_tokens"] for item in cnki_items], top_size=top_size)
    top_n = [token for token, _ in counter.most_common(top_size)]

    corrs_csv_string = corrs_to_csv_string(corrs)
    with open(os.path.join(outpur_dir, "keywords.corrs.csv"), "w") as f:
        f.write(corrs_csv_string)

    keywords_items = []
    for i, (k, v) in enumerate(counter.most_common()):
        keywords_items.append(dict(i=i + 1, name=k, count=v))
    pd.DataFrame.from_records(keywords_items).to_csv(
        os.path.join(outpur_dir, "keywords.items.csv"), index=False
    )

    # cortext network
    cortext_network = corrs_to_cortext_network(corrs)
    with open(os.path.join(outpur_dir, "keywords.cortext.csv"), "w") as f:
        f.write(cortext_network_to_csv_string(cortext_network))

    # keywords_year_extend
    top_keywords_year_extend = []

    # cortext network with year
    networks = {}
    for year in sorted(set([item["parsed_year"] for item in cnki_items if item["parsed_year"]])):
        year_items = [item for item in cnki_items if item["parsed_year"] == year]
        year_counter, year_corrs = get_corrs([item["keyword_tokens"] for item in year_items])
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
    pnetview_text = '\n'.join(
        [','.join(uniqify([t.replace(',', '-') for t in item["keyword_tokens"]])) for item in cnki_items]
    )
    with open(os.path.join(outpur_dir, "keywords.pnetview.txt"), "w") as f:
        f.write(pnetview_text)


def report_cnki_all(
    cnki_items,
    *,
    outpur_dir,
    keywords_top_size=50,
):
    pd.DataFrame.from_records(cnki_items).to_csv(os.path.join(outpur_dir, "items.csv"), index=False)
    report_cnki_keywords(
        cnki_items,
        outpur_dir=outpur_dir,
        top_size=keywords_top_size
    )
    report_cnki_org(cnki_items, outpur_dir=outpur_dir)
