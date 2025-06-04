# coding: utf-8

import os
import re
import pandas as pd

from libs.iterlib import uniqify
from scilib.iolib.file import write_file
from scilib.corrs.corrs_utils import (
    corrs_to_cortext_network, corrs_to_csv_string, cortext_network_to_csv_string, get_corrs, merge_year_cortext_networks
)


def parse_keyword_tokens(item, *, keyword_field, split_pattern=None, keyword_replace_map=None):
    keyword = item.get(keyword_field, '') or ''
    if str(keyword) == 'nan':
        return []
    tokens = re.split(split_pattern or r'[,;，]', keyword)
    tokens = [(keyword_replace_map or {}).get(i.strip(), i.strip()) for i in tokens if i and i.strip()]
    tokens = [i for i in tokens if i not in ['nan', 'None', 'null']]
    tokens = list(uniqify(tokens))
    return tokens


def report_keywords(
    *,
    items,
    keywords_field,
    year_field=None,
    output_dir='./',
    sizes=None,
    output_prefix='keywords'
):
    output_files = []
    sizes = [10, 20, 50, 100] if sizes is None else sizes
    for size in sizes:
        counter, corrs = get_corrs([item[keywords_field] or [] for item in items], top_size=size)
        top_n = [token for token, _ in counter.most_common(size)]

        # corr
        output_files.append(os.path.join(output_dir, f"{output_prefix}.{size}.corrs.csv"))
        write_file(output_files[-1], corrs_to_csv_string(corrs))

        # items
        keywords_items = [dict(i=i + 1, name=k, count=v) for i, (k, v) in enumerate(counter.most_common())]
        output_files.append(os.path.join(output_dir, f"{output_prefix}.{size}.items.csv"))
        pd.DataFrame.from_records(keywords_items).to_csv(output_files[-1], index=False)

        # cortext
        cortext_network = corrs_to_cortext_network(corrs)
        output_files.append(os.path.join(output_dir, f"{output_prefix}.{size}.cortext.csv"))
        write_file(output_files[-1], cortext_network_to_csv_string(cortext_network))

    # cortext network with year
    if year_field:
        top_keywords_year_extend = []
        networks = {}
        allow_years = [str(i) for i in range(1000, 3000)]
        years = sorted(set([str(item[year_field])[:4] for item in items if str(item[year_field])[:4] in allow_years]))
        for year in years:
            year_items = [item for item in items if str(item[year_field])[:4] == str(year)]
            year_counter, year_corrs = get_corrs([item[keywords_field] for item in year_items])
            networks[int(year)] = corrs_to_cortext_network(year_corrs)
            for k, v in year_counter.most_common():
                if k in top_n:
                    top_keywords_year_extend.extend(dict(year=year, keyword=k) for i in range(v))

        year_cortext_networks = merge_year_cortext_networks(networks)
        output_files.append(os.path.join(output_dir, f"{output_prefix}.cortext_with_year.csv"))
        write_file(output_files[-1], cortext_network_to_csv_string(year_cortext_networks))

        output_files.append(os.path.join(output_dir, f"{output_prefix}.top_n_year_extend.csv"))
        pd.DataFrame.from_records(top_keywords_year_extend).to_csv(output_files[-1], index=False)

    return output_files
