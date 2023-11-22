#!/usr/bin/python3

import pytest

from enrich_company_data import enrich_companies_from_url, print_error


def test_enrich_companies_from_url__no_path():
    def mock_url_fetcher(url):
        return {'not_stored': 'a_value'}

    timestamp = '2023-11-22 15:21.29'
    companies_dict = {'Company-A': {}}
    enrich_companies_from_url(companies_dict, timestamp, fetcher=mock_url_fetcher)
    assert companies_dict['Company-A'] == {
        'details_from_url': 'No url for company Company-A',
        'url_fetched_at': timestamp
    }


def test_enrich_companies_from_url__with_path_but_no_details():
    def mock_url_fetcher(url):
        return {}

    timestamp = '2023-11-22 15:21.29'
    companies_dict = {'Company-A': {'path': '/company-a/'}}
    enrich_companies_from_url(companies_dict, timestamp, fetcher=mock_url_fetcher)
    print(companies_dict)
    assert companies_dict['Company-A'] == {
        'path': '/company-a/',
        'details_from_url': 'No details from for company Company-A with url https://eqtgroup.com/page-data/company-a/page-data.json',
        'url_fetched_at': timestamp
    }


def test_enrich_companies_from_url__with_path_and_details():
    def mock_url_fetcher(url):
        return {'website': 'https://campany-a.com', 'not_stored': 'a_value'}

    timestamp = '2023-11-22 15:21.29'
    companies_dict = {'Company-A': {'path': '/company-a/'}}
    enrich_companies_from_url(companies_dict, timestamp, fetcher=mock_url_fetcher)
    print(companies_dict)
    assert companies_dict['Company-A'] == {
        'path': '/company-a/',
        'details_from_url': {'website': 'https://campany-a.com'},
        'url_fetched_at': timestamp
    }
