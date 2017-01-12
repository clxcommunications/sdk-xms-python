# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import
# pylint: disable=invalid-name

from clx.xms import api
from nose.tools import *

def test_iteration_over_pages():
    results = [
        ["element0", "element1"],
        ["element2"],
        []
    ]

    def fetcher(pageno):
        pg = api.Page()
        pg.page = pageno
        pg.content = results[pageno]
        pg.size = len(results[pageno])
        pg.total_size = 3
        return pg

    pages = api.Pages(fetcher)

    for pageno, page in enumerate(pages):
        assert_is(results[pageno], page.content)

        for idx, value in enumerate(page):
            assert_is(results[pageno][idx], value)
