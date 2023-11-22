#!/usr/bin/python3

import pytest

from enrich_company_data import print_error


def test_print_error():
    assert print_error('Not found') is None
    assert print_error('Not found') == 5

