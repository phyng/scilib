# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division
import os

from scilib.corrs.corrs_utils import (
    get_corrs,
    corrs_to_csv_string,
    corrs_to_cortext_network,
    cortext_network_to_csv_string,
    merge_year_cortext_networks,
)


def report_cnki_keywords(
    cnki_items,
    *,
    outpur_dir,
):
    corrs = get_corrs([item["keyword_tokens"] for item in cnki_items])
    corrs_csv_string = corrs_to_csv_string(corrs)
    with open(os.path.join(outpur_dir, "keywords.corrs.csv"), "w") as f:
        f.write(corrs_csv_string)

    # cortext network
    cortext_network = corrs_to_cortext_network(corrs)
    with open(os.path.join(outpur_dir, "keywords.cortext.csv"), "w") as f:
        f.write(cortext_network_to_csv_string(cortext_network))

    # cortext network with year
    networks = {}
    for year in sorted(set([item["parsed_year"] for item in cnki_items if item["parsed_year"]])):
        year_items = [item for item in cnki_items if item["parsed_year"] == year]
        year_corrs = get_corrs([item["keyword_tokens"] for item in year_items])
        networks[int(year)] = corrs_to_cortext_network(year_corrs)
    year_cortext_networks = merge_year_cortext_networks(networks)
    with open(os.path.join(outpur_dir, "keywords.cortext_with_year.csv"), "w") as f:
        f.write(cortext_network_to_csv_string(year_cortext_networks))

    # pnetview txt format
    pnetview_text = '\n'.join([','.join([t.replace(',', '-') for t in item["keyword_tokens"]]) for item in cnki_items])
    with open(os.path.join(outpur_dir, "keywords.pnetview.txt"), "w") as f:
        f.write(pnetview_text)


def report_cnki_all(
    cnki_items,
    *,
    outpur_dir,
):
    report_cnki_keywords(cnki_items, outpur_dir=outpur_dir)
