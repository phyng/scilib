# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

import os
from unittest import TestCase

from scilib.wos.importer import read_text_format_dir_as_pd
from scilib.wos.parse_country import add_countrys_to_df
from scilib.wos.parse_categorys import SSH_CATEGORYS_SET, parse_ecoom_categorys
from scilib.wos.parse_doi import parse_cr_dois
from scilib.wos.parse_orcid import parse_orcid, parse_orcid_info
from scilib.wos.parse_rid import parse_rid
from scilib.wos.parse_address import parse_address, parse_address_info
from scilib.wos.parser import parse_version1

TEST_PATH = os.path.dirname(__file__)


class WOSParserTest(TestCase):

    def test_add_countrys_to_df(self):
        df = read_text_format_dir_as_pd(TEST_PATH)
        df['countrys_c1'] = add_countrys_to_df(df, field='C1', hmt=True)
        countrys = [row['countrys_c1'] for index, row in df.iterrows()]
        countrys_join = ';'.join(i for i in countrys if i)

        self.assertTrue('china' in countrys_join)
        self.assertTrue('usa' in countrys_join)
        self.assertTrue('hong kong' in countrys_join)

    def test_parse_ecoom_categorys(self):
        df = read_text_format_dir_as_pd(TEST_PATH)
        count = 0
        for index, row in df.iterrows():
            ecoom_categorys = parse_ecoom_categorys(row)
            if [c for c in SSH_CATEGORYS_SET if c in ecoom_categorys]:
                count += 1
        self.assertTrue(count, 356)  # checked

    def test_parse_cr_dois(self):
        df = read_text_format_dir_as_pd(TEST_PATH)
        dois = []
        for index, row in df.iterrows():
            cr_dois = parse_cr_dois(row)
            dois.extend([i for i in cr_dois.split(';') if i])
        self.assertTrue(len(dois), 29451)  # checked

    def test_parse_version1(self):
        df = read_text_format_dir_as_pd(TEST_PATH)
        items = [dict(row) for i, row in df.iterrows()]

        parse_version1(items)
        for item in items:
            self.assertEqual(item['is_article'], 'article' in str(item['DT']).lower())
            self.assertEqual('10.' in ';'.join(item['cr_dois']), '10.' in str(item['CR']))
            self.assertEqual('hong kong' in ';'.join(item['countrys_c1']), 'hong kong' in str(item['C1']).lower())

            # For debug:
            # print('-' * 80)
            # for key in item.keys():
            #     if len(key) > 2:
            #         print(key, item[key])

    def test_parse_address(self):
        df = read_text_format_dir_as_pd(TEST_PATH)
        items = [dict(row) for i, row in df.iterrows()]

        for item in items:
            parse_address(item['C1'])
            parse_address_info(item['C1'])

        text = """
[Liu, Jian] Nanjing Normal Univ, Sch Geog Sci, Minist Educ, Key Lab Virtual Geog Environm, Nanjing 210023, Jiangsu, Peoples R China.;
[Liu, Jian] Chinese Acad Sci, Nanjing Inst Geog & Limnol, State Key Lab Lake Sci & Environm, Nanjing 210008, Jiangsu, Peoples R China.;
[Wang, Bin; Yim, So-Young; Lee, June-Yi] Univ Hawaii Manoa, Int Pacific Res Ctr, Honolulu, HI 96825 USA.;
[Wang, Bin; Yim, So-Young; Lee, June-Yi] Univ Hawaii Manoa, Dept Meteorol, Honolulu, HI 96825 USA.;
[Cane, Mark A.] Columbia Univ, Lamont Doherty Earth Observ, Palisades, NY 10964 USA.
        """.strip().replace('\n', '') # noqa
        results = parse_address(text)

        self.assertEqual(results[0][0], 'Liu, Jian')
        self.assertEqual(results[4][0], 'Cane, Mark A.')

        infos = parse_address_info(text)
        self.assertEqual(infos[0]['org'], 'Nanjing Normal Univ')
        self.assertEqual(infos[4]['org'], 'Columbia Univ')
        self.assertEqual(infos[0]['country'], 'china')
        self.assertEqual(infos[4]['country'], 'usa')

    def test_parse_orcid(self):
        df = read_text_format_dir_as_pd(TEST_PATH)
        items = [dict(row) for i, row in df.iterrows()]

        for item in items:
            parse_orcid(item['OI'])
            parse_orcid_info(item['OI'])

        first_results = parse_orcid_info(items[0]['OI'])
        self.assertEqual(first_results[0]['name'], 'Casula, Manuela')
        self.assertEqual(first_results[0]['orcid'], '0000-0002-5124-5361')

    def test_parse_rid(self):
        text = """
Bechter, Karl/AAH-6637-2020; Tian, Li/P-2950-2015; Otto,; Markus/F-4304-2015; Benros, Michael Eriksen/N-5868-2016; Muller,; Sabine/P-4279-2015
        """.strip().replace('\n', '') # noqa
        results = parse_rid(text)
        self.assertEqual(results[0][0], 'Bechter, Karl')
        self.assertEqual(results[0][1], 'AAH-6637-2020')

        df = read_text_format_dir_as_pd(TEST_PATH)
        items = [dict(row) for i, row in df.iterrows()]

        for item in items:
            parse_rid(item['RI'])
