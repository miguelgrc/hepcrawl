# -*- coding: utf-8 -*-
#
# This file is part of hepcrawl.
# Copyright (C) 2017 CERN.
#
# hepcrawl is a free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Functional tests for PoS spider"""

from __future__ import absolute_import, division, print_function

import pytest

from time import sleep

from hepcrawl.testlib.celery_monitor import CeleryMonitor
from hepcrawl.testlib.fixtures import (
    get_test_suite_path,
    expected_json_results_from_file,
)
from hepcrawl.testlib.tasks import app as celery_app
from hepcrawl.testlib.utils import get_crawler_instance


def override_generated_fields(record):
    record['acquisition_source']['datetime'] = u'2017-04-03T10:26:40.365216'
    record['acquisition_source']['submission_number'] = u'5652c7f6190f11e79e8000224dabeaad'

    return record


@pytest.fixture(scope="function")
def set_up_oai_environment():
    package_location = get_test_suite_path(
        'pos',
        'fixtures',
        'oai_harvested',
        'pos_record.xml',
        test_suite='functional',
    )

    # The test must wait until the docker environment is up (takes about 10 seconds).
    sleep(10)

    yield {
        'CRAWLER_HOST_URL': 'http://scrapyd:6800',
        'CRAWLER_PROJECT': 'hepcrawl',
        'CRAWLER_ARGUMENTS': {
            'source_file': 'file://' + package_location,
            'base_conference_paper_url': 'https://server.local/contribution?id=',
        }
    }


@pytest.mark.parametrize(
    'expected_results',
    [
        expected_json_results_from_file(
            'pos',
            'fixtures',
            'pos_records.json',
        ),
    ],
    ids=[
        'conference_paper_record_only',
    ]
)
def test_pos_conference_paper_record(
        set_up_oai_environment,
        expected_results,
):
    crawler = get_crawler_instance(set_up_oai_environment.get('CRAWLER_HOST_URL'))

    results = CeleryMonitor.do_crawl(
        app=celery_app,
        monitor_timeout=5,
        monitor_iter_limit=100,
        events_limit=1,
        crawler_instance=crawler,
        project=set_up_oai_environment.get('CRAWLER_PROJECT'),
        spider='pos',
        settings={},
        **set_up_oai_environment.get('CRAWLER_ARGUMENTS')
    )

    gotten_results = [override_generated_fields(result) for result in results]
    expected_results = [override_generated_fields(expected) for expected in expected_results]

    assert sorted(gotten_results) == expected_results


# TODO create test that receives conference paper record AND proceedings record.


# TODO create test that receives proceedings record ONLY.
