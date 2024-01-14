# coding: utf-8

from __future__ import unicode_literals, absolute_import, print_function, division

from unittest import TestCase
from scilib.corrs.corrs_utils import get_corrs, get_corrs_slow, corrs_to_pnetview_json


class CorrsUtilsTest(TestCase):

    def test_get_corrs(self):
        tokens_list = [
            ["a", "b", "c"],
            ["a", "b", "d"],
            ["a", "c", "d"],
            ["b", "c", "d"],
            ["b", "c", "e"],
            ["c", "d", "e"],
            ["c", "e", "f"],
            ["d", "e", "f"],
            ["e", "f", "g"],
            ["f", "g", "h"],
        ]
        counter, corrs = get_corrs(tokens_list, top_size=3)
        self.assertDictEqual(dict(counter.most_common(3)), {'c': 6, 'd': 5, 'e': 5})
        self.assertListEqual(corrs, [
            ['c', 6, 3, 3],
            ['d', 3, 5, 2],
            ['e', 3, 2, 5]
        ])

    def test_get_corrs_slow(self):
        tokens_list = [
            ["a", "b", "c"],
            ["a", "b", "d"],
            ["a", "c", "d"],
            ["b", "c", "d"],
            ["b", "c", "e"],
            ["c", "d", "e"],
            ["c", "e", "f"],
            ["d", "e", "f"],
            ["e", "f", "g"],
            ["f", "g", "h"],
        ]
        counter, corrs = get_corrs_slow(tokens_list, top_size=3)
        self.assertDictEqual(dict(counter.most_common(3)), {'c': 6, 'd': 5, 'e': 5})
        self.assertListEqual(corrs, [
            ['c', 6, 3, 3],
            ['d', 3, 5, 2],
            ['e', 3, 2, 5]
        ])

    def test_corrs_to_pnetview_json(self):
        corrs = [
            ['c', 6, 3, 3],
            ['d', 3, 5, 2],
            ['e', 3, 2, 5]
        ]
        expected_result = {
            "nodes": [
                {
                    "id": "c",
                    "style": {
                        "keyshape": {
                            "size": 100 * 6 / 6
                        },
                        "label": {
                            "value": "c"
                        }
                    }
                },
                {
                    "id": "d",
                    "style": {
                        "keyshape": {
                            "size": 100 * 5 / 6
                        },
                        "label": {
                            "value": "d"
                        }
                    }
                },
                {
                    "id": "e",
                    "style": {
                        "keyshape": {
                            "size": 100 * 5 / 6
                        },
                        "label": {
                            "value": "e"
                        }
                    }
                }
            ],
            "edges": [
                {
                    "source": "c",
                    "target": "d",
                    "value": 3,
                    "style": {
                        "keyshape": {
                            "lineWidth": 20 * 3 / 6
                        }
                    }
                },
                {
                    "source": "c",
                    "target": "e",
                    "value": 3,
                    "style": {
                        "keyshape": {
                            "lineWidth": 20 * 3 / 6
                        }
                    }
                },
                {
                    "source": "d",
                    "target": "e",
                    "value": 2,
                    "style": {
                        "keyshape": {
                            "lineWidth": 20 * 2 / 6
                        }
                    }
                }
            ]
        }

        self.assertListEqual(corrs_to_pnetview_json(corrs)['nodes'], expected_result['nodes'])
        self.assertListEqual(corrs_to_pnetview_json(corrs)['edges'], expected_result['edges'])
